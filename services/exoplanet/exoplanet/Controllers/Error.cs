using System;
using System.Text.Json.Serialization;

namespace exoplanet.Controllers
{
    public class Error
    {
        [JsonPropertyName("error")]
        public string Message { get; set; }

        public static Error Create(string error)
        {
            return new Error() {
                Message = error
            };
        }

        public static Error NotFound => Error.Create("not found");
        public static Error NotAllowed => Error.Create("not allowed");
    }    
}
