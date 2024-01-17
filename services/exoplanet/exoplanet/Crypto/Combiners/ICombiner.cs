using System;

namespace exoplanet.Crypto.Combiners
{
    public interface ICombiner
    {
        byte[] Combine(params byte[][] arrays);        
    }
}
