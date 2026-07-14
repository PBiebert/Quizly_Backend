import os

import yt_dlp
from django.conf import settings

MEDIA_DIR = settings.BASE_DIR / "media/temp"
path = str(MEDIA_DIR / "%(id)s.%(ext)s")


def download_audio(url):
    """Downloads the audio track of a YouTube video and returns the file path.

    returns:
        str: The file path to the downloaded audio file.
    """

    os.makedirs(MEDIA_DIR, exist_ok=True)

    ydl_opts = {
        "format": "worstaudio/worst",
        "outtmpl": path,
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def delete_temp_audio(path):
    """Deletes the temporary audio file.

    args:
        path (str): The file path to the temporary audio file.
    """

    if os.path.exists(path):
        os.remove(path)
        print(f"Temporary file {path} was deleted.")
