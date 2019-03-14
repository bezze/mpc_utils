#!/usr/bin/env python3

from io import StringIO
import sys
import os
import json

import youtube_dl
import subprocess as sp


def get_best_audio(metadata):
    """docstring for get_best_audio"""

    # audio_only = {fid: f for fid, f in formats.items() if "mime=audio" in f["url"]}
    audio_only = {fid: f for fid, f in formats.items() if "audio only" in f["format"]}
    best_audio_list = sorted(audio_only.values(), key=lambda v: v["abr"], reverse=True)
    best_audio = best_audio_list[0]

    return best_audio


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
