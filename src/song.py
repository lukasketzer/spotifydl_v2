from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic
import string
from typing import Final
import os
import subprocess


class Song:
    YT_MUSIC_BASE_URL: Final[str] = "https://youtube.com/watch?v="

    def __init__(self, title: str = "", artist: str = "", album: str = "", duration: str = ""):
        self.title = title
        self.artist = artist
        self.album = album
        self.duration: int = round(int(duration) / 1000) # from ms to s

    def download(self, playlist_path: str):
        yt = YTMusic()
        
        # add trailing / for path
        if playlist_path[-1] != "/":
            playlist_path += "/"

        base_file_name: str = self.clean_string(f"{self.title}_{self.artist}_{self.album}")
        file_name: str = f"{playlist_path}spotifydl_{base_file_name}.m4a"
        base_file_name = playlist_path + base_file_name

        query: str = f"{self.title} {self.artist} {self.album}"

        
        video_id: str = self.get_best_matching_id(yt.search(query=query))

        if video_id == None: # TODO handle video ids which have not been found
            return

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

                print(f"Embedding metadata...")
                subprocess.run(cmd)
                os.remove(f"{base_file_name}.m4a")
            except:
                return

    # get the best matching youtube video / song 
    def get_best_matching_id(self, results) -> str: 
    
        # return None if there are no search results
        if len(results) == 0:
            return None

        matches: list = []

        # iterate over results to get the best matching result 
        for res in results:
            if res["resultType"] not in ["song"]:
                continue

            # add all matchen to a list
            matches.append({
                "videoId": res["videoId"],
                "match": res["duration_seconds"] / self.duration
                })
        # get the closest match to 100%
        return min(matches, key=lambda x: abs(x.get("match") - 1)).get("videoId")

    # method for cleaning up any unwanted symbols in song name, artist name etc.
    # only for file name used not for metadata
    @staticmethod
    def clean_string(_string: str) -> str:
        _string = _string.replace(" ", "")
        for i in string.punctuation:
            _string = _string.replace(i, "")
        return _string


