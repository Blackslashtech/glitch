using System;
using System.Threading.Tasks;
using System.Collections.Generic;

using MongoDB.Bson;
using MongoDB.Driver;

using exoplanet.Models;

namespace exoplanet.Services
{
    public class ExoplanetService
    {
        private const int LastCount = 100;

        private readonly IMongoCollection<Star> stars;
        private readonly IMongoCollection<Planet> planets;

        public ExoplanetService(IDatabaseSettings settings)
        {
            var client = new MongoClient(settings.ConnectionString);
            var database = client.GetDatabase(settings.DatabaseName);

            this.stars = database.GetCollection<Star>(settings.StarsCollectionName);
            this.planets = database.GetCollection<Planet>(settings.PlanetsCollectionName);
        }

        public async Task<List<Star>> GetLastStarsAsync()
        {
            return await stars
                .Find(star => true)
                .Sort(Builders<Star>.Sort.Descending("$natural"))
                .Limit(LastCount)
                .ToListAsync()
                .ConfigureAwait(false);
        }

        public async Task<Star> GetStarAsync(string id)
        {
            if (!ObjectId.TryParse(id, out var objectId))
                return null;

            return await stars
                .Find(star => star.Id == id)
                .FirstOrDefaultAsync()
                .ConfigureAwait(false);
        }

        public async Task<Planet> GetPlanetAsync(string id)
        {
            if (!ObjectId.TryParse(id, out var objectId))
                return null;

            return await planets
                .Find(planet => planet.Id == id)
                .FirstOrDefaultAsync()
                .ConfigureAwait(false);
        }

        public async Task AddStarAsync(Star star)
        {
            star.Id = ObjectId.GenerateNewId().ToString();

            await stars
                .InsertOneAsync(star)
                .ConfigureAwait(false);
        }

        public async Task AddPlanetAsync(Planet planet, Star star)
        {
            planet.Id = ObjectId.GenerateNewId().ToString();
            
            star.Planets.Add(planet.Id);
            planet.StarId = star.Id;

            await planets
                .InsertOneAsync(planet)
                .ConfigureAwait(false);

            await stars
                .ReplaceOneAsync(_star => _star.Id == star.Id, star)
                .ConfigureAwait(false);
        }
    }
}
