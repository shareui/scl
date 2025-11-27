module SCL
  class ParseError < StandardError; end

  class SyntaxError < ParseError
    attr_reader :line, :column

    def initialize(message, line: nil, column: nil)
      @line = line
      @column = column
      full =
        if line && column
          "Syntax error at line #{line}, column #{column}: #{message}"
        else
          "Syntax error: #{message}"
        end
      super(full)
    end
  end
end


