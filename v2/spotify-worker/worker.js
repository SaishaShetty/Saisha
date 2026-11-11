// Cloudflare Worker: returns the last track you played on Spotify.
// Secrets (set with `wrangler secret put`): SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REFRESH_TOKEN
// Optional var: ALLOWED_ORIGIN (e.g. https://yourname.github.io), defaults to *

export default {
  async fetch(request, env) {
    const cors = {
      'Access-Control-Allow-Origin': env.ALLOWED_ORIGIN || '*',
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=30',
    };
    try {
      const tokenRes = await fetch('https://accounts.spotify.com/api/token', {
        method: 'POST',
        headers: {
          Authorization: 'Basic ' + btoa(env.SPOTIFY_CLIENT_ID + ':' + env.SPOTIFY_CLIENT_SECRET),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'refresh_token',
          refresh_token: env.SPOTIFY_REFRESH_TOKEN,
        }),
      });
      const tokenData = await tokenRes.json();
      const access_token = tokenData.access_token;
      if (!access_token) throw new Error('token: ' + (tokenData.error_description || tokenData.error || tokenRes.status));

      const r = await fetch('https://api.spotify.com/v1/me/player/recently-played?limit=1', {
        headers: { Authorization: 'Bearer ' + access_token },
      });
      const data = await r.json();
      if (data.error) throw new Error('spotify: ' + data.error.message);
      const t = data.items && data.items[0] && data.items[0].track;
      if (!t) return new Response(JSON.stringify({ track: null }), { headers: cors });

      return new Response(JSON.stringify({
        track: t.name,
        artist: t.artists.map(a => a.name).join(', '),
        url: t.external_urls && t.external_urls.spotify,
        playedAt: data.items[0].played_at,
      }), { headers: cors });
    } catch (e) {
      return new Response(JSON.stringify({ track: null, reason: String(e.message || e) }), { status: 200, headers: cors });
    }
  },
};
