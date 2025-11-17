use std::collections::HashMap;

use crate::errors::ParseError;
use crate::parser::Value;

pub struct Serializer {
    indent: usize,
}

impl Serializer {
    pub fn new(indent: usize) -> Self {
        Self { indent: if indent == 0 { 4 } else { indent } }
    }

    pub fn serialize_map(&self, data: &HashMap<String, Value>) -> String {
        let mut out = String::new();
        out.push_str(&self.serialize_level(data, 0));
        out.push('\n');
        out
    }

    fn serialize_level(&self, data: &HashMap<String, Value>, level: usize) -> String {
        let mut lines: Vec<String> = Vec::new();
        let indent = " ".repeat(self.indent * level);
        for (k, v) in data {
            let mut line = String::new();
            line.push_str(&indent);
            line.push_str(k);
            line.push_str(" :: ");
            line.push_str(&self.serialize_value(v, level));
            lines.push(line);
        }
        lines.join("\n")
    }

    fn serialize_value(&self, v: &Value, level: usize) -> String {
        match v {
            Value::Bool(b) => format!("bool {{ {} }}", if *b { "true" } else { "false" }),
            Value::Num(n) => format!("num {{ {} }}", n),
            Value::Fl(f) => format!("fl {{ {} }}", trim_float(*f)),
            Value::Str(s) => {
                if s.contains('\n') {
                    let indent = " ".repeat(self.indent * level);
                    format!("ml {{\n{}    '{}'\n{}}}", indent, s, indent)
                } else {
                    let esc = s.replace('\\', "\\\\").replace('"', "\\\"");
                    format!("str {{ \"{}\" }}", esc)
                }
            }
            Value::Ml(s) => {
                let indent = " ".repeat(self.indent * level);
                format!("ml {{\n{}    '{}'\n{}}}", indent, s, indent)
            }
            Value::Class(map) => {
                let mut s = String::from("class {\n");
                s.push_str(&self.serialize_level(map, level + 1));
                s.push('\n');
                s.push_str(&" ".repeat(self.indent * level));
                s.push('}');
                s
            }
            Value::ListBool(vs) => {
                let items = vs.iter().map(|b| if *b { "true".to_string() } else { "false".to_string() }).collect::<Vec<_>>().join(", ");
                format!("list(bool) {{ {} }}", items)
            }
            Value::ListNum(vs) => {
                let items = vs.iter().map(|n| n.to_string()).collect::<Vec<_>>().join(", ");
                format!("list(num) {{ {} }}", items)
            }
            Value::ListFl(vs) => {
                let items = vs.iter().map(|f| trim_float(*f)).collect::<Vec<_>>().join(", ");
                format!("list(fl) {{ {} }}", items)
            }
            Value::ListStr(vs) => {
                let items = vs.iter().map(|s| format!("\"{}\"", s.replace('\\', "\\\\").replace('"', "\\\""))).collect::<Vec<_>>().join(", ");
                format!("list(str) {{ {} }}", items)
            }
            Value::Dynamic(inner) => {
                self.serialize_dynamic(inner.as_ref(), level).expect("dynamic serialization failed")
            }
        }
    }

    pub fn serialize_dynamic(&self, v: &Value, level: usize) -> Result<String, ParseError> {
        let s = match v {
            Value::Bool(b) => format!("dynamic {{ {} }}", if *b { "true" } else { "false" }),
            Value::Num(n) => format!("dynamic {{ {} }}", n),
            Value::Fl(f) => format!("dynamic {{ {} }}", trim_float(*f)),
            Value::Str(s) => {
                if s.contains('\n') {
                    let indent = " ".repeat(self.indent * level);
                    format!("ml {{\n{}    '{}'\n{}}}", indent, s, indent)
                } else {
                    let esc = s.replace('\\', "\\\\").replace('"', "\\\"");
                    format!("dynamic {{ \"{}\" }}", esc)
                }
            }
            Value::Ml(s) => {
                let indent = " ".repeat(self.indent * level);
                format!("ml {{\n{}    '{}'\n{}}}", indent, s, indent)
            }
            Value::Class(_) | Value::ListBool(_) | Value::ListNum(_) | Value::ListFl(_) | Value::ListStr(_) => {
                return Err(ParseError::new("Unsupported value type for dynamic"));
            }
        };
        Ok(s)
    }
}

fn trim_float(f: f64) -> String {
    let s = format!("{}", f);
    if s.contains('.') {
        let s2 = s.trim_end_matches('0').trim_end_matches('.');
        if s2.is_empty() { "0".to_string() } else { s2.to_string() }
    } else {
        s
    }
}


