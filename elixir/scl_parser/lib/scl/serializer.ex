defmodule SCL.Serializer do
  @moduledoc false

  alias SCL.Errors.ParseError

  @indent 4

  def serialize(map) when is_map(map) do
    do_serialize(map, 0) <> "\n"
  end

  defp do_serialize(map, level) do
    indent = String.duplicate(" ", @indent * level)
    map
    |> Enum.map(fn {k, v} ->
      key = to_string(k)
      indent <> key <> " :: " <> serialize_value(v, level)
    end)
    |> Enum.join("\n")
  end

  # bool
  defp serialize_value(v, _level) when is_boolean(v) do
    "bool { " <> (if v, do: "true", else: "false") <> " }"
  end

  # int
  defp serialize_value(v, _level) when is_integer(v) do
    "num { " <> Integer.to_string(v) <> " }"
  end

  # float
  defp serialize_value(v, _level) when is_float(v) do
    "fl { " <> :erlang.float_to_binary(v, [:compact]) <> " }"
  end

  # string
  defp serialize_value(v, level) when is_binary(v) do
    if String.contains?(v, "\n") do
      indent = String.duplicate(" ", @indent * level)
      "ml {\n" <> indent <> "    '" <> v <> "'\n" <> indent <> "}"
    else
      escaped =
        v
        |> String.replace("\\", "\\\\")
        |> String.replace("\"", "\\\"")
      "str { \"" <> escaped <> "\" }"
    end
  end

  # map
  defp serialize_value(v, level) when is_map(v) do
    "class {\n" <> do_serialize(v, level + 1) <> "\n" <> String.duplicate(" ", @indent * level) <> "}"
  end

  # list
  defp serialize_value(v, _level) when is_list(v) do
    case v do
      [] -> "list(str) { }"
      _ ->
        first = hd(v)
        cond do
          is_boolean(first) and Enum.all?(v, &is_boolean/1) ->
            "list(bool) { " <> Enum.map_join(v, ", ", fn x -> if x, do: "true", else: "false" end) <> " }"
          is_integer(first) and Enum.all?(v, &is_integer/1) ->
            "list(num) { " <> Enum.map_join(v, ", ", &Integer.to_string/1) <> " }"
          (is_float(first) or is_integer(first)) and Enum.all?(v, &(is_float(&1) or is_integer(&1))) ->
            floats = Enum.map(v, fn x -> if is_integer(x), do: Integer.to_string(x), else: :erlang.float_to_binary(x, [:compact]) end)
            "list(fl) { " <> Enum.join(floats, ", ") <> " }"
          is_binary(first) and Enum.all?(v, &is_binary/1) ->
            escaped = Enum.map(v, fn s -> s |> String.replace("\\", "\\\\") |> String.replace("\"", "\\\"") end)
            "list(str) { " <> Enum.map_join(escaped, ", ", fn s -> "\"" <> s <> "\"" end) <> " }"
          true ->
            raise ParseError, message: "Unsupported list element: #{inspect(first)}"
        end
    end
  end

  # fallback
  defp serialize_value(v, _level) do
    cond do
      is_boolean(v) -> serialize_value(v, 0)
      is_integer(v) -> "dynamic { " <> Integer.to_string(v) <> " }"
      is_float(v) -> "dynamic { " <> :erlang.float_to_binary(v, [:compact]) <> " }"
      is_binary(v) ->
        escaped = v |> String.replace("\\", "\\\\") |> String.replace("\"", "\\\"")
        "dynamic { \"" <> escaped <> "\" }"
      true ->
        raise ParseError, message: "Unsupported type: #{inspect(v)}"
    end
  end
end