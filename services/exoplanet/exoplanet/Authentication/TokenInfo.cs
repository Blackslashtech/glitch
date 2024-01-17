using System;
using System.Linq;
using System.Collections.Generic;

namespace exoplanet.Authentication
{
    public class TokenInfo
    {
        public string Owner { get; private set; } = string.Empty;
        
        public IEnumerable<string> Content { get; private set; } = Enumerable.Empty<string>();
        
        public static TokenInfo Create(string owner, IEnumerable<string> content)
        {
            return new TokenInfo() { 
                Owner = owner,
                Content = content
            };
        }
    }
}
