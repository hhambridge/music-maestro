# Music Maestro

![](https://ssl-static.libsyn.com/p/assets/8/a/8/e/8a8e306b1e765ebd/Maestro_Pic.jpg)

This repository allows you to access your Spotify library programmatically, enabling systematic organization of your music into playlists, all through the power of data science. If you are looking for a no code option, check out [Organize Your Music](http://organizeyourmusic.playlistmachinery.com/). If you want to create customized mood playlists, see [Playlist Generator](https://www.playlist-generator.com/), though note this will frequently include music from outside your library.

## Quick Start
1. Clone this repo.
2. Update the `parameters.json` file with your Spotify username.
3. Go to [Spotify for Developers](https://developer.spotify.com/dashboard).
   1. Click "Create app".
   2. Complete the "App name", "App description", and "Website" fields.
   3. For "Redirect URI", enter the URI exactly as it appears in `parameters.json`.
   4. Accept the agreement and click "save".
   5. Copy the "client_id" and "client_secret" into `parameters.json`.
4. Create your conda environment with `environment.yml`.

## Pulling Your Library

After updating the `parameters.json` file, run the following:
```
python retrieve_user_data.py -p parameters.json
```

