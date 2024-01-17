using System;
using System.Numerics;

namespace exoplanet.Crypto.Multiplicators
{
    public interface IMultiplicator
    {
        BigInteger Multiply(BigInteger value);
    }
}
