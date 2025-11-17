require_relative "test_helper"

class SCLParserTest < Minitest::Test
  def test_loads_simple_configuration
    text = <<~SCL
      foo :: num { 42 }
      flag :: bool { true }
    SCL

    assert_equal({"foo" => 42, "flag" => true}, SCL.loads(text))
  end

  def test_dumps_round_trips_with_loads
    data = {"title" => "example", "count" => 3, "enabled" => false}

    serialized = SCL.dumps(data)

    assert serialized.end_with?("\n")
    assert_equal(data, SCL.loads(serialized))
  end

  def test_loads_raises_for_invalid_number
    text = <<~SCL
      foo :: num { bar }
    SCL

    error = assert_raises(SCL::SyntaxError) { SCL.loads(text) }
    assert_includes(error.message, ":number")
  end

  def test_load_reads_from_scl_file
    path = File.expand_path("fixtures/sample.scl", __dir__)
    assert File.exist?(path), "fixture is missing"

    result = SCL.load(path)
    expected = {"title" => "demo", "values" => [10, 20], "active" => false}

    assert_equal(expected, result)
  end
end


