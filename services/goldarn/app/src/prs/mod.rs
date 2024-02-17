use std::rc::Rc;

use self::token::Token;

pub mod token;

pub fn parse(code: Rc<String>) -> Vec<Token> {
    let mut tokens = Vec::new();

    let mut start = 0;
    let mut in_token = false;
    let mut escaped = false;
    let mut token = String::new();

    for (i, mut c) in code.chars().enumerate() {
        if c == '\\' && !escaped {
            escaped = true;
            continue;
        }

        if c.is_whitespace() && !escaped {
            if in_token {
                tokens.push(Token {
                    code: code.clone(),
                    value: token.drain(..).collect(),
                    span: start..i,
                });
            }
            in_token = false;
            continue;
        }

        if escaped && c == 'n' {
            c = '\n';
        }

        if !in_token {
            start = i;
            if escaped {
                start -= 1;
            }
            in_token = true;
        }

        token.push(c);
        escaped = false;
    }

    if !token.is_empty() {
        tokens.push(Token {
            code: code.clone(),
            value: token,
            span: start..code.chars().count(),
        });
    }

    tokens
}
