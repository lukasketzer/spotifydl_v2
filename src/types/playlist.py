from typing import Final, List
from song import Song


class Playlist:
    def __init__(self, link: str, creator: str, name: str, size: int):
        self.link: Final[str]
        self.creator: str
        self.name: str
        self.size: int

        self.playlist: List[Song] = []

    def download(self, playlist_path: str):
        # remove duplicate songs
        self.playlist = list(set(self.playlist))

        for song in self.playlist:
            song.download(playlist_path)

    def add(self, song: Song):
        self.playlist.append(song)
