using System;
using System.Linq;

using exoplanet.Crypto.Transformers;
using exoplanet.Crypto.Combiners;

namespace exoplanet.Crypto.Ciphers
{
    public class Cipher : ICipher
    {
        private static readonly Func<byte, byte, byte> ByteXor = (x, y) => (byte)(x ^ y);
        
        private readonly ITransformer transformer;
        private readonly ICombiner combiner;

        public Cipher(
            ITransformer transformer,
            ICombiner combiner)
        {
            this.transformer = transformer;
            this.combiner = combiner;
        }

        public void Encrypt(
            byte[] key,
            byte[] plaintext, 
            byte[] additional, 
            out byte[] checksum,
            out byte[] ciphertext)
        {
            ciphertext = Utils
                .CreateCounter(this.transformer.BlockSize, key)
                .Skip(1)
                .SelectMany(this.transformer.Transform)
                .Zip(
                    Utils.Pad(
                        plaintext, 
                        this.transformer.BlockSize), 
                    ByteXor)
                .Take(plaintext.Length)
                .ToArray();

            checksum = GenerateChecksum(key, ciphertext, additional);
        }

        public bool TryDecrypt(
            byte[] key,
            byte[] ciphertext,
            byte[] additional,
            byte[] checksum,
            out byte[] plaintext)
        {
            if (!GenerateChecksum(key, ciphertext, additional).SequenceEqual(checksum))
            {
                plaintext = null;
                return false;
            }

            plaintext = Utils
                .Batch(
                    Utils.Pad(
                        ciphertext, 
                        this.transformer.BlockSize),
                    this.transformer.BlockSize)
                .Zip(
                    Utils
                        .CreateCounter(this.transformer.BlockSize, key)
                        .Select(this.transformer.Transform)
                        .Skip(1),
                    Utils.Xor
                )
                .SelectMany(x => x)
                .Take(ciphertext.Length)
                .ToArray();

            return true;
        }

        private byte[] GenerateChecksum(
            byte[] key, 
            byte[] ciphertext, 
            byte[] additional)
        {
            return Utils
                .CreateCounter(this.transformer.BlockSize, key)
                .SelectMany(this.transformer.Transform)
                .Zip(
                    combiner.Combine(
                        additional,
                        ciphertext),
                    ByteXor)
                .ToArray();
        }
    }
}
