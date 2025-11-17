defmodule SCL.Parser.Core do
  @moduledoc false
  alias SCL.Errors.SyntaxError

  def parse(tokens) when is_list(tokens) do
    tokens = Enum.reject(tokens, &(&1.type in [:newline, :comment]))
    {cfg, pos} = parse_config(tokens, 0, %{})
    expect(tokens, pos, :eof)
    cfg
  end

  defp parse_config(tokens, pos, acc) do
    case at(tokens, pos) do
      %{type: :eof} -> {acc, pos}
      _ ->
        {name, value, pos2} = parse_parameter(tokens, pos)
        parse_config(tokens, pos2, Map.put(acc, name, value))
    end
  end

  defp parse_parameter(tokens, pos) do
    name_tok = at(tokens, pos)
    {name, pos1} =
      case name_tok.type do
        :identifier -> {name_tok.value, pos + 1}
        t when t in [:bool, :str, :num, :fl, :ml, :class, :list, :dynamic] -> {name_tok.value, pos + 1}
        :number -> {Integer.to_string(name_tok.value), pos + 1}
        :string -> {name_tok.value, pos + 1}
        _ -> raise SyntaxError, message: "Expected identifier or keyword, got #{inspect(name_tok.type)}", line: name_tok.line, column: name_tok.column
      end
    pos2 = eat!(tokens, pos1, :double_colon)
    type_tok = at(tokens, pos2)
    case type_tok.type do
      :bool -> {val, p} = parse_bool_value(tokens, pos2 + 1); {name, val, p}
      :str -> {val, p} = parse_str_value(tokens, pos2 + 1); {name, val, p}
      :num -> {val, p} = parse_num_value(tokens, pos2 + 1); {name, val, p}
      :fl -> {val, p} = parse_fl_value(tokens, pos2 + 1); {name, val, p}
      :ml -> {val, p} = parse_ml_value(tokens, pos2 + 1); {name, val, p}
      :class -> {val, p} = parse_class_value(tokens, pos2 + 1); {name, val, p}
      :list -> {val, p} = parse_list_value(tokens, pos2 + 1); {name, val, p}
      :dynamic -> {val, p} = parse_dynamic_value(tokens, pos2 + 1); {name, val, p}
      _ -> raise SyntaxError, message: "Unknown type: #{inspect(type_tok.value)}", line: type_tok.line, column: type_tok.column
    end
  end

  defp parse_bool_value(tokens, pos) do
    pos1 = eat!(tokens, pos, :lbrace)
    tok = at(tokens, pos1)
    if tok.type != :boolean, do: raise(SyntaxError, message: "Expected boolean", line: tok.line, column: tok.column)
    pos2 = pos1 + 1
    pos3 = eat!(tokens, pos2, :rbrace)
    {tok.value, pos3}
  end

  defp parse_str_value(tokens, pos) do
    pos1 = eat!(tokens, pos, :lbrace)
    tok = at(tokens, pos1)
    if tok.type != :string, do: raise(SyntaxError, message: "Expected string", line: tok.line, column: tok.column)
    pos2 = pos1 + 1
    pos3 = eat!(tokens, pos2, :rbrace)
    {tok.value, pos3}
  end

  defp parse_num_value(tokens, pos) do
    pos1 = eat!(tokens, pos, :lbrace)
    tok = at(tokens, pos1)
    if tok.type != :number, do: raise(SyntaxError, message: "Expected number", line: tok.line, column: tok.column)
    pos2 = pos1 + 1
    pos3 = eat!(tokens, pos2, :rbrace)
    {tok.value, pos3}
  end

  defp parse_fl_value(tokens, pos) do
    pos1 = eat!(tokens, pos, :lbrace)
    tok = at(tokens, pos1)
    val =
      case tok.type do
        :float -> tok.value
        :number -> tok.value * 1.0
        _ -> raise SyntaxError, message: "Expected float or number", line: tok.line, column: tok.column
      end
    pos2 = pos1 + 1
    pos3 = eat!(tokens, pos2, :rbrace)
    {val, pos3}
  end

  defp parse_ml_value(tokens, pos) do
    pos1 = eat!(tokens, pos, :lbrace)
    tok = at(tokens, pos1)
    if tok.type != :multiline_string, do: raise(SyntaxError, message: "Expected multiline string", line: tok.line, column: tok.column)
    pos2 = pos1 + 1
    pos3 = eat!(tokens, pos2, :rbrace)
    {tok.value, pos3}
  end

  defp parse_class_value(tokens, pos) do
    pos1 = eat!(tokens, pos, :lbrace)
    {obj, pos2} = parse_object_body(tokens, pos1, %{})
    pos3 = eat!(tokens, pos2, :rbrace)
    {obj, pos3}
  end

  defp parse_object_body(tokens, pos, acc) do
    case at(tokens, pos).type do
      :rbrace -> {acc, pos}
      _ ->
        {name, value, pos2} = parse_parameter(tokens, pos)
        parse_object_body(tokens, pos2, Map.put(acc, name, value))
    end
  end

  defp parse_list_value(tokens, pos) do
    pos1 = eat!(tokens, pos, :lparen)
    elem_type = at(tokens, pos1)
    {parser_fun, pos2} =
      case elem_type.type do
        :num -> {fn tokens, p -> tok = expect_type(tokens, p, :number); {tok.value, p + 1} end, pos1 + 1}
        :fl -> {&parse_float_element/2, pos1 + 1}
        :bool -> {fn tokens, p -> tok = expect_type(tokens, p, :boolean); {tok.value, p + 1} end, pos1 + 1}
        :str -> {fn tokens, p -> tok = expect_type(tokens, p, :string); {tok.value, p + 1} end, pos1 + 1}
        _ -> raise SyntaxError, message: "Unsupported list element type: #{inspect(elem_type.value)}", line: elem_type.line, column: elem_type.column
      end
    pos3 = eat!(tokens, pos2, :rparen)
    pos4 = eat!(tokens, pos3, :lbrace)
    {elements, pos5} = parse_list_elements(tokens, pos4, parser_fun, [])
    pos6 = eat!(tokens, pos5, :rbrace)
    {elements, pos6}
  end

  defp parse_list_elements(tokens, pos, fun, acc) do
    case at(tokens, pos).type do
      :rbrace -> {Enum.reverse(acc), pos}
      _ ->
        {val, pos1} = fun.(tokens, pos)
        case at(tokens, pos1).type do
          :comma -> parse_list_elements(tokens, pos1 + 1, fun, [val | acc])
          :rbrace -> {Enum.reverse([val | acc]), pos1}
          other -> raise SyntaxError, message: "Expected comma or closing brace, got #{inspect(other)}", line: at(tokens, pos1).line, column: at(tokens, pos1).column
        end
    end
  end

  defp parse_float_element(tokens, pos) do
    tok = at(tokens, pos)
    cond do
      tok.type == :float -> {tok.value, pos + 1}
      tok.type == :number -> {tok.value * 1.0, pos + 1}
      true -> raise SyntaxError, message: "Expected float or number", line: tok.line, column: tok.column
    end
  end

  defp parse_dynamic_value(tokens, pos) do
    pos1 = eat!(tokens, pos, :lbrace)
    tok = at(tokens, pos1)
    val =
      case tok.type do
        t when t in [:number, :float, :boolean, :string, :multiline_string] -> tok.value
        _ -> raise SyntaxError, message: "dynamic supports only base types (bool, str, num, fl, ml)", line: tok.line, column: tok.column
      end
    pos2 = pos1 + 1
    pos3 = eat!(tokens, pos2, :rbrace)
    {val, pos3}
  end

  defp expect(tokens, pos, type) do
    tok = at(tokens, pos)
    if tok.type != type, do: raise(SyntaxError, message: "Expected #{inspect(type)}, got #{inspect(tok.type)}", line: tok.line, column: tok.column)
    pos + 1
  end

  defp expect_type(tokens, pos, type) do
    tok = at(tokens, pos)
    if tok.type != type, do: raise(SyntaxError, message: "Expected #{inspect(type)}, got #{inspect(tok.type)}", line: tok.line, column: tok.column)
    tok
  end

  defp eat!(tokens, pos, type), do: expect(tokens, pos, type)

  defp at(tokens, pos), do: Enum.at(tokens, pos) || List.last(tokens)
end


