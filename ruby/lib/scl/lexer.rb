require_relative "errors"

module SCL
  Token = Struct.new(:type, :value, :line, :column)

  module TokenType
    IDENTIFIER = :identifier
    DOUBLE_COLON = :double_colon
    BOOL = :bool
    STR = :str
    NUM = :num
    FL = :fl
    ML = :ml
    CLASS = :class
    LIST = :list
    DYNAMIC = :dynamic
    LBRACE = :lbrace
    RBRACE = :rbrace
    LPAREN = :lparen
    RPAREN = :rparen
    COMMA = :comma
    STRING = :string
    MULTILINE_STRING = :multiline_string
    NUMBER = :number
    FLOAT = :float
    BOOLEAN = :boolean
    COMMENT = :comment
    NEWLINE = :newline
    EOF = :eof
  end

  class Lexer
    def initialize(text)
      @text = text
      @pos = 0
      @line = 1
      @col = 1
      @tokens = []
    end

    def self.tokenize(text)
      new(text).tokenize
    end

    def tokenize
      while @pos < @text.length
        skip_whitespace
        break if peek.nil?

        case peek
        when "["
          @tokens << read_comment
        when "\n"
          add(TokenType::NEWLINE, "\n")
          advance
        when ":"
          if peek(1) == ":"
            add(TokenType::DOUBLE_COLON, "::")
            advance(2)
          else
            error("Unexpected ':'")
          end
        when "{", "}", "(", ")", ","
          map = { "{" => TokenType::LBRACE, "}" => TokenType::RBRACE, "(" => TokenType::LPAREN, ")" => TokenType::RPAREN, "," => TokenType::COMMA }
          add(map[peek], peek)
          advance
        when "\""
          @tokens << read_string
        when "'"
          @tokens << read_multiline_string
        when "-"
          if digit?(peek(1))
            @tokens << read_number
          else
            error("Expected digit after '-'")
          end
        else
          if digit?(peek)
            @tokens << read_number_or_identifier
          elsif alpha_or_underscore?(peek)
            @tokens << read_identifier
          else
            error("Unexpected character: #{peek}")
          end
        end
      end
      @tokens << Token.new(TokenType::EOF, nil, @line, @col)
      @tokens
    end

    private

    def add(type, value)
      @tokens << Token.new(type, value, @line, @col)
    end

    def peek(offset = 0)
      i = @pos + offset
      return nil if i >= @text.length
      @text[i]
    end

    def advance(n = 1)
      n.times do
        ch = @text[@pos]
        @pos += 1
        if ch == "\n"
          @line += 1
          @col = 1
        else
          @col += 1
        end
      end
    end

    def skip_whitespace
      while peek == " " || peek == "\t"
        advance
      end
    end

    def read_comment
      line, col = @line, @col
      advance # skip '['
      buf = +""
      while peek && peek != "]"
        buf << peek
        advance
      end
      error("Unclosed comment") unless peek == "]"
      advance # skip ']'
      Token.new(TokenType::COMMENT, buf.strip, line, col)
    end

    def read_string
      line, col = @line, @col
      advance # skip "
      buf = +""
      while peek && peek != "\""
        if peek == "\\"
          advance
          case peek
          when "n" then buf << "\n"
          when "t" then buf << "\t"
          when "\"", "\\" then buf << peek
          else buf << peek
          end
          advance
        else
          buf << peek
          advance
        end
      end
      error("Unclosed string") unless peek == "\""
      advance # skip "
      Token.new(TokenType::STRING, buf, line, col)
    end

    def read_multiline_string
      line, col = @line, @col
      advance # skip '
      buf = +""
      while peek && peek != "'"
        buf << peek
        advance
      end
      error("Unclosed multiline string") unless peek == "'"
      advance # skip '
      Token.new(TokenType::MULTILINE_STRING, buf, line, col)
    end

    def read_number
      line, col = @line, @col
      buf = +""
      if peek == "-"
        buf << peek
        advance
        error("Expected digit after '-'") unless digit?(peek)
      end
      has_dot = false
      while peek && (digit?(peek) || peek == ".")
        if peek == "."
          break if has_dot
          has_dot = true
        end
        buf << peek
        advance
      end
      if has_dot
        Token.new(TokenType::FLOAT, buf.to_f, line, col)
      else
        Token.new(TokenType::NUMBER, buf.to_i, line, col)
      end
    end

    def read_number_or_identifier
      # lookahead digits then alpha/_ -> identifier
      line, col = @line, @col
      p = @pos
      while p < @text.length && digit?(@text[p])
        p += 1
      end
      if p < @text.length && (alpha?(@text[p]) || @text[p] == "_")
        read_identifier
      else
        read_number
      end
    end

    def read_identifier
      line, col = @line, @col
      buf = +""
      while peek && (alpha?((c = peek)) || digit?(c) || c == "_" || c == "-")
        buf << c
        advance
      end
      keywords = {
        "bool" => TokenType::BOOL,
        "str" => TokenType::STR,
        "num" => TokenType::NUM,
        "fl" => TokenType::FL,
        "ml" => TokenType::ML,
        "class" => TokenType::CLASS,
        "list" => TokenType::LIST,
        "dynamic" => TokenType::DYNAMIC
      }
      booleans = {
        "true" => true, "false" => false, "yes" => true, "no" => false
      }
      if keywords.key?(buf)
        Token.new(keywords[buf], buf, line, col)
      elsif booleans.key?(buf)
        Token.new(TokenType::BOOLEAN, booleans[buf], line, col)
      else
        Token.new(TokenType::IDENTIFIER, buf, line, col)
      end
    end

    def digit?(c) = c && c >= "0" && c <= "9"
    def alpha?(c) = c && ((c >= "A" && c <= "Z") || (c >= "a" && c <= "z"))
    def alpha_or_underscore?(c) = alpha?(c) || c == "_"

    def error(msg)
      raise SyntaxError.new(msg, line: @line, column: @col)
    end
  end
end


