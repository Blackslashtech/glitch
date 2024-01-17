using System;

namespace exoplanet.Crypto.Ciphers
{
    public interface ICipher
    {
        void Encrypt(
            byte[] key,
            byte[] plaintext,
            byte[] additional, 
            out byte[] checksum,
            out byte[] ciphertext);

        bool TryDecrypt(
            byte[] key,
            byte[] ciphertext,
            byte[] additional,
            byte[] checksum,
            out byte[] plaintext);
    }
}
