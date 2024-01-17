using System;
using System.Linq;
using System.Numerics;

using exoplanet.Crypto.Transformers;

namespace exoplanet.Crypto.Multiplicators
{
    public class Multiplicator : IMultiplicator
    {
        private readonly BigInteger[,] table;

        public Multiplicator(ITransformer transformer)
        {
            var key = transformer.Transform(new byte[transformer.BlockSize]);
            var initial = new BigInteger(key, true, true);

            this.table = BuildTable(initial);
        }

        public BigInteger Multiply(BigInteger value)
        {
            var parts = value.ToByteArray(true, false);
            
            return parts
                .Select((part, i) => this.table[i, part])
                .Aggregate(
                    BigInteger.Zero,
                    (x, y) => x ^ y);
        }

        private BigInteger MultiplyRaw(BigInteger value1, BigInteger value2)
        {
            var result = BigInteger.Zero;
            
            for (var i = 0; i < 128; i++)
            {
                result ^= value1 * ((value2 >> (127 - i)) & 1);
                value1 = (value1 >> 1) ^ (((value1 & 1) * 225) << 120);
            }

            return result;
        }

        private BigInteger[,] BuildTable(BigInteger initial)
        {
            var table = new BigInteger[16, 256];

            for (var i = 0; i < table.GetLength(0); i++)
            {
                for (var k = 0; k < table.GetLength(1); k++)
                {
                    var value = new BigInteger(k) << (8 * i);
                    table[i, k] = MultiplyRaw(initial, value);
                }
            }

            return table;
        }
    }
}
