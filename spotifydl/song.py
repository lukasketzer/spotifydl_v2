from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic
import string
from typing import Final
import os
import subprocess


class Song:
    """
    The Song class.

    A song object holds the important inforation of a single song.

    A Song object has the download()-Method, which downloads a song from youtube music



    """


    YT_MUSIC_BASE_URL: Final[str] = "https://youtube.com/watch?v="

    def __init__(self, title: str = "", artist: str = "", album: str = "", duration: int = 0):
        """
        Create a Song object, with the given parameters:
        :param str title:       The title of the song
        :param str artist:      The artist of the song
        :param str album:       The album of the song
        :param int duration:    The duration of the song in ms (milliseconds)
        """

        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration
        self.url = self.get_url()

    def download(self, playlist_path: str = ""):
        """
        :param str playlist_path:   A path where the downloaded file is to.
                                    If left empty, the downloaded song is going to be placed in the source directory.

        """

        
        # add trailing / for path
        if playlist_path != "" and playlist_path[-1] != "/": 
            playlist_path += "/"

        base_file_name: str = self.clean_string(f"{self.title}_{self.artist}_{self.album}")
        file_name: str = f"{playlist_path}spotifydl_{base_file_name}.m4a"
        base_file_name = playlist_path + base_file_name

        if self.url == None: # TODO handle video ids which have not been found
            return

        ydl_opts: dict = {"format": "bestaudio[ext=m4a]",           # downloaded audio should be m4a
                          "quiet": "true",
                          "outtmpl": f"{base_file_name}.%(ext)s"    # set output file name
                          }

        # download audio
        with YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"Downloading {self.title} by {self.artist}...")
                ydl.download(self.url)

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



    def get_url(self) -> str: 
        """
        A method that gets search results for the the songs metadata.
        The method returns the song which has the best matching song duration to the spotify song.

        :return: Url of the best matching song.
        """

        yt = YTMusic()

        query: str = f"{self.title} {self.artist} {self.album}"
        
        results = yt.search(query=query, filter="songs")

        # return None if there are no search results
        if len(results) == 0:
            return None

        matches: list = []

        # iterate over results to get the best matching result 
        for res in results:

            # add all matchen to a list
            matches.append({
                "title": res["title"],
                "videoId": res["videoId"],
                "match": res["duration_seconds"] / self.duration
                })

        filtered_matches = [m for m in matches if self.title in m.get("title")]


        # get the closest match to 100%
        if len(filtered_matches) == 0:
            return f'{self.YT_MUSIC_BASE_URL}{min(matches, key=lambda x: abs(x.get("match") - 1)).get("videoId")}'


        return f'{self.YT_MUSIC_BASE_URL}{min(filtered_matches, key=lambda x: abs(x.get("match") - 1)).get("videoId")}'

    @staticmethod
    def clean_string(_string: str) -> str:
        """
        A method for cleaning up any unwanted symbols in song name, artist name etc.
        Only for file name used not for metadata
        :param str _string:     The string that should be cleand of whitespaced and symbols.
        """

        _string = _string.replace(" ", "")
        for i in string.punctuation:
            _string = _string.replace(i, "")
        return _string
