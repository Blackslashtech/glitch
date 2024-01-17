using System;
using System.Linq;
using System.Numerics;

using exoplanet.Crypto.Multiplicators;
using exoplanet.Crypto.Transformers;

namespace exoplanet.Crypto.Combiners
{
    public class Combiner : ICombiner
    {
        private readonly ITransformer transformer;
        private readonly IMultiplicator multiplicator;

        public Combiner(
            ITransformer transformer,
            IMultiplicator multiplicator)
        {
            this.transformer = transformer;
            this.multiplicator = multiplicator;
        }

        public byte[] Combine(params byte[][] arrays)
        {
            return arrays
                .Select(array => Utils.Pad(array, this.transformer.BlockSize))
                .SelectMany(array => Utils.Batch(array, this.transformer.BlockSize))
                .Select(part => new BigInteger(part, true, true))
                .Append(
                    arrays
                        .Select(array => new BigInteger(array.Length))
                        .Aggregate((x, y) => 8 * (x << 64 | y)))
                .Aggregate(
                    BigInteger.Zero, 
                    (x, y) => multiplicator.Multiply(x ^ y))
                .ToByteArray(true, true);
        }
    }
}
