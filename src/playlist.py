from typing import Final, List
from song import Song


class Playlist:
    def __init__(self, playlist: List[Song] = None):
        if playlist is None:
            self.playlist = []
        else:
            self.playlist: List[Song] = playlist

        self.size: int = len(self.playlist)

    def download(self):
        for song in self.playlist:
            song.download()

    def add(self, song: Song):
        self.playlist.append(song)
