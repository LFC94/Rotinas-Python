import os

import yt_dlp as youtube_dl

from src.util.uteis import menuTelas


def downloadMP3():
    playlist_url = input("\nURL Playlist=>")

    download_directory = 'C:/Users/dev/Downloads/playlist'
    start_video_index = 1
    cookies_path = 'C:/Users/dev/Downloads/cookies.txt'

    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(download_directory, '%(title)s.%(ext)s'),
        'noplaylist': False,
        'ffmpeg_location': 'C:/Program Files/ffmpeg-7.0.1/bin',
        'cookiefile': cookies_path,
        'playliststart': start_video_index,   # Sua senha do YouTube
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])


def inicio():
    MENU = {'1': {'title': 'Download MP3', 'function': downloadMP3}}

    menuTelas(MENU)
