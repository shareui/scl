defmodule SCL.Parser.Tokens do
  @moduledoc false

  @type token_type ::
          :identifier
          | :double_colon
          | :bool
          | :str
          | :num
          | :fl
          | :ml
          | :class
          | :list
          | :dynamic
          | :lbrace
          | :rbrace
          | :lparen
          | :rparen
          | :comma
          | :string
          | :multiline_string
          | :number
          | :float
          | :boolean
          | :comment
          | :newline
          | :eof

  @type t :: %{type: token_type(), value: any(), line: non_neg_integer(), column: non_neg_integer()}
end


