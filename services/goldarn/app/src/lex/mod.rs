use std::{collections::VecDeque, rc::Rc};

use crate::{
    ast::{
        node::{Atom, Node},
        value::Value,
    },
    error::LanguageError,
    prs::token::Token,
};

pub fn build_ast(tokens: Vec<Token>) -> Result<Atom, LanguageError> {
    let mut stack = VecDeque::new();
    for token in tokens {
        if token.value.starts_with('\'') {
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Const(Value::I(token.value[1..].parse().map_err(|err| LanguageError {
                    code: token.code.clone(),
                    error: format!("{}", err),
                    span: token.span.clone(),
                })?)),
                span: token.span,
            });
            continue;
        }

        if token.value.starts_with('@') {
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Const(Value::S(token.value[1..].to_owned())),
                span: token.span,
            });
            continue;
        }

        if token.value == "+" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Add(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "-" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Sub(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "*" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Mul(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "/" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Div(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == ";" {
            let v = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Exec(Box::new(v)),
                span: token.span,
            });
            continue;
        }

        if token.value == "," {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Second(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "\"" {
            let v = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Show(Box::new(v)),
                span: token.span,
            });
            continue;
        }

        if token.value == "`" {
            let v = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::ShowLn(Box::new(v)),
                span: token.span,
            });
            continue;
        }

        if token.value == "!" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Write(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "%" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Append(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "?" {
            let v = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Read(Box::new(v)),
                span: token.span,
            });
            continue;
        }

        if token.value == "$" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Define(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "$$" {
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Define(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "^" {
            let v = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Access(Box::new(v)),
                span: token.span,
            });
            continue;
        }

        if token.value == "#" {
            let v = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Call(Box::new(v)),
                span: token.span,
            });
            continue;
        }

        if token.value.starts_with(':') {
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::InlineCall(token.value[1..].to_owned()),
                span: token.span,
            });
            continue;
        }

        if token.value == "=" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Eq(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "<" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Lt(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "~" {
            let v = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Not(Box::new(v)),
                span: token.span,
            });
            continue;
        }

        if token.value == "&" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::And(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "{" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            let v = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no if argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::If(Box::new(v), Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        if token.value == "." {
            let v = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Chr(Box::new(v)),
                span: token.span,
            });
            continue;
        }

        if token.value == "§" {
            let r = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no right argument".to_owned(),
                span: token.span.clone(),
            })?;
            let l = stack.pop_back().ok_or_else(|| LanguageError {
                code: token.code.clone(),
                error: "no left argument".to_owned(),
                span: token.span.clone(),
            })?;
            stack.push_back(Atom {
                code: token.code.clone(),
                node: Node::Ord(Box::new(l), Box::new(r)),
                span: token.span,
            });
            continue;
        }

        return Err(LanguageError {
            code: token.code.clone(),
            error: "unknown token".to_owned(),
            span: token.span,
        });
    }

    if stack.len() == 1 {
        Ok(stack.pop_back().unwrap())
    } else {
        Err(LanguageError {
            code: if let Some(token) = stack.back() {
                token.code.clone()
            } else {
                Rc::new(String::new())
            },
            error: "no tokens found or more than 1 token left".to_owned(),
            span: 0..0,
        })
    }
}
