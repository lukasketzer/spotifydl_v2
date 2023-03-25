# Spotify Downloader V2
Spotify DL is a python-script to download a spotify playlist from youtube-music.
You need to create a spotify client-id and a client-secret on the [spotify dev website](https://developer.spotify.com/dashboard/).


## Host locally 

1. Add your client-id and client-secret to your environment variables

**Linux** and **MacOS**
Add the following lines to your **.bashrc** (or **.zshrc** on MacOS)
```
export CLIENT_ID="your_spotify_client_id"
export CLIENT_SECRET="your_spotify_client_secret"
```
**Windows**:
[follow this tutorial](https://www.howtogeek.com/787217/how-to-edit-environment-variables-on-windows-10-or-11/)

2. Clone the directory:
```
git clone https://github.com/lukasketzer/spotifydl_v2.git && cd spotifydl_v2
```
3. Create a python venv in the source directory and activate it:
```
python -m venv venv
source venv/bin/activate
```
4. Install all depedencies:
```
pip install -r requirements.txt
```
5. Go into the `spotifydl` directory:
```
cd spotifydl
````
6. Download the playlist or album you want
```
python . "playlist_url"
```

