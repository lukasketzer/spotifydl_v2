import argparse
from spotifydl import SpotifyDL
from time import sleep


def main(args):
    spdl = SpotifyDL(args.link) # TODO different output for album and playlist5
    print(f"Playlist name: {spdl.name}")
    print(f"Creator / Artist: {spdl.creator}")
    print(f"Size: {spdl.size}")
    print("=============================================================")
    # start_download: str = input("Start download [y / N]\n").lower()
    # if start_download == "y" or start_download == "n":
    #     spdl.download(threads=args.thread_count)
    sleep(1)
    spdl.download(threads=args.thread_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("link", help="The link of the spotify playlist or album. The playlist should be public.")
    parser.add_argument("-t", "--thread_count", default=16, help="amout of threads used by the script", type=int)

    args = parser.parse_args()

    main(args)
