use std::vec::Vec;

const CONSTANTS: [u32; 64] = [ 
    2320580733, 1787337053, 4251985396, 2807377974, 1218319809, 4123899979,
    3237985526, 624917886, 3913274677, 3603784776, 19008228, 3624325155,
    3897454249, 587281880, 3262834740, 4113116148, 1181817537, 2836038666,
    4246454000, 1752699109, 2352479259, 4294799046, 2288500396, 1821834964,
    4257183660, 2778497332, 1254726629, 4134360714, 3212882625, 662504932,
    3928788511, 3582962050, 57023195, 3644581578, 3881328466, 549599862,
    3287428321, 4102010066, 1145222674, 2864477163, 4240589907, 1717923846,
    2384193475, 4294294311, 2256240761, 1856190139, 4262048386, 2749399002,
    1291035144, 4144497534, 3187528003, 700040073, 3943994535, 3561858610,
    95033694, 3664552458, 3864898592, 511874784, 3311764340, 4090582603,
    1108538085, 2892691235, 4234393575, 1683013989
];


pub struct Hash {
    values: [u32; 4],
    buffer: Vec<u8>,
}

impl Hash {
    pub fn new() -> Self {
        Self {
            values: [
                0x47a8925b,
                0xc3efcbbd,
                0x8f2ce0f5,
                0xb451eaa5
            ],
            buffer: Vec::new(),
        }
    }

    pub fn update(&mut self, bytes: &[u8]) {
        self.buffer.extend_from_slice(bytes)
    }

    fn pad(&mut self) {
        let buffer_len: u64 = (self.buffer.len() as u64).wrapping_mul(8);
        self.buffer.push(0x80);
        while self.buffer.len() % 64 != 56 {
            self.buffer.push(0);
        }

        self.buffer.extend_from_slice(&buffer_len.to_le_bytes());
    }

    pub fn digest_values(mut self) -> [u32; 4] {
        self.pad();

        for i in 0..(self.buffer.len() / 64) {
            unsafe {
                self.values = Self::hash_block(self.values, &self.buffer[i * 64 .. i * 64 + 64]);
            }
        }

        self.values

    }
    pub fn digest(self) -> Vec<u8> {
        self.digest_values().iter().fold(Vec::new(), |mut res, value| {
            res.extend_from_slice(&value.to_le_bytes());
            res
        })
    }

    unsafe fn hash_block(values: [u32; 4], block: &[u8]) -> [u32; 4] {
        let (mut a, mut b, mut c, mut d) = (values[0], values[1], values[2], values[3]); 
        for (i, constant) in CONSTANTS.iter().enumerate() {
            let f: u32;
            let index: usize;
            if (0..16).contains(&i) {
                f = (c & b) | (!c & d);
                index = i;
            } else if (16..32).contains(&i) {
                f = (d & b) | (!d & c);
                index = (5 * i + 7) % 16;
            } else if (32..48).contains(&i) {
                f = b ^ c ^ d;
                index = (3 * i + 5) % 16;
            } else {
                f = b ^ (c | !d);
                index = (7 * i) % 16;

            }
            let new_b = a.
                wrapping_add(f)
                .wrapping_add(*constant)
                .wrapping_add(u32::from_le_bytes(block[index * 4..index * 4 + 4].try_into().unwrap()));

            (a, b, c, d) = (d, new_b, b, c);
        }

        values.into_iter().zip([a, b, c, d]).map(|(a, b)| a.wrapping_add(b)).collect::<Vec<u32>>().try_into().unwrap()
    }
}
