use num::{BigUint, BigInt, FromPrimitive, Zero, bigint::ToBigInt};
use num_primes::Generator;

use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct Key {
    n: BigUint,
    e: BigUint,
    d: BigUint,
}

fn egcd(a: &BigInt, b: &BigInt) -> (BigInt, BigInt, BigInt) {
    let zero = BigInt::zero();
    let one = BigInt::from_i32(1).unwrap();
    let (mut a, mut b) = (a.clone(), b.clone());
    let (mut x0, mut x1, mut y0, mut y1) = (one.clone(), zero.clone(), zero.clone(), one.clone());
    let mut q;
    while !a.cmp(&zero).is_eq() && !b.cmp(&zero).is_eq() {
        (q, a, b) = (&a / &b, b.clone(), &a % &b);
        (x0, x1) = (x1.clone(), &x0 - &q * &x1);
        (y0, y1) = (y1.clone(), &y0 - &q * &y1);
    }
    (a, x0, y0)
}

fn modinv(n: &BigUint, p: &BigUint) -> BigUint {
    let n = n.to_bigint().unwrap();
    let p = p.to_bigint().unwrap();
    let (_, kn, _) = egcd(&n, &p);
    ((kn % p.clone() + p.clone()) % p.clone()).to_biguint().unwrap()
}

fn new_prime(bits: usize) -> BigUint {
    BigUint::from_bytes_le(&Generator::new_prime(bits).to_bytes_le())
}

impl Key {
    pub fn random_key() -> Self {
        let p = new_prime(512);
        let q = new_prime(512);
        let n = &p * &q;
        let phi = (p - BigUint::from_i32(1).unwrap()) * (q - BigUint::from_i32(1).unwrap());

        let e = BigUint::from_i32(31337).unwrap();
        let d = modinv(&e, &phi);
        Self {
            n,
            e,
            d,
        }

    }

    pub fn encrypt(&self, bytes: &[u8]) -> Vec<u8> {
        BigUint::from_bytes_le(bytes).modpow(&self.e, &self.n).to_bytes_le()
    }

    pub fn decrypt(&self, bytes: &[u8]) -> Vec<u8> {
        BigUint::from_bytes_le(bytes).modpow(&self.d, &self.n).to_bytes_le()
    }
}
