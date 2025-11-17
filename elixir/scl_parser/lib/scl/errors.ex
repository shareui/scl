defmodule SCL.Errors do
  defmodule ParseError do
    defexception [:message]
  end

  defmodule SyntaxError do
    defexception [:message, :line, :column]

    def exception(opts) do
      msg = Keyword.fetch!(opts, :message)
      line = Keyword.get(opts, :line)
      col = Keyword.get(opts, :column)

      full =
        if line && col do
          "Syntax error at line #{line}, column #{col}: #{msg}"
        else
          "Syntax error: #{msg}"
        end

      %__MODULE__{message: full, line: line, column: col}
    end
  end
end


