Gem::Specification.new do |spec|
  spec.name          = "scl_parser"
  spec.version       = "0.1.0"
  spec.authors       = ["shareui"]
  spec.summary       = "Parser for Structured Configuration Language (SCL)"
  spec.description   = "Ruby parser and serializer for SCL: bool, str, num, fl, ml, class, list, dynamic."
  spec.license       = "MIT"
  spec.files         = Dir["lib/**/*", "README.md", "LICENSE*"]
  spec.homepage      = "https://gitlab.com/shareui/scl"
  spec.metadata      = {
    "homepage_uri" => "https://gitlab.com/shareui/scl",
    "source_code_uri" => "https://gitlab.com/shareui/scl",
    "bug_tracker_uri" => "https://discord.com/users/1367967801125376143"
  }
  spec.required_ruby_version = ">= 2.7"
end


