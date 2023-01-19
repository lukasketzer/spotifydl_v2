from sys import exit
import math
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Final, List
import os
from playlist import Playlist
from song import Song
import threading


class SpotifyDL:
    CLIENT_ID: Final[str] = os.environ.get("CLIENT_ID")
    CLIENT_SECRET: Final[str] = os.environ.get("CLIENT_SECRET")
    ccm = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=ccm)

    def __init__(self, link: str):
        self.link: Final[str] = link

        # playlist metadata
        self.creator: str = None
        self.name: str = None
        self.size: int = 0
        self.playlist: Playlist = None

        if "playlist" in link:
            self.playlist: Playlist = self.get_spotify_playlist()
        elif "album" in link:
            self.playlist: Playlist = self.get_spotify_album()
        else:
            print("Invaild URL, or cannot be downloaded")
            exit(1)

    def get_spotify_album(self) -> Playlist:
        response = self.sp.album(self.link)
        self.name = response.get("name")
        self.creator = response.get("artists")[0].get("name")
        self.size = response.get("tracks").get("total")

        album: Playlist = Playlist()

        for i in range(math.ceil(self.size / 100)):
            response = self.sp.album_tracks(album_id=self.link, offset=(i * 100))
            for song in response.get("items"):

                # extract title artist and album from api response and append to playlist list
                title: str = song.get("name")
                artist: str = song.get("artists")[0].get("name")  # TODO there are multiple artists, only takes one atm

                album.add(Song(
                    title=title,
                    artist=artist,
                    album=self.name
                ))
        return album

    def get_spotify_playlist(self) -> Playlist:
        # make api call
        response = self.sp.playlist(self.link)

        # get playlist and size
        self.name = response.get("name")
        self.creator = response.get("owner").get("display_name")
        self.size = response.get("tracks").get("total")

        playlist = Playlist()

        for i in range(math.ceil(self.size / 100)):
            response = self.sp.playlist_items(playlist_id=self.link, limit=100, offset=(i * 100))
            for song in response.get("items"):
                song = song.get("track")

                # extract title artist and album from api response and append to playlist list
                title: str = song.get("name")
                artist: str = song.get("artists")[0].get("name")  # TODO there are multiple artists, only takes one atm
                album: str = song.get("album").get("name")

                playlist.add(Song(
                    title=title,
                    artist=artist,
                    album=album
                ))

        return playlist

    def split_playlist(self, threads: int) -> List[Playlist]:
        threading_playlists: List[Playlist] = []
        threading_playlists_size: int = round(self.size / threads)

        for i in range(0, self.size, threading_playlists_size):
            sub: List[Song] = self.playlist.playlist[i:i + threading_playlists_size]
            sub: Playlist = Playlist(sub)
            threading_playlists.append(sub)
        return threading_playlists

    def download(self, threads: int = 1):
        for thread_playlist in self.split_playlist(threads=threads):
            threading.Thread(target=thread_playlist.download).start()
