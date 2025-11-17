use crate::errors::SyntaxError;
use crate::tokens::{Token, TokenType};

pub struct Lexer<'a> {
    text: &'a str,
    bytes: &'a [u8],
    pos: usize,
    line: usize,
    col: usize,
    tokens: Vec<Token>,
}

impl<'a> Lexer<'a> {
    pub fn new(text: &'a str) -> Self {
        Self { text, bytes: text.as_bytes(), pos: 0, line: 1, col: 1, tokens: Vec::new() }
    }

    fn peek(&self, off: usize) -> Option<u8> {
        self.bytes.get(self.pos + off).copied()
    }

    fn advance(&mut self) -> Option<u8> {
        if let Some(&b) = self.bytes.get(self.pos) {
            self.pos += 1;
            if b == b'\n' {
                self.line += 1;
                self.col = 1;
            } else {
                self.col += 1;
            }
            Some(b)
        } else {
            None
        }
    }

    fn add(&mut self, t: TokenType, value: Option<String>, line: usize, col: usize) {
        self.tokens.push(Token::new(t, value, line, col));
    }

    fn skip_ws(&mut self) {
        while matches!(self.peek(0), Some(b' ' | b'\t')) {
            self.advance();
        }
    }

    fn error<T>(&self, msg: &str) -> Result<T, SyntaxError> {
        Err(SyntaxError::new(msg, Some(self.line), Some(self.col)))
    }

    fn read_comment(&mut self) -> Result<(), SyntaxError> {
        let line = self.line;
        let col = self.col;
        self.advance(); // '['
        let start = self.pos;
        while let Some(b) = self.peek(0) {
            if b == b']' { break; }
            self.advance();
        }
        if self.peek(0) != Some(b']') {
            return self.error("Unclosed comment");
        }
        let s = &self.text[start..self.pos];
        self.advance(); // ']'
        self.add(TokenType::Comment, Some(s.trim().to_string()), line, col);
        Ok(())
    }

    fn read_string(&mut self) -> Result<(), SyntaxError> {
        let line = self.line;
        let col = self.col;
        self.advance(); // "
        let mut out = String::new();
        while let Some(b) = self.peek(0) {
            if b == b'"' { break; }
            let ch = self.advance().unwrap();
            if ch == b'\\' {
                match self.peek(0) {
                    Some(b'n') => { self.advance(); out.push('\n'); }
                    Some(b't') => { self.advance(); out.push('\t'); }
                    Some(b'"') => { self.advance(); out.push('"'); }
                    Some(b'\\') => { self.advance(); out.push('\\'); }
                    Some(x) => { out.push(x as char); self.advance(); }
                    None => return self.error("Unexpected end of string after backslash"),
                }
            } else {
                out.push(ch as char);
            }
        }
        if self.peek(0) != Some(b'"') {
            return self.error("Unclosed string");
        }
        self.advance(); // "
        self.add(TokenType::String, Some(out), line, col);
        Ok(())
    }

    fn read_multiline_string(&mut self) -> Result<(), SyntaxError> {
        let line = self.line;
        let col = self.col;
        self.advance(); // '
        let start = self.pos;
        while let Some(b) = self.peek(0) {
            if b == b'\'' { break; }
            self.advance();
        }
        if self.peek(0) != Some(b'\'') {
            return self.error("Unclosed multiline string");
        }
        let s = &self.text[start..self.pos];
        self.advance(); // '
        self.add(TokenType::MultilineString, Some(s.to_string()), line, col);
        Ok(())
    }

    fn read_number(&mut self) -> Result<(), SyntaxError> {
        let line = self.line;
        let col = self.col;
        let mut buf = String::new();
        if self.peek(0) == Some(b'-') {
            buf.push('-' as char);
            self.advance();
            if self.peek(0).map(|c| (c as char).is_ascii_digit()) != Some(true) {
                return self.error("Expected digit after '-'");
            }
        }
        let mut has_dot = false;
        while let Some(b) = self.peek(0) {
            if (b as char).is_ascii_digit() {
                buf.push(b as char);
                self.advance();
            } else if b == b'.' {
                if has_dot { break; }
                has_dot = true;
                buf.push('.');
                self.advance();
            } else {
                break;
            }
        }
        if has_dot {
            self.add(TokenType::Float, Some(buf), line, col);
        } else {
            self.add(TokenType::Number, Some(buf), line, col);
        }
        Ok(())
    }

