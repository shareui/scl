defmodule SCLParserTest do
  use ExUnit.Case, async: true

  alias SCL.Errors.SyntaxError

  describe "loads/1" do
    test "parses a simple configuration" do
      text = """
      foo :: num { 42 }
      flag :: bool { true }
      """

      assert SCL.loads(text) == %{"foo" => 42, "flag" => true}
    end

    test "raises syntax error on invalid numeric value" do
      text = """
      foo :: num { bar }
      """

      assert_raise SyntaxError, ~r/Expected :number/, fn -> SCL.loads(text) end
    end
  end

  describe "dumps/1" do
    test "round-trips through loads/1" do
      data = %{"title" => "example", "count" => 3, "enabled" => false}

      serialized = SCL.dumps(data)

      assert String.ends_with?(serialized, "\n")
      assert SCL.loads(serialized) == data
    end
  end

  describe "load/1" do
    test "loads configuration from a .scl file" do
      path = Path.expand("fixtures/sample.scl", __DIR__)
      assert File.exists?(path)

      assert SCL.load(path) == %{
               "name" => "demo",
               "items" => [1, 2, 3],
               "enabled" => true
             }
    end
  end
end


