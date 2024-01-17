using System;
using System.Threading.Tasks;

using MongoDB.Driver;

using exoplanet.Models;

namespace exoplanet.Services
{
    public class SecretService
    {
        private readonly IMongoCollection<Secret> secrets;

        public SecretService(IDatabaseSettings settings)
        {
            var client = new MongoClient(settings.ConnectionString);
            var database = client.GetDatabase(settings.DatabaseName);

            this.secrets = database.GetCollection<Secret>(settings.SecretsCollectionName);
        }

        public async Task<Secret> GetSecretAsync(string name)
        {
            return await secrets
                .Find(secret => secret.Name == name)
                .FirstOrDefaultAsync()
                .ConfigureAwait(false);
        }

        public async Task AddSecretAsync(Secret secret)
        {
            var options = new ReplaceOptions();
            options.IsUpsert = true;

            await secrets.ReplaceOneAsync(
                _secret => _secret.Name == secret.Name, 
                secret, 
                options
            ).ConfigureAwait(false);
        }
    }
}
