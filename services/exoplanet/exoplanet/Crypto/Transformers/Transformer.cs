using System;
using System.Security.Cryptography;

namespace exoplanet.Crypto.Transformers
{
    public class Transformer : ITransformer
    {
        private readonly ICryptoTransform transformer;

        public int BlockSize { get; }

        public Transformer(SymmetricAlgorithm algorithm)
        {
            this.BlockSize = algorithm.BlockSize / 8;
            this.transformer = algorithm.CreateEncryptor();
        }

        public byte[] Transform(byte[] data) => transformer.TransformFinalBlock(data, 0, data.Length);
    }
}
