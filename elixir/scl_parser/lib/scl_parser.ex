defmodule SCL do
  @moduledoc """
  SCL parser for Elixir.

  API matches Python version:
    - load/1, loads/1
    - dump/2, dumps/1
  """

  alias SCL.Parser.Lexer
  alias SCL.Parser.Core
  alias SCL.Serializer

  @doc "Parse string"
  @spec loads(String.t()) :: map()
  def loads(text) when is_binary(text) do
    tokens = Lexer.tokenize(text)
    Core.parse(tokens)
  end

  @doc "Parse file"
  @spec load(Path.t()) :: map()
  def load(path) when is_binary(path) do
    path |> File.read!() |> loads()
  end

  @doc "Map → string"
  @spec dumps(map()) :: String.t()
  def dumps(data) when is_map(data) do
    Serializer.serialize(data)
  end

  @doc "Map → file"
  @spec dump(map(), Path.t()) :: :ok
  def dump(data, path) when is_map(data) and is_binary(path) do
    path |> File.write!(dumps(data))
    :ok
  end
end