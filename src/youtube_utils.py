# src/youtube_utils.py
import re
import logging
from pathlib import Path
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger(__name__)


def get_youtube_video_id(url: str) -> Optional[str]:
    """
    Extrait l'ID de la vidéo depuis l'URL YouTube.

    Args:
        url (str): URL de la vidéo.

    Returns:
        Optional[str]: L'ID de la vidéo ou None si non trouvé.
    """
    pattern = r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        logger.error("Impossible d'extraire l'ID de la vidéo depuis l'URL fournie.")
        return None


def get_video_transcript(video_id: str, language: str = "fr") -> Optional[str]:
    """
    Récupère les sous-titres de la vidéo dans la langue spécifiée.

    Args:
        video_id (str): ID de la vidéo.
        language (str): Code de langue (par défaut 'fr').

    Returns:
        Optional[str]: La transcription sous forme de texte ou None en cas d'échec.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return "\n".join(entry['text'] for entry in transcript)
    except NoTranscriptFound:
        logger.error(f"Aucun sous-titre trouvé pour la langue '{language}' pour la vidéo {video_id}.")
        return None
    except Exception as e:
        logger.exception("Erreur lors de la récupération des sous-titres : %s", e)
        return None


def download_audio(video_url: str) -> Optional[Path]:
    """
    Télécharge l'audio de la vidéo YouTube et le sauvegarde dans le dossier 'data'
    en utilisant yt-dlp exclusivement.

    Le fichier est nommé selon l'ID de la vidéo (exemple : mv9HwUI2JIA.mp3).

    Args:
        video_url (str): URL de la vidéo YouTube.

    Returns:
        Optional[Path]: Chemin vers le fichier audio ou None en cas d'erreur.
    """
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    import yt_dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(data_dir / "%(id)s.%(ext)s"),  # Nom basé sur l'ID de la vidéo
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    import os
    ffmpeg_location = os.environ.get("FFMPEG_LOCATION")
    if ffmpeg_location:
        ydl_opts['ffmpeg_location'] = ffmpeg_location

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_id = info_dict.get("id", None)
            if video_id:
                output_path = data_dir / f"{video_id}.mp3"
                logger.info("Audio téléchargé avec yt-dlp : %s", output_path)
                return output_path
            else:
                logger.error("Impossible d'extraire l'ID vidéo de info_dict.")
                return None
    except Exception as e:
        logger.exception("Erreur avec yt-dlp : %s", e)
        return None
