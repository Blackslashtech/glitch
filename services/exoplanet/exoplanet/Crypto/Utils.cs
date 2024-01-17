using System;
using System.Collections.Generic;

namespace exoplanet.Crypto
{
    public static class Utils
    {
        public static T[] Pad<T>(T[] array, int size)
        {
            var length = (size - array.Length % size) % size;
            var result = new T[array.Length + length];

            array.CopyTo(result, 0);

            return result;
        }

        public static IEnumerable<T[]> Batch<T>(T[] array, int size)
        {
            for (var i = 0; i < (array.Length + size - 1) / size; i++)
            {
                var part = new T[size];
                Array.Copy(array, i * size, part, 0, size);

                yield return part;
            }
        }

        public static byte[] Xor(byte[] array1, byte[] array2)
        {
            var result = new byte[Math.Min(array1.Length, array2.Length)];

            for (var i = 0; i < result.Length; i++)
            {
                result[i] = (byte)(array1[i] ^ array2[i]);
            }

            return result;
        }

        public static IEnumerable<byte[]> CreateCounter(int size, byte[] initial = null)
        {
            var counter = new Counter(size, initial);
            return counter.GetEnumerable();
        }

        private class Counter
        {
            private readonly byte[] state;

            public Counter(int size, byte[] initial = null)
            {
                this.state = new byte[Math.Max(size, initial?.Length ?? 0)];

                initial?.CopyTo(state, 0);
            }

            public IEnumerable<byte[]> GetEnumerable()
            {
                while (true)
                {
                    Increment();
                    yield return state.Clone() as byte[];
                }
            }

            private void Increment()
            {
                for (var i = this.state.Length - 1; i >= 0; i--)
                {
                    if (this.state[i] < byte.MaxValue)
                    {
                        this.state[i]++;
                        return;
                    }

                    this.state[i] = 0;
                }
            }
        }
    }
}
