#!/usr/bin/env python3

from io import StringIO
import sys
import re
import os
import json
import subprocess as sp

import youtube_dl

MPD_PLAYLISTS = os.environ.get("MPD_PLAYLISTS", ".local/lib/mpd/playlists")
HOME = os.environ.get("HOME")
MPD_HOST = os.environ.get("MPD_HOST", "127.0.0.1")
MPD_PORT = os.environ.get("MPD_PORT", "6600")


def get_best_audio(metadata):
    """docstring for get_best_audio"""

    formats = {f["format_id"]: f for f in metadata["formats"]}
    audio_only = {
        fid: f for fid,
        f in formats.items() if f["vcodec"] == "none" and "abr" in f}
    print(audio_only)
    best_audio_list = sorted(
        audio_only.values(),
        key=lambda v: v["abr"],
        reverse=True)
    print(best_audio_list)
    best_audio = best_audio_list[0]

    return best_audio


class Playlist():
    def __init__(self, file_path, stream_url, author="", title="", duration=0):
        self.file_path = file_path
        self.stream_url = stream_url
        self.author = author
        self.title = title
        self.duration = float(duration)

    def set_author(self, name):
        self.author = name

    def set_title(self, name):
        self.title = name

    def set_duration(self, length):
        self.duration = float(length)

    def write(self):
        with open(self.file_path, "w") as pl_file:
            pl_file.write("#EXTM3U\n")
            pl_file.write(
                f"#EXTINF:{self.duration:.0f},{self.title} {self.author}\n")
            pl_file.write(f"{self.stream_url}\n")


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


def get_json():
    """docstring for get_json"""

    try:
        with Capturing() as output:
            youtube_dl._real_main(
                ["-j", sys.argv[1]]
            )
    except SystemExit:
        pass
    metadata = json.loads(output[0])

    # with open("example.json") as f:
    #     metadata = json.load(f)

    return metadata


def get_duration(audio):
    """docstring for get_duration"""

    url = audio["url"]
    dur_regex = re.compile("dur=(\d*\.\d*)")
    match = dur_regex.search(url)
    if match:
        duration = match.group(1)
    else:
        duration = 0

    return duration


def main():

    metadata = get_json()
    best_audio = get_best_audio(metadata)
    url = best_audio["url"]
    duration = get_duration(best_audio)

    pl = Playlist(os.path.join(HOME, MPD_PLAYLISTS, "stream_pl.m3u"), url,
                  title=metadata["title"],
                  duration=duration
                  )

    pl.write()

    cmd = ["/usr/bin/mpc", f"--host={MPD_HOST}", f"--port={MPD_PORT}"]
    cmd += ["load", "stream_pl"]
    sp.run(cmd)

    cmd = ["/usr/bin/mpc", f"--host={MPD_HOST}", f"--port={MPD_PORT}"]
    cmd += ["rm", "stream_pl"]
    sp.run(cmd)


if __name__ == '__main__':
    main()
