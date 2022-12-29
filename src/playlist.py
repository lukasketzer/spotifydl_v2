import math

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
from typing import Final, List
import os
from song import Song


class Playlist:
    CLIENT_ID: Final[str] = os.environ.get("CLIENT_ID")
    CLIENT_SECRET: Final[str] = os.environ.get("CLIENT_SECRET")

    def __init__(self, playlist_link: str):
        self.playlist_link: Final[str] = playlist_link
        # self.playlist_id: Final[str] = re.findall(r"([A-Za-z0-9]{22})", playlist_link)[0]  # extract playlist id

        # playlist metadata
        self.creator: str = None
        self.playlist_name: str = None
        self.size: int = 0

        self.playlist: List[Song] = self.get_spotify_playlist()

    def get_spotify_playlist(self):
        ccm = SpotifyClientCredentials(client_id=self.CLIENT_ID, client_secret=self.CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=ccm)

        # make api call
        response = sp.playlist(self.playlist_link)

        # get playlist and size
        self.playlist_name = response.get("name")
        self.creator = response.get("owner").get("display_name")
        self.size = response.get("tracks").get("total")

        playlist: List[Song] = []
        tracks = response.get("tracks")

        for i in range(math.ceil(self.size / 100)):
            response = sp.playlist_items(playlist_id=self.playlist_link, limit=100, offset=(i * 100))
            for song in response.get("items"):
                song = song.get("track")

                # extract title artist and album from api response and append to playlist list
                title: str = song.get("name")
                artist: str = song.get("artists")[0].get("name") # TODO there are multiple artists, only takes one atm
                album: str = song.get("album").get("name")

                playlist.append(Song(
                    title=title,
                    artist=artist,
                    album=album
                ))

        return playlist

    def split_playlist(self):
        pass

    def download(self):
        print(f"Playlist name: {self.playlist_name}")
        print(f"Creator: {self.creator}")
        print(f"Size: {self.size}")
        print("=============================================================")
        # temporary
        for song in self.playlist:
            song.download()


if __name__ == '__main__':
    p = Playlist("https://open.spotify.com/playlist/5yPpUAD9d8hTVTvNsxNxAl?si=e143a1e4cc9c4bdb")
    p.download()