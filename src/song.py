from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic
import string
from typing import Final
import os
import subprocess


class Song:
    YT_MUSIC_BASE_URL: Final[str] = "https://youtube.com/watch?v="

    def __init__(self, title: str = "", artist: str = "", album: str = ""):
        self.title = title
        self.artist = artist
        self.album = album

    def download(self):
        yt = YTMusic()

        base_file_name: str = self.clean_string(f"{self.title}_{self.artist}_{self.album}")
        file_name: str = f"spotifydl_{base_file_name}.m4a"

        query: str = f"{self.title} {self.artist} {self.album}"

        video_id: str = yt.search(query=query, filter="songs")[0].get("videoId")    # get first search result
        video_url: str = f"{self.YT_MUSIC_BASE_URL}{video_id}"

        ydl_opts: dict = {"format": "bestaudio[ext=m4a]",           # downloaded audio should be m4a
                          "quiet": "true",
                          "outtmpl": f"{base_file_name}.%(ext)s"    # set output file name
                          }

        # download audio
        with YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"Downloading {self.title} by {self.artist}...")
                ydl.download(video_url)

                cmd = ["ffmpeg", "-i", f"{base_file_name}.m4a",
                       "-metadata", f"title={self.title}",
                       "-metadata", f"artist={self.artist}",
                       "-metadata", f"album={self.album}",
                       file_name]

                print(f"Embedding metadata")
                subprocess.run(cmd)
                os.remove(f"{base_file_name}.m4a")
            except:
                return

    # method for cleaning up any unwanted symbols in song name, artist name etc.
    # only for file name used not for metadata
    @staticmethod
    def clean_string(_string: str) -> str:
        _string = _string.replace(" ", "")
        for i in string.punctuation:
            _string = _string.replace(i, "")
        return _string


