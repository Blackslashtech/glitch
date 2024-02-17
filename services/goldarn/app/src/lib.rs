#![feature(file_create_new)]

use std::rc::Rc;

use ast::value::Value;
use error::LanguageError;

pub mod ast;
pub mod error;
pub mod exc;
pub mod lex;
pub mod prs;

pub fn run(ctx: &mut exc::context::Context, code: Rc<String>) -> Result<Value, LanguageError> {
    let ast = lex::build_ast(prs::parse(code))?;
    ctx.exec(ast, 0)
}
