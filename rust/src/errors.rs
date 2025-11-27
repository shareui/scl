use std::fmt::{Display, Formatter, Result as FmtResult};

#[derive(Debug)]
pub struct SyntaxError {
    pub message: String,
    pub line: Option<usize>,
    pub column: Option<usize>,
}

impl SyntaxError {
    pub fn new<M: Into<String>>(message: M, line: Option<usize>, column: Option<usize>) -> Self {
        Self { message: message.into(), line, column }
    }
}

impl Display for SyntaxError {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match (self.line, self.column) {
            (Some(l), Some(c)) => write!(f, "Syntax error at line {}, column {}: {}", l, c, self.message),
            _ => write!(f, "Syntax error: {}", self.message),
        }
    }
}

impl std::error::Error for SyntaxError {}

#[derive(Debug)]
pub struct ParseError {
    pub message: String,
}

impl ParseError {
    pub fn new<M: Into<String>>(message: M) -> Self {
        Self { message: message.into() }
    }
}

impl Display for ParseError {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        write!(f, "Parse error: {}", self.message)
    }
}

impl std::error::Error for ParseError {}


