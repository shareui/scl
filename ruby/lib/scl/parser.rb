require_relative "errors"
require_relative "lexer"

module SCL
  class Parser
    class << self
      def parse(tokens)
        tokens = tokens.reject { |t| t.type == TokenType::NEWLINE || t.type == TokenType::COMMENT }
        parser = new(tokens)
        cfg = parser.parse_config
        parser.expect(TokenType::EOF)
        cfg
      end
    end

    def initialize(tokens)
      @tokens = tokens
      @pos = 0
    end

    def parse_config(acc = {})
      return acc if current.type == TokenType::EOF
      name, value = parse_parameter
      parse_config(acc.merge(name => value))
    end

    def parse_parameter
      name_tok = current
      name =
        case name_tok.type
        when TokenType::IDENTIFIER then eat(TokenType::IDENTIFIER).value
        when TokenType::BOOL, TokenType::STR, TokenType::NUM, TokenType::FL, TokenType::ML, TokenType::CLASS, TokenType::LIST, TokenType::DYNAMIC
          @pos += 1
          name_tok.value
        when TokenType::NUMBER then eat(TokenType::NUMBER).value.to_s
        when TokenType::STRING then eat(TokenType::STRING).value
        else error("Expected identifier or keyword, got #{name_tok.type}")
        end
      eat(TokenType::DOUBLE_COLON)
      case current.type
      when TokenType::BOOL then @pos += 1; [name, parse_bool_value]
      when TokenType::STR then @pos += 1; [name, parse_str_value]
      when TokenType::NUM then @pos += 1; [name, parse_num_value]
      when TokenType::FL then @pos += 1; [name, parse_fl_value]
      when TokenType::ML then @pos += 1; [name, parse_ml_value]
      when TokenType::CLASS then @pos += 1; [name, parse_class_value]
      when TokenType::LIST then @pos += 1; [name, parse_list_value]
      when TokenType::DYNAMIC then @pos += 1; [name, parse_dynamic_value]
      else error("Unknown type: #{current.value || current.type}")
      end
    end

    def parse_bool_value
      eat(TokenType::LBRACE)
      v = eat(TokenType::BOOLEAN).value
      eat(TokenType::RBRACE)
      v
    end

    def parse_str_value
      eat(TokenType::LBRACE)
      v = eat(TokenType::STRING).value
      eat(TokenType::RBRACE)
      v
    end

    def parse_num_value
      eat(TokenType::LBRACE)
      v = eat(TokenType::NUMBER).value
      eat(TokenType::RBRACE)
      v
    end

    def parse_fl_value
      eat(TokenType::LBRACE)
      tok = current
      v =
        case tok.type
        when TokenType::FLOAT then eat(TokenType::FLOAT).value
        when TokenType::NUMBER then eat(TokenType::NUMBER).value.to_f
        else error("Expected float or number")
        end
      eat(TokenType::RBRACE)
      v
    end

    def parse_ml_value
      eat(TokenType::LBRACE)
      v = eat(TokenType::MULTILINE_STRING).value
      eat(TokenType::RBRACE)
      v
    end

    def parse_class_value
      eat(TokenType::LBRACE)
      obj = {}
      until current.type == TokenType::RBRACE
        name, value = parse_parameter
        obj[name] = value
      end
      eat(TokenType::RBRACE)
      obj
    end

    def parse_list_value
      eat(TokenType::LPAREN)
      elem_type = current
      parser =
        case elem_type.type
        when TokenType::NUM then @pos += 1; -> { eat(TokenType::NUMBER).value }
        when TokenType::FL then @pos += 1; -> {
          if current.type == TokenType::FLOAT
            eat(TokenType::FLOAT).value.to_f
          else
            eat(TokenType::NUMBER).value.to_f
          end
        }
        when TokenType::BOOL then @pos += 1; -> { eat(TokenType::BOOLEAN).value }
        when TokenType::STR then @pos += 1; -> { eat(TokenType::STRING).value }
        else error("Unsupported list element type: #{elem_type.value}")
        end
      eat(TokenType::RPAREN)
      eat(TokenType::LBRACE)
      arr = []
      until current.type == TokenType::RBRACE
        arr << parser.call
        if current.type == TokenType::COMMA
          eat(TokenType::COMMA)
        elsif current.type != TokenType::RBRACE
          error("Expected comma or closing brace")
        end
      end
      eat(TokenType::RBRACE)
      arr
    end

    def parse_dynamic_value
      eat(TokenType::LBRACE)
      tok = current
      v =
        case tok.type
        when TokenType::NUMBER then eat(TokenType::NUMBER).value
        when TokenType::FLOAT then eat(TokenType::FLOAT).value
        when TokenType::BOOLEAN then eat(TokenType::BOOLEAN).value
        when TokenType::STRING then eat(TokenType::STRING).value
        when TokenType::MULTILINE_STRING then eat(TokenType::MULTILINE_STRING).value
        else error("dynamic supports only base types (bool, str, num, fl, ml)")
        end
      eat(TokenType::RBRACE)
      v
    end

    def current
      @tokens[@pos] || @tokens[-1]
    end

    def eat(type)
      tok = current
      if tok.type != type
        error("Expected #{type}, got #{tok.type}")
      end
      @pos += 1
      tok
    end

    def expect(type)
      eat(type)
    end

    def error(msg)
      tok = current
      raise SyntaxError.new(msg, line: tok.line, column: tok.column)
    end
  end
end


