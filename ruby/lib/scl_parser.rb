# frozen_string_literal: true

require_relative "scl/errors"
require_relative "scl/lexer"
require_relative "scl/parser"
require_relative "scl/serializer"

module SCL
  VERSION = "0.1.0"
  AUTHOR = "shareui"

  module_function

  def loads(text)
    tokens = Lexer.tokenize(text)
    Parser.parse(tokens)
  end

  def load(path, encoding: "UTF-8")
    loads(File.read(path, mode: "r:bom|utf-8", encoding: encoding))
  end

  def dumps(hash, indent: 4)
    Serializer.new(indent: indent).serialize(hash)
  end

  def dump(hash, path, indent: 4, encoding: "UTF-8")
    File.write(path, dumps(hash, indent: indent), mode: "w:utf-8", encoding: encoding)
  end
end


