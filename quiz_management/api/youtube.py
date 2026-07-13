import os

import yt_dlp
from django.conf import settings

MEDIA_DIR = settings.BASE_DIR / "media/temp"
path = str(MEDIA_DIR / "%(id)s.%(ext)s")


def download_audio(url):
    """Lädt die Audiospur eines YouTube-Videos herunter und gibt den
    Dateipfad zurück.

    returns:
        str: Der Datei-Pfad zur heruntergeladenen Audiodatei.
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
    """Löscht die temporäre Audiodatei.

    args:
        path (str): Der Datei-Pfad zur temporären Audiodatei.
    """
    if os.path.exists(path):
        os.remove(path)
        print(f"Temporäre Datei {path} wurde gelöscht.")
