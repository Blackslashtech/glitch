using System;
using System.ComponentModel.DataAnnotations;

using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace exoplanet.Models
{
    public enum PlanetType
    {
        Unknown,
        Terrestrial,
        Protoplanet,
        GasGiant
    }
    
    public class Planet
    {
        [BsonId]
        [BsonIgnoreIfDefault]
        [BsonRepresentation(BsonType.ObjectId)]
        public string Id { get; set; }

        [Required]
        public string StarId { get; set; }

        [Required]
        public string Name { get; set; }

        [Required]
        public string Location { get; set; }

        public PlanetType Type { get; set; } = PlanetType.Unknown;

        public bool IsHidden { get; set; } = false;
    }
}
