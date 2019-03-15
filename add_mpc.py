#!/usr/bin/env python3

from io import StringIO
import sys
import os
import json
import subprocess as sp

import youtube_dl


def get_best_audio(metadata):
    """docstring for get_best_audio"""

    # audio_only = {fid: f for fid, f in formats.items() if "mime=audio" in f["url"]}
    audio_only = {fid: f for fid, f in formats.items() if "audio" in f["format_note"]}
    best_audio_list = sorted(audio_only.values(), key=lambda v: v["abr"], reverse=True)
    best_audio = best_audio_list[0]

    return best_audio


class Playlist():
    def __init__(self, file_path, stream_url):
        self.file_path = file_path
        self.stream_url = stream_url
        self.author = ""
        self.title = ""
        self.duration = 0

    def author(self, name):
        self.author = name

    def title(self, name):
        self.title = name

    def duration(self, length):
        self.duration = length

    def write(self):
        with open(self.file_path) as pl_file:
            pl_file.write("#EXTM3U\n")
            pl_file.write(f"#EXTINF:{self.duration},{self.author} - {self.title}\n")
            pl_file.write(f"{self.stream_url}")


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


try:
    with Capturing() as output:
        youtube_dl._real_main(
            ["-j", sys.argv[1]]
        )
except SystemExit:
    pass

metadata = json.loads(output[0])

title = metadata["title"]
formats = {f["format_id"]: f for f in metadata["formats"]}
best_audio = get_best_audio(metadata)

url = best_audio["url"]
# song_format =
# sp.run("mpc -f {song_format} add {url}")

cmd = ["/usr/bin/mpc"]
# host = "192.168.1.4"
# port = "6603""-h", f"{host}", "-p", f"{port}",
cmd += ["add", f"{url}"]

sp.run(cmd)
