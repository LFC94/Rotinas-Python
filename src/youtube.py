import os
from pathlib import Path

import yt_dlp as youtube_dl
from rich.progress import (BarColumn, DownloadColumn, Progress, TextColumn,
                           TimeRemainingColumn, TransferSpeedColumn)

from src.util.uteis import MyLogger, menuTelas

# Barra de progresso com Rich
progress_bar = Progress(
    TextColumn("[bold cyan]{task.fields[filename]}", justify="left"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    DownloadColumn(),
    TransferSpeedColumn(),
    TimeRemainingColumn(),
)

# Mapeamento de tarefas ativas
task_mapping = {}


def mostrar_progresso(d):
    status = d['status']
    info = d.get('info_dict', {})
    video_id = info.get('id')
    title = info.get('title', 'Baixando...')
    downloaded = d.get('downloaded_bytes', 0)
    total = d.get('total_bytes') or d.get('total_bytes_estimate')
    if status == 'downloading':
        task_id = task_mapping.get(video_id)
        if not task_id and task_id != 0:
            task_id = progress_bar.add_task(
                "", filename=title, total=total or 1)
            task_mapping[video_id] = task_id

        progress_bar.update(task_id, completed=downloaded)

    elif status == 'finished':
        task_id = task_mapping.get(video_id)
        if task_id or task_id == 0:
            progress_bar.remove_task(task_id)
        task_mapping.pop(video_id, None)
        print(f"✅ Download Finalizado: {d.get('filename')}")
    else:
        print(f"🚩 status: {status}")


def conversao_hook(d):
    status = d['status']
    postprocessor = d['postprocessor']
    info = d.get('info_dict', {})
    video_title = info.get('title')
    video_filepath = info.get('filepath')
    if status == 'started':
        print(f"🎧 {postprocessor}: {video_title}")
    elif status == 'finished':
        print(f"✅ {postprocessor} finalizada: {video_filepath}")

# https://www.youtube.com/playlist?list=PL3oW2tjiIxvStcP4RCwKOGkXP7Toccnj2


def downloadMP3():

    download_directory = Path.home() / "Downloads/playlist"

    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    script_dir = Path(__file__).resolve().parent
    ffmpeg_path = script_dir.parent / "external" / "ffmpeg"
    cookies_path = script_dir.parent / "external" / "cookies.txt"
    playlist_url = input("🎵 Cole o link da playlist: ")

    start_video_index = 1
    ydl_opts = {
        'extract_flat': True,  # Extrai somente os links dos vídeos da playlist
        'quiet': True,
        'playliststart': start_video_index,
        'logger': MyLogger(),
    }

    print(f"🔍 Lendo a playlist: {playlist_url}")

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    if 'entries' in info:
        video_urls = [entry['url'] for entry in info['entries']]
        count_video = len(video_urls)
        print(f"📋 {count_video} vídeos encontrados na playlist.")

        count_download = 0
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl':  str(download_directory / '%(title)s.%(ext)s'),
            'noplaylist': False,
            'ffmpeg_location': str(ffmpeg_path),
            'cookiefile': cookies_path,
            'quiet': True,
            'verbose': False,
            'logger': MyLogger(),
            'progress_hooks': [mostrar_progresso],
            'postprocessor_hooks': [conversao_hook]
        }

        with progress_bar:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                for video_url in video_urls:
                    count_download += 1
                    try:
                        print(f"\n🎵 {count_download}/{count_video} Baixando")
                        ydl.download([video_url])
                    except Exception as e:
                        print(f"⚠️ Erro ao baixar {video_url}: {e}")
                        continue
    else:
        print("❌ A URL fornecida não parece ser uma playlist válida.")


def inicio():
    MENU = {'1': {'title': 'Download MP3', 'function': downloadMP3}}

    menuTelas(MENU)
