from sys import exit
import math
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Final, List
import os
import threading
import shutil
from types.playlist import Playlist
from types.song import Song


"""

entry point

"""

class SpotifyDL:
    CLIENT_ID: Final[str] = os.environ.get("CLIENT_ID")
    CLIENT_SECRET: Final[str] = os.environ.get("CLIENT_SECRET")
    MAX_THREADS: int = 32
    PROJECT_DIR: Final[str] = os.path.dirname(os.path.realpath(__file__))

    ccm = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=ccm)

    def __init__(self, link: str):
        self.link: Final[str] = link

        self.playlist: Playlist = None

        if "playlist" in link:
            self.playlist: Playlist = self.get_spotify_playlist()
        elif "album" in link:
            self.playlist: Playlist = self.get_spotify_album()
        else:
            print("Invaild URL, or cannot be downloaded")
            exit(1)

        # playlist paths
        self.playlist_path = self.PROJECT_DIR + f"/out/{self.name.replace(' ', '_')}"
        self.zip_path = self.playlist_path + ".zip"

    def get_spotify_album(self) -> Playlist:
        response = self.sp.album(self.link)
        name: str = response.get("name")
        creator: str = response.get("artists")[0].get("name")
        size: int = response.get("tracks").get("total")

        album: Playlist = Playlist(
            link=self.link,
            name=name,
            creator=creator,
            size=size
        )

        for i in range(math.ceil(self.size / 100)):
            response = self.sp.album_tracks(album_id=self.link, offset=(i * 100))
            for song in response.get("items"):

                # extract title artist and album from api response and append to playlist list
                track: int = song.get("track_number")
                track: int = song.get()
                title: str = song.get("name")
                artist: str = song.get("artists")[0].get(
                    "name"
                )  # TODO there are multiple artists, only takes one atm
                features: List[str] = song.get("artists")[1:]
                features = list(map(lambda f: f.get("name"), features))

                duration: str = song.get("duration_ms")

                album.add(
                    Song(
                        track=track,
                        title=title,
                        artist=artist,
                        features=features,
                        album=self.name,
                        duration=duration,
                    )
                )

        return album

    def get_spotify_playlist(self) -> Playlist:
        # make api call
        response = self.sp.playlist(self.link)

        # get playlist and size
        self.name = response.get("name")
        self.creator = response.get("owner").get("display_name")
        self.size = response.get("tracks").get("total")

        playlist: Playlist = Playlist()

        for i in range(math.ceil(self.size / 100)):
            response = self.sp.playlist_items(
                playlist_id=self.link, limit=100, offset=(i * 100)
            )
            for song in response.get("items"):
                song = song.get("track")

                # extract title artist and album from api response and append to playlist list
                track: int = song.get("track_number")
                title: str = song.get("name")
                artist: str = song.get("artists")[0].get(
                    "name"
                )  # TODO if there are multiple artists, only takes one atm
                features: List[str] = song.get("artists")[1:]
                features = list(map(lambda f: f.get("name"), features))

                album: str = song.get("album").get("name")
                duration: int = round(
                    int(song.get("duration_ms")) / 1000
                )  # from ms to s

                playlist.add(
                    Song(
                        track=track,
                        title=title,
                        artist=artist,
                        features=features,
                        album=album,
                        duration=duration,
                    )
                )

        return playlist

    # split the playlist into sublists for threading
    def split_playlist(self, threads: int) -> List[Playlist]:
        # if the playlist size is smaller the the wanted threads
        if self.size <= threads:
            threads = self.size

        threading_playlists: List[Playlist] = []
        threading_playlists_size: int = round(self.size / threads)

        for i in range(0, self.size, threading_playlists_size):
            sub: List[Song] = self.playlist.playlist[i : i + threading_playlists_size]
            sub: Playlist = Playlist(sub)
            threading_playlists.append(sub)

        return threading_playlists

    # start downloading the playlist
    def download(self, threads: int = 10, fix_missing: bool = False):
        # playlist_path: str = self.PROJECT_DIR + f"/out/{self.name.replace(' ', '_')}"

        # create genric out folder
        try:
            os.mkdir(self.PROJECT_DIR + "/out")
        except FileExistsError:
            pass

        # create playlist folder
        if not fix_missing:
            # remove older playlists from out folder
            try:
                shutil.rmtree(self.playlist_path)
            except FileNotFoundError:
                pass

        # create new playlist folder
        try:
            os.mkdir(self.playlist_path)
        except FileExistsError:
            pass

        # remove old zip folder
        try:
            os.remove(self.zip_path)
        except FileNotFoundError:
            pass

        # max thread count
        if threads > self.MAX_THREADS:
            threads = self.MAX_THREADS

        thread_list = []

        # start all threads
        for thread_playlist in self.split_playlist(threads=threads):
            t = threading.Thread(
                target=thread_playlist.download, args=[self.playlist_path]
            )
            t.start()
            thread_list.append(t)

        # wait until all threads are done
        for thread in thread_list:
            thread.join()

        print("Download complete...")
        print("Compressing folder...")

        # zip folder
        shutil.make_archive(self.playlist_path, "zip", self.playlist_path)

        return self.zip_path
