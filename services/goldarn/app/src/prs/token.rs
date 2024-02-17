use std::{ops::Range, rc::Rc};

#[derive(Debug)]
pub struct Token {
    pub code: Rc<String>,
    pub value: String,
    pub span: Range<usize>,
}
