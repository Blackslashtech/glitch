using System;
using System.Security.Cryptography;
using System.ComponentModel.DataAnnotations;

using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace exoplanet.Models
{
    public class Secret
    {
        [BsonId]
        [BsonIgnoreIfDefault]
        [BsonRepresentation(BsonType.ObjectId)]
        public string Id { get; set; }

        [Required]
        public string Name { get; set; }

        [Required]
        public string Value { get; set; }

        public static Secret Generate(string name, int length)
        {
            var bytes = new byte[length];

            RandomNumberGenerator.Fill(bytes);

            return new Secret()
            {
                Name = name,
                Value = Convert.ToBase64String(bytes)
            };
        }
    }
}
