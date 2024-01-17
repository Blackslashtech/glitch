using System;

namespace exoplanet.Crypto.Transformers
{
    public interface ITransformer
    {
        int BlockSize { get; } 
        byte[] Transform(byte[] data);  
    }
}
