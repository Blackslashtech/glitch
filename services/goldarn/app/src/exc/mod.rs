use self::context::Context;

pub mod context;

pub fn create_context() -> Context {
    Context::default()
}
