using System;
using System.Security.Cryptography;

using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

using exoplanet.Crypto.Multiplicators;
using exoplanet.Crypto.Transformers;
using exoplanet.Crypto.Combiners;
using exoplanet.Crypto.Ciphers;
using exoplanet.Authentication;
using exoplanet.Services;
using exoplanet.Models;

namespace exoplanet
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        public void ConfigureServices(IServiceCollection services)
        {
            services.AddSingleton<IDatabaseSettings>(
                Configuration.GetSection(nameof(DatabaseSettings)).Get<DatabaseSettings>());

            services.AddSingleton<SecretService>();
            services.AddSingleton<ExoplanetService>();

            services.AddSingleton<SymmetricAlgorithm>(provider => {
                var service = provider.GetService<SecretService>();
                
                var secret = service.GetSecretAsync("secret")
                    .GetAwaiter().GetResult();

                if (secret == null)
                {
                    secret = Secret.Generate("secret", 16);
                    service.AddSecretAsync(secret)
                        .GetAwaiter().GetResult();
                }

                var alg = SymmetricAlgorithm.Create("AES");
                alg.Key = Convert.FromBase64String(secret.Value);
                alg.Mode = CipherMode.ECB;
                alg.Padding = PaddingMode.Zeros;

                return alg;
            });

            services.AddSingleton<ITransformer, Transformer>();
            services.AddSingleton<IMultiplicator, Multiplicator>();
            services.AddSingleton<ICombiner, Combiner>();
            services.AddSingleton<ICipher, Cipher>();

            services.AddSingleton<Authenticator>();

            services.AddControllers().AddJsonOptions(options => {
                options.JsonSerializerOptions.IgnoreNullValues = true;
            });
        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            app.UseRouting()
;
            app.UseDefaultFiles();
            app.UseStaticFiles();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
            });
        }
    }
}
