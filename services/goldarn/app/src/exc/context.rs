use std::{collections::HashMap, io::Write, rc::Rc};

use crate::{
    ast::{
        node::{Atom, Node},
        value::Value,
    },
    error::LanguageError,
    lex, prs,
};

const MAX_TOTAL_FILE_BYTES: usize = 256;
const MAX_STRING_LENGTH: usize = 32768;
const MAX_VARIABLES: usize = 1024;
const MAX_RECURSION_DEPTH: usize = 64;

#[derive(Default)]
pub struct Context {
    variables: HashMap<String, Value>,
    total_file_bytes: usize,
}

impl Context {
    pub fn exec(&mut self, ast: Atom, depth: usize) -> Result<Value, LanguageError> {
        let span = ast.span.clone();
        if depth > MAX_RECURSION_DEPTH {
            return Err(LanguageError {
                code: ast.code,
                error: "recursion depth exceeded".to_owned(),
                span: span,
            });
        }
        match ast.node {
            Node::Const(v) => match v {
                Value::I(v) => Ok(Value::I(v)),
                Value::S(v) => {
                    if v.len() > MAX_STRING_LENGTH {
                        Err(LanguageError {
                            code: ast.code,
                            error: "string length exceeded".to_owned(),
                            span,
                        })
                    } else {
                        Ok(Value::S(v))
                    }
                }
            },

            Node::Add(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                let r = self.exec(*r, depth + 1)?;
                match l {
                    Value::I(l) => {
                        if let Value::I(r) = r {
                            Ok(Value::I(l + r))
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "can't add string to int".to_owned(),
                                span,
                            })
                        }
                    }
                    Value::S(l) => {
                        if let Value::S(r) = r {
                            if l.len() + r.len() > MAX_STRING_LENGTH {
                                Err(LanguageError {
                                    code: ast.code,
                                    error: "string length exceeded".to_owned(),
                                    span,
                                })
                            } else {
                                Ok(Value::S(l + &r))
                            }
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "can't add int to string".to_owned(),
                                span,
                            })
                        }
                    }
                }
            }

            Node::Sub(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                let r = self.exec(*r, depth + 1)?;
                match l {
                    Value::I(l) => {
                        if let Value::I(r) = r {
                            Ok(Value::I(l - r))
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "can't sub string from int".to_owned(),
                                span,
                            })
                        }
                    }
                    Value::S(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't sub from string".to_owned(),
                        span,
                    }),
                }
            }

            Node::Mul(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                let r = self.exec(*r, depth + 1)?;
                match l {
                    Value::I(l) => {
                        if let Value::I(r) = r {
                            Ok(Value::I(l * r))
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "can't mul int by string".to_owned(),
                                span,
                            })
                        }
                    }
                    Value::S(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't mul string".to_owned(),
                        span,
                    }),
                }
            }

            Node::Div(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                let r = self.exec(*r, depth + 1)?;
                match l {
                    Value::I(l) => {
                        if let Value::I(r) = r {
                            Ok(Value::I(l / r))
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "can't div int by string".to_owned(),
                                span,
                            })
                        }
                    }
                    Value::S(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't div string".to_owned(),
                        span,
                    }),
                }
            }

            Node::Exec(v) => {
                let v = self.exec(*v, depth + 1)?;
                match v {
                    Value::I(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't exec int".to_owned(),
                        span,
                    }),
                    Value::S(v) => self.exec(lex::build_ast(prs::parse(Rc::new(v)))?, depth + 1),
                }
            }

            Node::Second(l, r) => {
                self.exec(*l, depth + 1)?;
                self.exec(*r, depth + 1)
            }

            Node::Show(v) => {
                let v = self.exec(*v, depth + 1)?;
                let s = match v {
                    Value::I(v) => format!("{v}"),
                    Value::S(v) => format!("{v}"),
                };
                print!("{s}");
                Ok(Value::I(s.chars().count() as i64))
            }

            Node::ShowLn(v) => {
                let v = self.exec(*v, depth + 1)?;
                let s = match v {
                    Value::I(v) => format!("{v}"),
                    Value::S(v) => format!("{v}"),
                };
                println!("{s}");
                Ok(Value::I(s.chars().count() as i64))
            }

            Node::Write(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                let r = self.exec(*r, depth + 1)?;
                match l {
                    Value::I(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't use int as file name".to_owned(),
                        span,
                    }),
                    Value::S(l) => match r {
                        Value::I(_) => Err(LanguageError {
                            code: ast.code,
                            error: "can't write int to file".to_owned(),
                            span,
                        }),
                        Value::S(r) => {
                            let Ok(mut f) = std::fs::File::create_new(l) else {
                                return Err(LanguageError {
                                    code: ast.code,
                                    error: "can't create new file".to_owned(),
                                    span,
                                })
                            };
                            if self.total_file_bytes + r.as_bytes().len() > MAX_TOTAL_FILE_BYTES {
                                return Err(LanguageError {
                                    code: ast.code,
                                    error: "total file bytes exceeded".to_owned(),
                                    span,
                                });
                            } else {
                                self.total_file_bytes += r.as_bytes().len()
                            }
                            if f.write_all(r.as_bytes()).is_err() {
                                Err(LanguageError {
                                    code: ast.code,
                                    error: "can't write to file".to_owned(),
                                    span,
                                })
                            } else {
                                Ok(Value::I(r.chars().count() as i64))
                            }
                        }
                    },
                }
            }

            Node::Append(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                let r = self.exec(*r, depth + 1)?;
                match l {
                    Value::I(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't use int as file name".to_owned(),
                        span,
                    }),
                    Value::S(l) => match r {
                        Value::I(_) => Err(LanguageError {
                            code: ast.code,
                            error: "can't write int to file".to_owned(),
                            span,
                        }),
                        Value::S(r) => {
                            let Ok(mut f) = std::fs::OpenOptions::new().append(true).open(l) else {
                                return Err(LanguageError {
                                    code: ast.code,
                                    error: "can't create new file".to_owned(),
                                    span,
                                })
                            };
                            if self.total_file_bytes + r.as_bytes().len() > MAX_TOTAL_FILE_BYTES {
                                return Err(LanguageError {
                                    code: ast.code,
                                    error: "total file bytes exceeded".to_owned(),
                                    span,
                                });
                            } else {
                                self.total_file_bytes += r.as_bytes().len()
                            }
                            if f.write_all(r.as_bytes()).is_err() {
                                Err(LanguageError {
                                    code: ast.code,
                                    error: "can't write to file".to_owned(),
                                    span,
                                })
                            } else {
                                Ok(Value::I(r.chars().count() as i64))
                            }
                        }
                    },
                }
            }

            Node::Read(v) => {
                let v = self.exec(*v, depth + 1)?;
                match v {
                    Value::I(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't use int as file name".to_owned(),
                        span,
                    }),
                    Value::S(v) => {
                        let Ok(s) = std::fs::read_to_string(v) else {
                            return Err(LanguageError {
                                code: ast.code,
                                error: "can't read from file".to_owned(),
                                span,
                            })
                        };

                        Ok(Value::S(s))
                    }
                }
            }

            Node::Define(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                let r = self.exec(*r, depth + 1)?;
                match l {
                    Value::I(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't use int as variable name".to_owned(),
                        span,
                    }),
                    Value::S(l) => {
                        self.variables.insert(l, r.clone());
                        if self.variables.len() > MAX_VARIABLES {
                            Err(LanguageError {
                                code: ast.code,
                                error: "variables exceeded".to_owned(),
                                span,
                            })
                        } else {
                            Ok(r)
                        }
                    }
                }
            }

            Node::Access(v) => {
                let v = self.exec(*v, depth + 1)?;
                match v {
                    Value::I(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't access int".to_owned(),
                        span,
                    }),
                    Value::S(v) => self
                        .variables
                        .get(&v)
                        .ok_or(LanguageError {
                            code: ast.code,
                            error: "no such variable".to_owned(),
                            span,
                        })
                        .map(Clone::clone),
                }
            }

            Node::Call(v) => {
                let v = self.exec(*v, depth + 1)?;
                match v {
                    Value::I(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't call int".to_owned(),
                        span,
                    }),
                    Value::S(v) => {
                        let v = self.variables.get(&v).ok_or(LanguageError {
                            code: ast.code.clone(),
                            error: "no such variable".to_owned(),
                            span: span.clone(),
                        })?;
                        match v {
                            Value::I(_) => Err(LanguageError {
                                code: ast.code.clone(),
                                error: "can't exec int".to_owned(),
                                span,
                            }),
                            Value::S(v) => self.exec(lex::build_ast(prs::parse(Rc::new(v.to_string())))?, depth + 1),
                        }
                    }
                }
            }

            Node::InlineCall(v) => {
                let v = self.variables.get(&v).ok_or(LanguageError {
                    code: ast.code.clone(),
                    error: "no such variable".to_owned(),
                    span: span.clone(),
                })?;
                match v {
                    Value::I(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't exec int".to_owned(),
                        span,
                    }),
                    Value::S(v) => self.exec(lex::build_ast(prs::parse(Rc::new(v.to_string())))?, depth + 1),
                }
            }

            Node::Eq(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                let r = self.exec(*r, depth + 1)?;
                match l {
                    Value::I(l) => {
                        if let Value::I(r) = r {
                            Ok(Value::I(i64::from(l == r)))
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "can't compare string to int".to_owned(),
                                span,
                            })
                        }
                    }
                    Value::S(l) => {
                        if let Value::S(r) = r {
                            Ok(Value::I(i64::from(l == r)))
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "can't compare int to string".to_owned(),
                                span,
                            })
                        }
                    }
                }
            }

            Node::Lt(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                let r = self.exec(*r, depth + 1)?;
                match l {
                    Value::I(l) => {
                        if let Value::I(r) = r {
                            Ok(Value::I(i64::from(l < r)))
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "can't compare string to int".to_owned(),
                                span,
                            })
                        }
                    }
                    Value::S(l) => {
                        if let Value::S(r) = r {
                            Ok(Value::I(i64::from(l < r)))
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "can't compare int to string".to_owned(),
                                span,
                            })
                        }
                    }
                }
            }

            Node::Not(v) => {
                let v = self.exec(*v, depth + 1)?;
                match v {
                    Value::I(v) => Ok(Value::I(i64::from(v == 0))),
                    Value::S(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't not string".to_owned(),
                        span,
                    }),
                }
            }

            Node::And(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                match l {
                    Value::I(l) => {
                        if l == 0 {
                            return Ok(Value::I(0));
                        }

                        let r = self.exec(*r, depth + 1)?;
                        if let Value::I(r) = r {
                            Ok(Value::I(i64::from(r != 0)))
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "can't and int and string".to_owned(),
                                span,
                            })
                        }
                    }
                    Value::S(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't and string".to_owned(),
                        span,
                    }),
                }
            }

            Node::If(v, l, r) => {
                let v = self.exec(*v, depth + 1)?;
                match v {
                    Value::I(v) => {
                        if v == 0 {
                            self.exec(*l, depth + 1)
                        } else {
                            self.exec(*r, depth + 1)
                        }
                    }
                    Value::S(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't if on string".to_owned(),
                        span,
                    }),
                }
            }

            Node::Chr(v) => {
                let v = self.exec(*v, depth + 1)?;
                match v {
                    Value::I(v) => {
                        if let Some(c) = char::from_u32(v as u32) {
                            Ok(Value::S(c.to_string()))
                        } else {
                            Err(LanguageError {
                                code: ast.code,
                                error: "invalid char code".to_owned(),
                                span,
                            })
                        }
                    }
                    Value::S(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't chr string".to_owned(),
                        span,
                    }),
                }
            }

            Node::Ord(l, r) => {
                let l = self.exec(*l, depth + 1)?;
                let r = self.exec(*r, depth + 1)?;
                match l {
                    Value::I(_) => Err(LanguageError {
                        code: ast.code,
                        error: "can't ord int".to_owned(),
                        span,
                    }),
                    Value::S(l) => match r {
                        Value::I(r) => {
                            if let Some(c) = l.chars().nth(r as usize) {
                                Ok(Value::I(c as u32 as i64))
                            } else {
                                Err(LanguageError {
                                    code: ast.code,
                                    error: "bad index".to_owned(),
                                    span,
                                })
                            }
                        }
                        Value::S(_) => Err(LanguageError {
                            code: ast.code,
                            error: "can't use string as index".to_owned(),
                            span,
                        }),
                    },
                }
            }
        }
    }
}
