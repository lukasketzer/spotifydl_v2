from sys import exit
import math
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Final, List
import os
from .playlist import Playlist
from .song import Song
import threading
import shutil

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
                duration: str = song.get("duration_ms")

                album.add(Song(
                    title=title,
                    artist=artist,
                    album=self.name,
                    duration=duration
                ))

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
            response = self.sp.playlist_items(playlist_id=self.link, limit=100, offset=(i * 100))
            for song in response.get("items"):
                song = song.get("track")

                # extract title artist and album from api response and append to playlist list
                title: str = song.get("name")
                artist: str = song.get("artists")[0].get("name")  # TODO if there are multiple artists, only takes one atm
                album: str = song.get("album").get("name")
                duration: int = round(int(song.get("duration_ms")) / 1000) # from ms to s

                playlist.add(Song(
                    title=title,
                    artist=artist,
                    album=album,
                    duration=duration
                ))

        return playlist
    
    # split the playlist into sublists for threading 
    def split_playlist(self, threads: int) -> List[Playlist]:
        # if the playlist size is smaller the the wanted threads
        if self.size <= threads:
            threads = self.size

        threading_playlists: List[Playlist] = []
        threading_playlists_size: int = round(self.size / threads)

        for i in range(0, self.size, threading_playlists_size):
            sub: List[Song] = self.playlist.playlist[i:i + threading_playlists_size]
            sub: Playlist = Playlist(sub)
            threading_playlists.append(sub)
        return threading_playlists
    
    # start downloading the playlist
    def download(self, threads: int = 1):
        MAX_THREADS = 32 # FIXME: Temporary fix 
        PROJECT_DIR: Final[str] = os.path.dirname(os.path.realpath(__file__))

        playlist_path: str = PROJECT_DIR + f"/out/{self.name.replace(' ', '_')}"

        # create genric out folder 
        try:
            os.mkdir(PROJECT_DIR + "/out")
        except FileExistsError:
            pass
        
        # create playlist folder
        # remove older playlists from out folder
        try:
            shutil.rmtree(playlist_path)
        except FileNotFoundError:
            pass

        try:
            os.remove(f"{playlist_path}.zip")
        except FileNotFoundError:
            pass

        os.mkdir(playlist_path)
       
        # max thread count 
        if threads > MAX_THREADS:
            threads = MAX_THREADS

        thread_list = []

        # start all threads
        for thread_playlist in self.split_playlist(threads=threads):
            t = threading.Thread(target=thread_playlist.download, args=[playlist_path])
            t.start()
            thread_list.append(t)

        # wait until all threads are done
        for thread in thread_list:
            thread.join()

        # zip folder 
        shutil.make_archive(playlist_path, "zip", playlist_path)

        return f"{playlist_path}.zip"

        
