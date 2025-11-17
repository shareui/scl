use std::collections::HashMap;

use crate::errors::SyntaxError;
use crate::tokens::{Token, TokenType};

#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Bool(bool),
    Num(i64),
    Fl(f64),
    Str(String),
    Ml(String),
    Class(HashMap<String, Value>),
    ListBool(Vec<bool>),
    ListNum(Vec<i64>),
    ListFl(Vec<f64>),
    ListStr(Vec<String>),
    Dynamic(Box<Value>),
}

pub struct Parser {
    tokens: Vec<Token>,
    pos: usize,
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        let tokens = tokens.into_iter().filter(|t| t.ttype != TokenType::Newline && t.ttype != TokenType::Comment).collect();
        Self { tokens, pos: 0 }
    }

    fn cur(&self) -> &Token {
        self.tokens.get(self.pos).unwrap_or_else(|| self.tokens.last().expect("tokens not empty"))
    }

    fn eat(&mut self, t: TokenType) -> Result<Token, SyntaxError> {
        let c = self.cur().clone();
        if c.ttype != t {
            return Err(SyntaxError::new(format!("Expected {:?}, got {:?}", t, c.ttype), Some(c.line), Some(c.column)));
        }
        self.pos += 1;
        Ok(c)
    }

    pub fn parse(mut self) -> Result<HashMap<String, Value>, SyntaxError> {
        let mut cfg = HashMap::new();
        while self.cur().ttype != TokenType::Eof {
            let (name, value) = self.parse_parameter()?;
            cfg.insert(name, value);
        }
        Ok(cfg)
    }

    fn parse_parameter(&mut self) -> Result<(String, Value), SyntaxError> {
        let name_tok = self.cur().clone();
        let name = match name_tok.ttype {
            TokenType::Identifier
            | TokenType::BoolKw | TokenType::StrKw | TokenType::NumKw
            | TokenType::FlKw | TokenType::MlKw | TokenType::ClassKw | TokenType::ListKw | TokenType::DynamicKw
            => { self.pos += 1; name_tok.value.unwrap_or_default() }
            TokenType::Number => { self.eat(TokenType::Number)?; name_tok.value.unwrap_or_default() }
            TokenType::String => { self.eat(TokenType::String)?; name_tok.value.unwrap_or_default() }
            _ => {
                return Err(SyntaxError::new(format!("Expected identifier or keyword, got {:?}", name_tok.ttype), Some(name_tok.line), Some(name_tok.column)));
            }
        };
        self.eat(TokenType::DoubleColon)?;
        let ttype = self.cur().ttype;
        let value = match ttype {
            TokenType::BoolKw => { self.eat(TokenType::BoolKw)?; self.parse_bool_value()? }
            TokenType::StrKw => { self.eat(TokenType::StrKw)?; self.parse_str_value()? }
            TokenType::NumKw => { self.eat(TokenType::NumKw)?; self.parse_num_value()? }
            TokenType::FlKw => { self.eat(TokenType::FlKw)?; self.parse_fl_value()? }
            TokenType::MlKw => { self.eat(TokenType::MlKw)?; self.parse_ml_value()? }
            TokenType::ClassKw => { self.eat(TokenType::ClassKw)?; self.parse_class_value()? }
            TokenType::ListKw => { self.eat(TokenType::ListKw)?; self.parse_list_value()? }
            TokenType::DynamicKw => { self.eat(TokenType::DynamicKw)?; self.parse_dynamic_value()? }
            _ => {
                let c = self.cur().clone();
                return Err(SyntaxError::new(format!("Unknown type: {:?}", c.value), Some(c.line), Some(c.column)));
            }
        };
        Ok((name, value))
    }

    fn parse_bool_value(&mut self) -> Result<Value, SyntaxError> {
        self.eat(TokenType::LBrace)?;
        let v = self.cur().clone();
        if v.ttype != TokenType::Boolean {
            return Err(SyntaxError::new("Expected boolean", Some(v.line), Some(v.column)));
        }
        self.pos += 1;
        self.eat(TokenType::RBrace)?;
        Ok(Value::Bool(matches!(v.value.as_deref(), Some("true") | Some("yes"))))
    }

    fn parse_str_value(&mut self) -> Result<Value, SyntaxError> {
        self.eat(TokenType::LBrace)?;
        let v = self.eat(TokenType::String)?;
        self.eat(TokenType::RBrace)?;
        Ok(Value::Str(v.value.unwrap_or_default()))
    }

    fn parse_num_value(&mut self) -> Result<Value, SyntaxError> {
        self.eat(TokenType::LBrace)?;
        let v = self.eat(TokenType::Number)?;
        self.eat(TokenType::RBrace)?;
        let n: i64 = v.value.unwrap_or_default().parse().unwrap_or(0);
        Ok(Value::Num(n))
    }

    fn parse_fl_value(&mut self) -> Result<Value, SyntaxError> {
        self.eat(TokenType::LBrace)?;
        let v = self.cur().clone();
        let f = match v.ttype {
            TokenType::Float => { self.pos += 1; v.value.unwrap_or_default().parse::<f64>().unwrap_or(0.0) }
            TokenType::Number => { self.pos += 1; v.value.unwrap_or_default().parse::<i64>().unwrap_or(0) as f64 }
            _ => return Err(SyntaxError::new("Expected float or number", Some(v.line), Some(v.column))),
        };
        self.eat(TokenType::RBrace)?;
        Ok(Value::Fl(f))
    }

    fn parse_ml_value(&mut self) -> Result<Value, SyntaxError> {
        self.eat(TokenType::LBrace)?;
        let v = self.eat(TokenType::MultilineString)?;
        self.eat(TokenType::RBrace)?;
        Ok(Value::Ml(v.value.unwrap_or_default()))
    }

    fn parse_class_value(&mut self) -> Result<Value, SyntaxError> {
        self.eat(TokenType::LBrace)?;
        let mut map = HashMap::new();
        while self.cur().ttype != TokenType::RBrace {
            let (n, v) = self.parse_parameter()?;
            map.insert(n, v);
        }
        self.eat(TokenType::RBrace)?;
        Ok(Value::Class(map))
    }

    fn parse_list_value(&mut self) -> Result<Value, SyntaxError> {
        self.eat(TokenType::LParen)?;
        let el = self.cur().clone();
        let kind = el.ttype;
        match kind {
            TokenType::NumKw | TokenType::FlKw | TokenType::BoolKw | TokenType::StrKw => { self.pos += 1; }
            _ => return Err(SyntaxError::new(format!("Unsupported list element type: {:?}", el.value), Some(el.line), Some(el.column))),
        }
        self.eat(TokenType::RParen)?;
        self.eat(TokenType::LBrace)?;
        let val = match kind {
            TokenType::NumKw => {
                let mut v = Vec::new();
                while self.cur().ttype != TokenType::RBrace {
                    let n = self.eat(TokenType::Number)?.value.unwrap_or_default().parse::<i64>().unwrap_or(0);
                    v.push(n);
                    if self.cur().ttype == TokenType::Comma { self.pos += 1; }
                    else if self.cur().ttype != TokenType::RBrace {
                        let c = self.cur().clone();
                        return Err(SyntaxError::new("Expected comma or closing brace", Some(c.line), Some(c.column)));
                    }
                }
                Value::ListNum(v)
            }
            TokenType::FlKw => {
                let mut v = Vec::new();
                while self.cur().ttype != TokenType::RBrace {
                    let c = self.cur().clone();
                    let f = match c.ttype {
                        TokenType::Float => { self.pos += 1; c.value.unwrap_or_default().parse::<f64>().unwrap_or(0.0) }
                        TokenType::Number => { self.pos += 1; c.value.unwrap_or_default().parse::<i64>().unwrap_or(0) as f64 }
                        _ => return Err(SyntaxError::new("Expected float or number", Some(c.line), Some(c.column))),
                    };
                    v.push(f);
                    if self.cur().ttype == TokenType::Comma { self.pos += 1; }
                    else if self.cur().ttype != TokenType::RBrace {
                        let c2 = self.cur().clone();
                        return Err(SyntaxError::new("Expected comma or closing brace", Some(c2.line), Some(c2.column)));
                    }
                }
                Value::ListFl(v)
            }
            TokenType::BoolKw => {
                let mut v = Vec::new();
                while self.cur().ttype != TokenType::RBrace {
                    let b = matches!(self.eat(TokenType::Boolean)?.value.as_deref(), Some("true") | Some("yes"));
                    v.push(b);
                    if self.cur().ttype == TokenType::Comma { self.pos += 1; }
                    else if self.cur().ttype != TokenType::RBrace {
                        let c = self.cur().clone();
                        return Err(SyntaxError::new("Expected comma or closing brace", Some(c.line), Some(c.column)));
                    }
                }
                Value::ListBool(v)
            }
            TokenType::StrKw => {
                let mut v = Vec::new();
                while self.cur().ttype != TokenType::RBrace {
                    let s = self.eat(TokenType::String)?.value.unwrap_or_default();
                    v.push(s);
                    if self.cur().ttype == TokenType::Comma { self.pos += 1; }
                    else if self.cur().ttype != TokenType::RBrace {
                        let c = self.cur().clone();
                        return Err(SyntaxError::new("Expected comma or closing brace", Some(c.line), Some(c.column)));
                    }
                }
                Value::ListStr(v)
            }
            _ => unreachable!(),
        };
        self.eat(TokenType::RBrace)?;
        Ok(val)
    }

    fn parse_dynamic_value(&mut self) -> Result<Value, SyntaxError> {
        self.eat(TokenType::LBrace)?;
        let c = self.cur().clone();
        let v = match c.ttype {
            TokenType::Number => { self.pos += 1; Value::Num(c.value.unwrap_or_default().parse::<i64>().unwrap_or(0)) }
            TokenType::Float => { self.pos += 1; Value::Fl(c.value.unwrap_or_default().parse::<f64>().unwrap_or(0.0)) }
            TokenType::Boolean => { self.pos += 1; Value::Bool(matches!(c.value.as_deref(), Some("true") | Some("yes"))) }
            TokenType::String => { self.pos += 1; Value::Str(c.value.unwrap_or_default()) }
            TokenType::MultilineString => { self.pos += 1; Value::Ml(c.value.unwrap_or_default()) }
            _ => return Err(SyntaxError::new("dynamic supports only base types (bool, str, num, fl, ml)", Some(c.line), Some(c.column))),
        };
        self.eat(TokenType::RBrace)?;
        Ok(Value::Dynamic(Box::new(v)))
    }
}


