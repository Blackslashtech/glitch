using System;

namespace exoplanet.Authentication
{
    public class Token
    {
        public byte[] Data { get; private set; } = new byte[0];
        public byte[] Owner { get; private set; } = new byte[0];
        public byte[] Checksum { get; private set; } = new byte[0];

        public static Token Create(byte[] data, byte[] owner, byte[] checksum)
        {
            return new Token() { 
                Data = data,
                Owner = owner,
                Checksum = checksum
            };
        }

        public override string ToString()
        {
            var bytes = new byte[
                3 * sizeof(int) + 
                Data.Length +
                Owner.Length +  
                Checksum.Length];

            BitConverter.GetBytes(Data.Length).CopyTo(bytes, 0);
            BitConverter.GetBytes(Owner.Length).CopyTo(bytes, sizeof(int));
            BitConverter.GetBytes(Checksum.Length).CopyTo(bytes, 2 * sizeof(int));
            
            Data.CopyTo(bytes, 3 * sizeof(int));
            Owner.CopyTo(bytes, 3 * sizeof(int) + Data.Length);
            Checksum.CopyTo(bytes, 3 * sizeof(int) + Data.Length + Owner.Length);

            return Convert.ToBase64String(bytes);
        }

        public static Token FromString(string token)
        {
            var bytes = Convert.FromBase64String(token);

            var dataLength = BitConverter.ToInt32(bytes, 0);
            var ownerLength = BitConverter.ToInt32(bytes, sizeof(int));
            var checksumLength = BitConverter.ToInt32(bytes, 2 * sizeof(int));

            var data = new byte[dataLength];
            var owner = new byte[ownerLength];
            var checksum = new byte[checksumLength];

            Array.Copy(bytes, 3 * sizeof(int), data, 0, dataLength);
            Array.Copy(bytes, 3 * sizeof(int) + dataLength, owner, 0, ownerLength);
            Array.Copy(bytes, 3 * sizeof(int) + dataLength + ownerLength, checksum, 0, checksumLength);

            return Token.Create(data, owner, checksum);
        }
    }
}
