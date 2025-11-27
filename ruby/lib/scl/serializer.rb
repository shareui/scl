require_relative "errors"

module SCL
  class Serializer
    def initialize(indent: 4)
      @indent = indent
    end

    def serialize(hash)
      raise ParseError, "Expected Hash" unless hash.is_a?(Hash)
      (serialize_obj(hash, 0) + "\n")
    end

    private

    def serialize_obj(hash, level)
      indent = " " * (@indent * level)
      hash.map do |k, v|
        key = k.to_s
        indent + key + " :: " + serialize_value(v, level)
      end.join("\n")
    end

    def serialize_value(v, level)
      case v
      when TrueClass, FalseClass
        "bool { #{v ? "true" : "false"} }"
      when Integer
        "num { #{v} }"
      when Float
        "fl { #{v} }"
      when String
        if v.include?("\n")
          indent = " " * (@indent * level)
          "ml {\n#{indent}    '#{v}'\n#{indent}}"
        else
          escaped = v.gsub("\\", "\\\\").gsub("\"", "\\\"")
          "str { \"#{escaped}\" }"
        end
      when Hash
        "class {\n" + serialize_obj(v, level + 1) + "\n" + (" " * (@indent * level)) + "}"
      when Array
        serialize_list(v)
      else
        serialize_dynamic(v, level)
      end
    end

    def serialize_list(arr)
      return "list(str) { }" if arr.empty?
      first = arr.first
      if arr.all? { |x| x.is_a?(TrueClass) || x.is_a?(FalseClass) }
        items = arr.map { |x| x ? "true" : "false" }.join(", ")
        "list(bool) { #{items} }"
      elsif arr.all? { |x| x.is_a?(Integer) }
        items = arr.map(&:to_s).join(", ")
        "list(num) { #{items} }"
      elsif arr.all? { |x| x.is_a?(Float) || x.is_a?(Integer) }
        items = arr.map { |x| x.is_a?(Integer) ? x.to_s : x.to_s }.join(", ")
        "list(fl) { #{items} }"
      elsif arr.all? { |x| x.is_a?(String) }
        items = arr.map { |s| "\"#{s.gsub("\\", "\\\\").gsub("\"", "\\\"")}\"" }.join(", ")
        "list(str) { #{items} }"
      else
        raise ParseError, "Unsupported list element type: #{first.class}"
      end
    end

    def serialize_dynamic(v, level)
      case v
      when TrueClass, FalseClass
        "dynamic { #{v ? "true" : "false"} }"
      when Integer
        "dynamic { #{v} }"
      when Float
        "dynamic { #{v} }"
      when String
        if v.include?("\n")
          indent = " " * (@indent * level)
          "ml {\n#{indent}    '#{v}'\n#{indent}}"
        else
          escaped = v.gsub("\\", "\\\\").gsub("\"", "\\\"")
          "dynamic { \"#{escaped}\" }"
        end
      else
        raise ParseError, "Unsupported value type: #{v.class}"
      end
    end
  end
end


