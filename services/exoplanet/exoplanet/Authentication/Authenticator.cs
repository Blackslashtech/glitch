using System;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Generic;

using exoplanet.Crypto.Ciphers;
using exoplanet.Services;
using exoplanet.Models;

namespace exoplanet.Authentication
{
    public class Authenticator
    {
        private readonly ICipher cipher;
        private readonly SecretService service;

        public Authenticator(ICipher cipher, SecretService service)
        {
            this.cipher = cipher;
            this.service = service;
        }

        public async Task<string> GenerateTokenAsync(TokenInfo info)
        {
            var secret = await service
                .GetSecretAsync(info.Owner)
                .ConfigureAwait(false);

            if (secret == null || secret.Value == null)
            {
                secret = Secret.Generate(info.Owner, 9);
                await service.AddSecretAsync(secret);
            }

            var content = JsonSerializer.Serialize(
                info.Content,
                typeof(IEnumerable<string>),
                new JsonSerializerOptions() {
                    IgnoreNullValues = true
                });

            var owner = Encoding.UTF8.GetBytes(info.Owner);
            
            this.cipher.Encrypt(
                Encoding.UTF8.GetBytes(secret.Value),
                Encoding.UTF8.GetBytes(content),
                owner,
                out var checksum,
                out var data);
            
            return Token.Create(data, owner, checksum).ToString();
        }

        public async Task<TokenInfo> ExtractTokenInfoAsync(string token)
        {
            var _token = Token.FromString(token);

            var owner = Encoding.UTF8.GetString(_token.Owner);

            var secret = await service
                .GetSecretAsync(owner)
                .ConfigureAwait(false);

            if (secret == null || secret.Value == null)
                return null;

            if (!this.cipher.TryDecrypt(
                Encoding.UTF8.GetBytes(secret.Value),
                _token.Data,
                _token.Owner,
                _token.Checksum,
                out var data))
                return null;

            var content = JsonSerializer.Deserialize(
                Encoding.UTF8.GetString(data),
                typeof(IEnumerable<string>), 
                new JsonSerializerOptions() {
                    IgnoreNullValues = true
                }) as IEnumerable<string>;

            return TokenInfo.Create(
                owner,
                content ?? Enumerable.Empty<string>());
        }
    }
}
