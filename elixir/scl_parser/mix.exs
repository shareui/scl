defmodule SCLParser.MixProject do
  use Mix.Project

  def project do
    [
      app: :scl_parser,
      version: "0.1.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      description: "Parser for Structured Configuration Language (SCL)",
      package: [
        licenses: ["MIT"],
        links: %{
          "Homepage" => "https://gitlab.com/shareui/scl",
          "Source" => "https://gitlab.com/shareui/scl",
          "Bug Reports" => "https://discord.com/users/1367967801125376143"
        }
      ]
    ]
  end

  def application do
    [
      extra_applications: [:logger]
    ]
  end

  defp deps do
    []
  end
end


