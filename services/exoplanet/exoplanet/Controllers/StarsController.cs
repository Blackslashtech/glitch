using System;
using System.Linq;
using System.Threading.Tasks;

using Microsoft.AspNetCore.Mvc;

using exoplanet.Authentication;
using exoplanet.Services;
using exoplanet.Models;

namespace exoplanet.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class StarsController : ControllerBase
    {
        private readonly ExoplanetService service;
        private readonly Authenticator authenticator;

        public StarsController(ExoplanetService service, Authenticator authenticator)
        {
            this.service = service;
            this.authenticator = authenticator;
        }

        [HttpGet]
        public async Task<ActionResult> GetLastStars()
        {
            var stars = await service
                .GetLastStarsAsync()
                .ConfigureAwait(false);

            return Ok(stars);
        }

        [HttpGet("{id}", Name = nameof(GetStar))]
        public async Task<ActionResult> GetStar(string id)
        {
            var star = await service
                .GetStarAsync(id)
                .ConfigureAwait(false);

            if (star == null)
                return NotFound(Error.NotFound);

            return Ok(star);
        }

        [HttpPost]
        public async Task<ActionResult> AddStar(Star star)
        {
            star.Planets.Clear();
            
            await service
                .AddStarAsync(star)
                .ConfigureAwait(false);

            var info = TokenInfo.Create(
                star.Id,
                Enumerable.Empty<string>());

            var token = await this.authenticator
                .GenerateTokenAsync(info)
                .ConfigureAwait(false);

            Response.Cookies.Append("token", token);

            return CreatedAtRoute(nameof(GetStar), new { id = star.Id }, star);
        }
    }
}
