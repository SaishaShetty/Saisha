# One-time Spotify setup

1. https://developer.spotify.com/dashboard -> Create app.
   Redirect URI: http://127.0.0.1:8888/callback  (Web API)
2. Open this in your browser (replace CLIENT_ID):

   https://accounts.spotify.com/authorize?client_id=CLIENT_ID&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A8888%2Fcallback&scope=user-read-recently-played

3. Approve. You'll land on a dead page; copy the `code=` value from the URL.
4. Exchange it (replace CLIENT_ID, CLIENT_SECRET, CODE):

   curl -X POST https://accounts.spotify.com/api/token \
     -u CLIENT_ID:CLIENT_SECRET \
     -d grant_type=authorization_code \
     -d code=CODE \
     -d redirect_uri=http://127.0.0.1:8888/callback

   Save `refresh_token` from the response.
5. Deploy:

   cd v2/spotify-worker
   npx wrangler deploy
   npx wrangler secret put SPOTIFY_CLIENT_ID
   npx wrangler secret put SPOTIFY_CLIENT_SECRET
   npx wrangler secret put SPOTIFY_REFRESH_TOKEN

6. Put the printed worker URL in `SPOTIFY_API` in v2/main.html.
