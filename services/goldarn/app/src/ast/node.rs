use std::{ops::Range, rc::Rc};

use super::value::Value;

#[derive(Debug)]
pub enum Node<T> {
    Const(Value),
    Add(Box<T>, Box<T>),
    Sub(Box<T>, Box<T>),
    Mul(Box<T>, Box<T>),
    Div(Box<T>, Box<T>),
    Exec(Box<T>),
    Second(Box<T>, Box<T>),
    Show(Box<T>),
    ShowLn(Box<T>),
    Write(Box<T>, Box<T>),
    Append(Box<T>, Box<T>),
    Read(Box<T>),
    Define(Box<T>, Box<T>),
    Access(Box<T>),
    Call(Box<T>),
    InlineCall(String),
    Eq(Box<T>, Box<T>),
    Lt(Box<T>, Box<T>),
    Not(Box<T>),
    And(Box<T>, Box<T>),
    If(Box<T>, Box<T>, Box<T>),
    Chr(Box<T>),
    Ord(Box<T>, Box<T>),
}

#[derive(Debug)]
pub struct Atom {
    pub code: Rc<String>,
    pub node: Node<Atom>,
    pub span: Range<usize>,
}
