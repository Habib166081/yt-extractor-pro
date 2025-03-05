import whisper
import logging

logger = logging.getLogger(__name__)

def load_whisper_model(model_name: str = "base"):
    """
    Charge et renvoie le modèle Whisper.

    Args:
        model_name (str): Nom du modèle (base, small, medium, large).

    Returns:
        Le modèle Whisper ou None en cas d'erreur.
    """
    try:
        # Utilisation explicite du CPU
        model = whisper.load_model(model_name, device="cpu")
        return model
    except Exception as e:
        logger.exception("Erreur lors du chargement du modèle Whisper : %s", e)
        return None

def audio_to_text(audio_path: str, model_name: str = "base") -> str:
    """
    Transcrit l'audio en texte en utilisant le modèle Whisper.

    Args:
        audio_path (str): Chemin vers le fichier audio.
        model_name (str): Nom du modèle Whisper (par défaut 'base').

    Returns:
        str: La transcription ou un message d'erreur.
    """
    model = load_whisper_model(model_name)
    if model is None:
        return "Erreur lors du chargement du modèle de transcription."
    try:
        # Forcer l'utilisation de FP32 en passant fp16=False pour éviter le warning
        result = model.transcribe(audio_path, fp16=False)
        return result.get("text", "")
    except Exception as e:
        logger.exception("Erreur lors de la transcription audio : %s", e)
        return "Erreur lors de la transcription audio."
