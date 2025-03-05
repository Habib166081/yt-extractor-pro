import os
from pathlib import Path
import streamlit as st
from src.youtube_utils import get_youtube_video_id, get_video_transcript, download_audio
from src.speech_to_text import audio_to_text
from src.utils import ensure_data_folder

# Configuration de la page
st.set_page_config(page_title="YT Extractor Pro", layout="wide", page_icon="🎥")

# CSS MODERNISÉ & UNIQUE - TEXTES CORRIGÉS POUR LE SELECTEUR DE LANGUE
custom_css = """
<style>
/* Importation de Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&display=swap');

/* Animation du fond en dégradé */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

html, body {
    margin: 0;
    padding: 0;
    min-height: 100vh;
    font-family: 'Montserrat', sans-serif;
    background: linear-gradient(-45deg, #3b3b98, #eb4d4b, #f9ca24, #6ab04c);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: #fff;
}

/* Barre latérale modernisée avec effet glass */
[data-testid="stSidebar"] {
    background: rgba(20, 20, 20, 0.8);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}
/* Forcer la couleur blanche pour la majorité des éléments de la sidebar */
[data-testid="stSidebar"] * {
    color: #fff !important;
}
/* Pour les champs de saisie dans la sidebar, forcer fond blanc et texte noir */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    color: #000 !important;
    background-color: #fff !important;
}
/* Pour les sélecteurs (select) dans la sidebar */
[data-testid="stSidebar"] select {
    color: #000 !important;
    background-color: #fff !important;
}
/* Pour les options du sélecteur */
[data-testid="stSidebar"] select option {
    color: #000 !important;
    background-color: #fff !important;
}
/* Cibler également le composant BaseWeb utilisé par Streamlit pour les selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] {
    color: #000 !important;
    background-color: #fff !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #000 !important;
    background-color: #fff !important;
}

[data-testid="stSidebar"] .css-1d391kg {
    background-color: transparent;
}

/* Titres, labels et textes */
h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    text-align: center;
    animation: fadeInDown 1s ease-out;
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}
h2, label {
    font-weight: 600 !important;
    font-size: 1rem !important;
}

/* Espacement et uniformisation des composants */
.stTextInput, .stSelectbox, .stRadio {
    margin-bottom: 15px !important;
}

/* Style des options radio */
.stRadio label, div[data-baseweb="radio"] > div {
    font-size: 1rem;
    font-weight: 500;
}

/* Conteneur principal avec effet glass */
.content-box {
    background: rgba(255, 255, 255, 0.1);
    padding: 2rem;
    border-radius: 1rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    margin-bottom: 2rem;
}

/* Styles pour les inputs et textareas hors sidebar */
input, select, textarea {
    background: rgba(255, 255, 255, 0.2) !important;
    color: #000 !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    padding: 0.75rem;
    border-radius: 0.5rem;
    transition: border 0.3s ease, box-shadow 0.3s ease;
}
input:focus, select:focus, textarea:focus {
    border-color: #f9ca24 !important;
    box-shadow: 0 0 8px rgba(249, 202, 36, 0.5);
}

/* Placeholder */
::placeholder {
    color: #ddd !important;
    opacity: 1;
}

/* Boutons modernisés avec effet de survol */
.stButton > button {
    background: linear-gradient(45deg, #eb4d4b, #f9ca24);
    border: none;
    border-radius: 0.5rem;
    padding: 0.75rem 1.5rem;
    color: #fff;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 10px rgba(249, 202, 36, 0.8);
}

/* Pied de page épuré */
footer {
    text-align: center;
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 2rem;
}
footer a {
    color: #f9ca24;
    text-decoration: none;
    font-weight: 600;
}
footer a:hover {
    text-decoration: underline;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# **TITRE & DESCRIPTION**
st.markdown("<h1>🎥 YT Extractor Pro</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>L'outil ultime pour extraire, télécharger et transcrire les vidéos YouTube en un clic.</p>",
    unsafe_allow_html=True
)

# **BARRE LATÉRALE - CONFIGURATION**
with st.sidebar:
    st.markdown("<h2>⚙️ Configuration</h2>", unsafe_allow_html=True)

    # URL de la vidéo
    video_url = st.text_input("🔗 Entrez l'URL de la vidéo YouTube",
                              placeholder="https://www.youtube.com/watch?v=...",
                              label_visibility="hidden")

    # Options principales
    st.markdown("<label>🛠 Choisissez une option :</label>", unsafe_allow_html=True)
    extraction_option = st.radio(
        "Sélectionnez un mode d'extraction",
        ("📜 Sous-titres (texte)", "🎙 Transcription audio", "🎵 Audio uniquement"),
        index=0,
        label_visibility="hidden"
    )

    # Options spécifiques
    if extraction_option == "📜 Sous-titres (texte)":
        lang_options = {"Français": "fr", "Anglais": "en", "Espagnol": "es", "Allemand": "de", "Italien": "it"}
        lang_choice = st.selectbox("🌍 Langue des sous-titres :", list(lang_options.keys()), index=0, label_visibility="visible")
        selected_language = lang_options[lang_choice]
    elif extraction_option == "🎙 Transcription audio":
        model_choice = st.selectbox("🧠 Modèle Whisper :", ["base", "small", "medium", "large"], index=0, label_visibility="hidden")

    st.markdown("---")
    run_extraction = st.button("🚀 Lancer l'extraction")

# **TRAITEMENT PRINCIPAL**
if video_url and run_extraction:
    ensure_data_folder()
    video_id = get_youtube_video_id(video_url)

    if not video_id:
        st.error("❌ URL invalide. Vérifiez l'URL fournie.")
    else:
        st.success(f"✅ Vidéo détectée : {video_id}")

        if extraction_option == "📜 Sous-titres (texte)":
            with st.spinner("📜 Récupération des sous-titres..."):
                transcript = get_video_transcript(video_id, language=selected_language)
            if transcript:
                st.success("✅ Sous-titres récupérés avec succès !")
                st.text_area("📝 Sous-titres :", transcript, height=300)
            else:
                st.error(f"❌ Aucun sous-titre disponible en {selected_language}.")

        elif extraction_option == "🎙 Transcription audio":
            with st.spinner("🎙 Téléchargement de l'audio..."):
                audio_file_path = download_audio(video_url)
            if audio_file_path and audio_file_path.exists():
                with st.spinner("🔍 Transcription en cours..."):
                    transcription = audio_to_text(str(audio_file_path), model_name=model_choice)
                st.success("✅ Transcription terminée !")
                st.text_area("📝 Transcription audio :", transcription, height=300)
                os.remove(audio_file_path)
            else:
                st.error("🚨 Échec du téléchargement audio.")

        elif extraction_option == "🎵 Audio uniquement":
            with st.spinner("🎵 Téléchargement de l'audio..."):
                audio_file_path = download_audio(video_url)
            if audio_file_path and audio_file_path.exists():
                st.success("✅ Audio téléchargé avec succès !")
                with open(audio_file_path, "rb") as audio_file:
                    st.download_button("⬇️ Télécharger l'audio", data=audio_file, file_name=audio_file_path.name,
                                       mime="audio/mp3")
                os.remove(audio_file_path)
            else:
                st.error("🚨 Échec du téléchargement audio.")

# **PIED DE PAGE PROFESSIONNEL**
footer_html = """
<footer>
  <p>Réalisé par <a href="https://www.linkedin.com/in/habib-boukrana-755479175/" target="_blank">Habib Boukrana</a> | 
  <a href="https://www.habib-boukrana.com/" target="_blank">Portfolio</a></p>
</footer>
"""
st.markdown(footer_html, unsafe_allow_html=True)
