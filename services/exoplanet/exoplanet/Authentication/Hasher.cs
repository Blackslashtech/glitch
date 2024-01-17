using System;
using System.Text;
using System.Security.Cryptography;

namespace exoplanet.Authentication
{
    public static class Hasher
    {
        public static string Hash(string data)
        {
            using (var md5 = MD5.Create())
            {
                var bytes = Encoding.UTF8.GetBytes(data);
                var hash = md5.ComputeHash(bytes);

                return BitConverter
                    .ToString(hash)
                    .Replace("-", string.Empty)
                    .ToLower();
            }
        }
    }
}
