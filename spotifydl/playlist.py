from typing import Final, List
from song import Song


class Playlist:
    def __init__(self, playlist: List[Song] = None):
        if playlist is None:
            self.playlist = []
        else:
            self.playlist: List[Song] = playlist

        self.size: int = len(self.playlist)

    def download(self, playlist_path: str):

        # remove duplicate songs
        self.playlist = list(set(self.playlist))

        for song in self.playlist:
            song.download(playlist_path)

    def add(self, song: Song):
        self.playlist.append(song)
