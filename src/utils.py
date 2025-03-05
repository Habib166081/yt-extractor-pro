# src/utils.py
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def ensure_data_folder():
    """
    Vérifie et crée le dossier 'data' s'il n'existe pas.
    """
    data_path = Path("data")
    if not data_path.exists():
        try:
            data_path.mkdir(parents=True, exist_ok=True)
            logger.info("Dossier 'data' créé.")
        except Exception as e:
            logger.exception("Erreur lors de la création du dossier 'data' : %s", e)
