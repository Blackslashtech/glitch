use std::{ops::Range, rc::Rc};

pub struct LanguageError {
    pub code: Rc<String>,
    pub error: String,
    pub span: Range<usize>,
}

impl LanguageError {
    pub fn apply(&self) -> String {
        format!(
            "{}{}{}",
            &self.code[0..self.span.start],
            ansi_term::Colour::Red.underline().paint(&self.code[self.span.clone()]),
            &self.code[self.span.end..]
        )
    }
}
