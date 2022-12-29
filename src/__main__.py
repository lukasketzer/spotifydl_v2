import argparse
from spotifydl import SpotifyDL


def main(args):
    spdl = SpotifyDL(args.playlist_link)
    print(f"Playlist name: {spdl.playlist_name}")
    print(f"Creator: {spdl.creator}")
    print(f"Size: {spdl.size}")
    print("=============================================================")
    start_download: str = input("Start download [y / N]\n").lower()
    if start_download == "y" or start_download == "n":
        spdl.download(threads=args.thread_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("playlist_link", help="The link of the spotify playlist. The playlist should be public.")
    parser.add_argument("-t", "--thread_count", default=5, help="amout of threads used by the script", type=int)

    args = parser.parse_args()

    main(args)