    fn read_identifier_or_number(&mut self) -> Result<(), SyntaxError> {
        // if digits followed by letter/underscore -> identifier
        let line = self.line;
        let col = self.col;
        let start = self.pos;
        while let Some(b) = self.peek(0) {
            if (b as char).is_ascii_digit() {
                self.advance();
            } else {
                break;
            }
        }
        if let Some(b) = self.peek(0) {
            if (b as char).is_ascii_alphabetic() || b == b'_' {
                let mut s = self.text[start..self.pos].to_string();
                while let Some(b2) = self.peek(0) {
                    let ch = b2 as char;
                    if ch.is_ascii_alphanumeric() || ch == '_' || ch == '-' {
                        s.push(ch);
                        self.advance();
                    } else {
                        break;
                    }
                }
                self.add(TokenType::Identifier, Some(s), line, col);
                return Ok(());
            }
        }
        // number
        self.pos = start;
        self.read_number()
    }

    fn read_identifier(&mut self) -> Result<(), SyntaxError> {
        let line = self.line;
        let col = self.col;
        let mut s = String::new();
        while let Some(b) = self.peek(0) {
            let ch = b as char;
            if ch.is_ascii_alphanumeric() || ch == '_' || ch == '-' {
                s.push(ch);
                self.advance();
            } else {
                break;
            }
        }
        let t = match s.as_str() {
            "bool" => TokenType::BoolKw,
            "str" => TokenType::StrKw,
            "num" => TokenType::NumKw,
            "fl" => TokenType::FlKw,
            "ml" => TokenType::MlKw,
            "class" => TokenType::ClassKw,
            "list" => TokenType::ListKw,
            "dynamic" => TokenType::DynamicKw,
            "true" | "false" | "yes" | "no" => TokenType::Boolean,
            _ => TokenType::Identifier,
        };
        if t == TokenType::Boolean {
            let val = matches!(s.as_str(), "true" | "yes").to_string();
            self.add(TokenType::Boolean, Some(val), line, col);
        } else {
            self.add(t, Some(s), line, col);
        }
        Ok(())
    }

    pub fn tokenize(mut self) -> Result<Vec<Token>, SyntaxError> {
        while self.pos < self.bytes.len() {
            self.skip_ws();
            if self.pos >= self.bytes.len() { break; }
            match self.peek(0) {
                Some(b'[') => { self.read_comment()?; }
                Some(b'\n') => {
                    let l = self.line; let c = self.col;
                    self.add(TokenType::Newline, Some("\n".into()), l, c);
                    self.advance();
                }
                Some(b':') if self.peek(1) == Some(b':') => {
                    let l = self.line; let c = self.col;
                    self.advance(); self.advance();
                    self.add(TokenType::DoubleColon, Some("::".into()), l, c);
                }
                Some(b'{') => { let l=self.line; let c=self.col; self.advance(); self.add(TokenType::LBrace, Some("{".into()), l, c); }
                Some(b'}') => { let l=self.line; let c=self.col; self.advance(); self.add(TokenType::RBrace, Some("}".into()), l, c); }
                Some(b'(') => { let l=self.line; let c=self.col; self.advance(); self.add(TokenType::LParen, Some("(".into()), l, c); }
                Some(b')') => { let l=self.line; let c=self.col; self.advance(); self.add(TokenType::RParen, Some(")".into()), l, c); }
                Some(b',') => { let l=self.line; let c=self.col; self.advance(); self.add(TokenType::Comma, Some(",".into()), l, c); }
                Some(b'"') => { self.read_string()?; }
                Some(b'\'') => { self.read_multiline_string()?; }
                Some(b'-') if self.peek(1).map(|c| (c as char).is_ascii_digit()) == Some(true) => { self.read_number()?; }
                Some(b) if (b as char).is_ascii_digit() => { self.read_identifier_or_number()?; }
                Some(b) if (b as char).is_ascii_alphabetic() || b == b'_' => { self.read_identifier()?; }
                Some(_) => { return self.error("Unexpected character"); }
                None => break,
            }
        }
        self.add(TokenType::Eof, None, self.line, self.col);
        Ok(self.tokens)
    }
}


