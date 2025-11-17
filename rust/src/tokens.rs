#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TokenType {
    Identifier,
    DoubleColon,
    BoolKw,
    StrKw,
    NumKw,
    FlKw,
    MlKw,
    ClassKw,
    ListKw,
    DynamicKw,
    LBrace,
    RBrace,
    LParen,
    RParen,
    Comma,
    String,
    MultilineString, // ml
    Number,
    Float,
    Boolean,
    Comment,
    Newline,
    Eof, // end of dile
}

#[derive(Debug, Clone)]
pub struct Token {
    pub ttype: TokenType,
    pub value: Option<String>,
    pub line: usize,
    pub column: usize,
}

impl Token {
    pub fn new(ttype: TokenType, value: Option<String>, line: usize, column: usize) -> Self {
        Self { ttype, value, line, column }
    }
}


