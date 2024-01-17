using System;

namespace exoplanet.Models
{
    public interface IDatabaseSettings
    {
        string StarsCollectionName { get; set; }
        string PlanetsCollectionName { get; set; }
        string SecretsCollectionName { get; set; }
        string ConnectionString { get; set; }
        string DatabaseName { get; set; }
    }

    public class DatabaseSettings : IDatabaseSettings
    {
        public string StarsCollectionName { get; set; }
        public string PlanetsCollectionName { get; set; }
        public string SecretsCollectionName { get; set; }
        public string ConnectionString { get; set; }
        public string DatabaseName { get; set; }
    }
}
