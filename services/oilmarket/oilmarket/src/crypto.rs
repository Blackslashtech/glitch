mod hash;
mod rsa;

use std::vec::Vec;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct Key {
    key: rsa::Key,
}

impl Key {
    pub fn random_key() -> Self {
        Self {
            key: rsa::Key::random_key(),
        }
    }

    pub fn sign(&self, data: &[u8]) -> Vec<u8> {
        let mut hasher = hash::Hash::new();
        hasher.update(data);
        self.key.decrypt(&hasher.digest())
    }

    pub fn verify(&self, signature: &[u8], data: &[u8]) -> bool {
        let mut hasher = hash::Hash::new();
        hasher.update(data);
        let digest = hasher.digest();
        self.key.decrypt(&digest) == signature

    }
}
