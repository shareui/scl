mod errors;
mod tokens;
mod lexer;
mod parser;
mod serializer;

use std::collections::HashMap;
use std::fs;
use std::io::{Read, Write};
use std::path::Path;

pub use errors::{ParseError, SyntaxError};
pub use parser::Value;
use lexer::Lexer;
use parser::Parser;
use serializer::Serializer;

pub fn loads(text: &str) -> Result<HashMap<String, Value>, SyntaxError> {
    let tokens = Lexer::new(text).tokenize()?;
    Parser::new(tokens).parse()
}

pub fn load<P: AsRef<Path>>(path: P) -> Result<HashMap<String, Value>, Box<dyn std::error::Error>> {
    let mut f = fs::File::open(path)?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    let m = loads(&s)?;
    Ok(m)
}

pub fn dumps(data: &HashMap<String, Value>, indent: usize) -> String {
    Serializer::new(indent).serialize_map(data)
}

pub fn dump<P: AsRef<Path>>(data: &HashMap<String, Value>, path: P, indent: usize) -> Result<(), Box<dyn std::error::Error>> {
    let s = dumps(data, indent);
    let mut f = fs::File::create(path)?;
    f.write_all(s.as_bytes())?;
    Ok(())
}


