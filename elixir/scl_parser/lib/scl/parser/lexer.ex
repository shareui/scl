defmodule SCL.Parser.Lexer do
  @moduledoc false
  alias SCL.Errors.SyntaxError

  def tokenize(text) when is_binary(text) do
    do_tokenize(%{text: text, pos: 0, line: 1, col: 1, tokens: []})
    |> Enum.reverse()
  end

  defp do_tokenize(%{text: text, pos: pos, line: line, col: col, tokens: acc}) do
    cond do
      pos >= byte_size(text) ->
        [%{type: :eof, value: nil, line: line, column: col} | acc]

      true ->
        <<_::binary-size(pos), ch::binary-size(1), _::binary>> = text
        case ch do
          " " -> do_tokenize(advance(text, pos, line, col, acc))
          "\t" -> do_tokenize(advance(text, pos, line, col, acc))
          "\n" ->
            nxt = advance(text, pos, line, col, [%{type: :newline, value: "\n", line: line, column: col} | acc])
            do_tokenize(nxt)
          "[" ->
            {tok, st} = read_comment(text, pos, line, col)
            do_tokenize(%{st | tokens: [tok | acc]})
          ":" ->
            if peek(text, pos + 1) == ":" do
              do_tokenize(%{text: text, pos: pos + 2, line: line, col: col + 2, tokens: [%{type: :double_colon, value: "::", line: line, column: col} | acc]})
            else
              raise SyntaxError, message: "Unexpected ':'", line: line, column: col
            end
          "{" -> do_tokenize(%{text: text, pos: pos + 1, line: line, col: col + 1, tokens: [%{type: :lbrace, value: "{", line: line, column: col} | acc]})
          "}" -> do_tokenize(%{text: text, pos: pos + 1, line: line, col: col + 1, tokens: [%{type: :rbrace, value: "}", line: line, column: col} | acc]})
          "(" -> do_tokenize(%{text: text, pos: pos + 1, line: line, col: col + 1, tokens: [%{type: :lparen, value: "(", line: line, column: col} | acc]})
          ")" -> do_tokenize(%{text: text, pos: pos + 1, line: line, col: col + 1, tokens: [%{type: :rparen, value: ")", line: line, column: col} | acc]})
          "," -> do_tokenize(%{text: text, pos: pos + 1, line: line, col: col + 1, tokens: [%{type: :comma, value: ",", line: line, column: col} | acc]})
          "\"" ->
            {tok, st} = read_string(text, pos, line, col)
            do_tokenize(%{st | tokens: [tok | acc]})
          "'" ->
            {tok, st} = read_multiline_string(text, pos, line, col)
            do_tokenize(%{st | tokens: [tok | acc]})
          "-" ->
            case peek(text, pos + 1) do
              d when d in ?0..?9 -> 
                {tok, st} = read_number(text, pos, line, col)
                do_tokenize(%{st | tokens: [tok | acc]})
              _ -> raise SyntaxError, message: "Expected digit after '-'", line: line, column: col
            end
          _ ->
            cond do
              digit?(ch) ->
                {tok, st} = read_number_or_identifier(text, pos, line, col)
                do_tokenize(%{st | tokens: [tok | acc]})
              alpha_or_underscore?(ch) ->
                {tok, st} = read_identifier(text, pos, line, col)
                do_tokenize(%{st | tokens: [tok | acc]})
              true ->
                raise SyntaxError, message: "Unexpected character: #{ch}", line: line, column: col
            end
        end
    end
  end

  defp read_comment(text, pos, line, col) do
    {_, pos1, line1, col1} = advance_vals(text, pos, line, col)
    {content, pos2, line2, col2} = take_until(text, pos1, line1, col1, "]")
    if peek(text, pos2) != "]", do: raise(SyntaxError, message: "Unclosed comment", line: line2, column: col2)
    { %{type: :comment, value: String.trim(content), line: line, column: col}, %{text: text, pos: pos2 + 1, line: line2, col: col2 + 1} }
  end

  defp read_string(text, pos, line, col) do
    {_, pos1, line1, col1} = advance_vals(text, pos, line, col)
    {buf, pos2, line2, col2} = take_string(text, pos1, line1, col1)
    { %{type: :string, value: buf, line: line, column: col}, %{text: text, pos: pos2 + 1, line: line2, col: col2 + 1} }
  end

  defp read_multiline_string(text, pos, line, col) do
    {_, pos1, line1, col1} = advance_vals(text, pos, line, col)
    {buf, pos2, line2, col2} = take_until(text, pos1, line1, col1, "'")
    if peek(text, pos2) != "'", do: raise(SyntaxError, message: "Unclosed multiline string", line: line2, column: col2)
    { %{type: :multiline_string, value: buf, line: line, column: col}, %{text: text, pos: pos2 + 1, line: line2, col: col2 + 1} }
  end

  defp read_number(text, pos, line, col) do
    {num, pos2, _, _} = take_while(text, pos, fn _ch, _p -> true end, line, col, &number_pred/2)
    {type, val} =
      if String.contains?(num, ".") do
        {:float, String.to_float(num)}
      else
        {:number, String.to_integer(num)}
      end
    { %{type: type, value: val, line: line, column: col}, %{text: text, pos: pos2, line: line, col: col + (pos2 - pos)} }
  end

  defp read_number_or_identifier(text, pos, line, col) do
    # Peek ahead: if digits followed by letters/underscore -> identifier
    {digits, p1, _, _} = take_while(text, pos, fn ch, _ -> digit?(ch) end, line, col, &default_step/2)
    case peek(text, p1) do
      x when is_binary(x) and alpha_or_underscore?(x) ->
        read_identifier(text, pos, line, col)
      _ ->
        read_number(text, pos, line, col)
    end
  end

  defp read_identifier(text, pos, line, col) do
    {ident, p2, _, _} = take_while(text, pos, fn ch, _ -> alpha_num_or_dash_underscore?(ch) end, line, col, &default_step/2)
    {type, value} =
      case ident do
        "bool" -> {:bool, ident}
        "str" -> {:str, ident}
        "num" -> {:num, ident}
        "fl" -> {:fl, ident}
        "ml" -> {:ml, ident}
        "class" -> {:class, ident}
        "list" -> {:list, ident}
        "dynamic" -> {:dynamic, ident}
        "true" -> {:boolean, true}
        "false" -> {:boolean, false}
        "yes" -> {:boolean, true}
        "no" -> {:boolean, false}
        _ -> {:identifier, ident}
      end
    { %{type: type, value: value, line: line, column: col}, %{text: text, pos: p2, line: line, col: col + (p2 - pos)} }
  end

  defp number_pred(ch, idx_from_start) do
    cond do
      idx_from_start == 0 and ch == "-" -> true
      ch == "." -> true
      digit?(ch) -> true
      true -> false
    end
  end

  defp take_string(text, pos, line, col, acc \\ "", esc \\ false) do
    case peek(text, pos) do
      nil -> raise SyntaxError, message: "Unclosed string", line: line, column: col
      "\"" when not esc -> {acc, pos, line, col}
      "\\" when not esc -> take_string(text, pos + 1, line, col + 1, acc, true)
      <<c::utf8>> when esc ->
        repl =
          case <<c::utf8>> do
            "n" -> "\n"
            "t" -> "\t"
            "\"" -> "\""
            "\\" -> "\\"
            other -> other
          end
        take_string(text, pos + 1, line, col + 1, acc <> repl, false)
      <<c::utf8>> ->
        {line2, col2} = if <<c::utf8>> == "\n", do: {line + 1, 1}, else: {line, col + 1}
        take_string(text, pos + 1, line2, col2, acc <> <<c::utf8>>, false)
    end
  end

  defp take_until(text, pos, line, col, stop_char, acc \\ "") do
    case peek(text, pos) do
      nil -> {acc, pos, line, col}
      ^stop_char -> {acc, pos, line, col}
      <<c::utf8>> ->
        {line2, col2} = if <<c::utf8>> == "\n", do: {line + 1, 1}, else: {line, col + 1}
        take_until(text, pos + 1, line2, col2, stop_char, acc <> <<c::utf8>>)
    end
  end

  defp take_while(text, pos, pred, line, col, step_fun, acc \\ "", idx \\ 0) do
    case peek(text, pos) do
      nil -> {acc, pos, line, col}
      <<c::utf8>> ->
        if pred.(<<c::utf8>>, idx) do
          {pos2, line2, col2} = step_fun.(pos, <<c::utf8>>)
          take_while(text, pos2, pred, line2, col2, step_fun, acc <> <<c::utf8>>, idx + 1)
        else
          {acc, pos, line, col}
        end
    end
  end

  defp default_step(pos, ch) do
    {pos + byte_size(ch), 0, 0}
  end

  defp advance(text, pos, line, col, tokens) do
    <<_::binary-size(pos), ch::binary-size(1), _::binary>> = text
    {line2, col2} = if ch == "\n", do: {line + 1, 1}, else: {line, col + 1}
    %{text: text, pos: pos + 1, line: line2, col: col2, tokens: tokens}
  end

  defp advance_vals(text, pos, line, col) do
    <<_::binary-size(pos), ch::binary-size(1), _::binary>> = text
    {ch, pos + 1, (if ch == "\n", do: line + 1, else: line), (if ch == "\n", do: 1, else: col + 1)}
  end

  defp peek(text, pos) when pos < 0 or pos >= byte_size(text), do: nil
  defp peek(text, pos) do
    <<_::binary-size(pos), ch::binary-size(1), _::binary>> = text
    ch
  end

  defp digit?(ch), do: ch >= "0" and ch <= "9"
  defp alpha?(ch), do: ch >= "A" and ch <= "Z" or ch >= "a" and ch <= "z"
  defp alpha_or_underscore?(ch), do: alpha?(ch) or ch == "_"
  defp alpha_num_or_dash_underscore?(ch), do: alpha?(ch) or digit?(ch) or ch in ["_", "-"]
end


