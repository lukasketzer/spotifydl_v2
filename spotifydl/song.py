from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic
import string
from typing import Final, List
import os
import subprocess
import mutagen.mp4


class Song:
    """
    The Song class.

    A song object holds the important inforation of a single song.

    A Song object has the download()-Method, which downloads a song from youtube music



    """


    YT_MUSIC_BASE_URL: Final[str] = "https://youtube.com/watch?v="

    def __init__(self, title: str = "", artist: str = "", features: List[str] = [] ,album: str = "", duration: int = 0):
        """
        Create a Song object, with the given parameters:
        :param str title:       The title of the song
        :param str artist:      The artist of the song
        :param str album:       The album of the song
        :param int duration:    The duration of the song in ms (milliseconds)
        """

        self.title = title
        self.artist = artist
        self.features = features
        self.album = album
        self.duration = duration

    def __str__(self):
        return f"{self.title} by {self.artist}, {', '.join(self.features)}"

    def download(self, playlist_path: str = ""):
        """
        :param str playlist_path:   A path where the downloaded file is to.
                                    If left empty, the downloaded song is going to be placed in the source directory.

        """

        file_ext: str = "m4a" 
        # add trailing / for path
        if playlist_path != "" and playlist_path[-1] != "/": 
            playlist_path += "/"

        base_file_name: str = "spotifydl_" + self.clean_string(f"{self.title}_{self.artist}_{self.album}")
        base_file_name = playlist_path + base_file_name

        file_path: str = f"{base_file_name}.{file_ext}"

        if os.path.exists(file_path):
            print(f"Skipping {self.title} by {self.artist}")
            return



        url = self.get_url()

        if url == None: # TODO handle video ids which have not been found
            return

        ydl_opts: dict = {"format": f"bestaudio[ext={file_ext}]",           # downloaded audio should be m4a
                          "quiet": "true",
                          "outtmpl": f"{base_file_name}.%(ext)s"    # set output file name
                          }

        # download audio
        with YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"Downloading {self.title} by {self.artist}...")
                ydl.download(url)
 
                file = mutagen.mp4.MP4(file_path)
                file["©nam"] = self.title
                file["©ART"] = self.artist
                file["©alb"] = self.album

                print(f"\nEmbedding metadata...")
                file.save()
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
            try:
                matches.append({
                    "title": res["title"],
                    "artist": res["artists"][0]["name"],
                    "videoId": res["videoId"],
                    "match": res["duration_seconds"] / self.duration
                    })

            except KeyError:
                continue
            except ZeroDivisionError:
                continue

        # filter out wrong artists
        filtered_matches = [m for m in matches if self.artist in m.get("artist")]

        filtered_matches = [m for m in filtered_matches if self.title in m.get("title")]


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

