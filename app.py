import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
import random

# -------------------------
# 1️⃣ API Keys from Streamlit Secrets
# -------------------------
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

# -------------------------
# 2️⃣ Initialize TMDb
# -------------------------
from tmdbv3api import TMDb, Movie
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
tmdb.language = 'en'
movie_api = Movie()

# -------------------------
# 3️⃣ Initialize Spotify
# -------------------------
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

spotify_auth = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
spotify = spotipy.Spotify(auth_manager=spotify_auth)

# -------------------------
# 4️⃣ Streamlit app config
# -------------------------
st.set_page_config(page_title="Movie Moodboard", layout="wide")
st.title("🎬 Movie Moodboard")

# -------------------------
# 5️⃣ Input scene description & mood
# -------------------------
scene_description = st.text_area("Describe your movie scene:", "")
mood = st.selectbox("Choose a mood:", ["Happy", "Sad", "Suspenseful", "Romantic"])

# -------------------------
# 6️⃣ Mood images fallback
# -------------------------
mood_images = {
    "Happy": ["assets/happy1.jpg", "assets/happy2.jpg"],
    "Sad": ["assets/sad1.jpg", "assets/sad2.jpg"],
    "Romantic": ["assets/romantic1.jpg"],
    "Suspenseful": ["assets/suspense1.jpg"]
}

# -------------------------
# 7️⃣ Display movie poster from TMDb
# -------------------------
if scene_description:
    st.subheader("🎨 Movie Poster / Concept Art")
    poster_displayed = False
    try:
        results = movie_api.search(scene_description)
        if results:
            poster_path = results[0].poster_path
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                response = requests.get(poster_url)
                poster_img = Image.open(BytesIO(response.content))
                st.image(poster_img, caption=f"Poster: {results[0].title}", use_column_width=True)
                poster_displayed = True
    except:
        poster_displayed = False

    # Fallback if no poster
    if not poster_displayed:
        placeholder_path = random.choice(mood_images.get(mood, ["assets/placeholder.jpg"]))
        st.image(Image.open(placeholder_path), caption=f"{mood} Moodboard (placeholder)", use_column_width=True)

# -------------------------
# 8️⃣ AI Concept Art using OpenAI DALL·E
# -------------------------
st.subheader("🖌️ AI Concept Art (OpenAI DALL·E)")
ai_image_displayed = False
try:
    import openai
    openai.api_key = OPENAI_API_KEY
    prompt = f"Concept art for a {mood.lower()} movie scene: {scene_description}"
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    ai_image = Image.open(BytesIO(requests.get(image_url).content))
    st.image(ai_image, caption="AI Concept Art", use_column_width=True)
    ai_image_displayed = True
except:
    ai_image_displayed = False

# Fallback if AI fails
if not ai_image_displayed:
    placeholder_path = random.choice(mood_images.get(mood, ["assets/placeholder.jpg"]))
    st.image(Image.open(placeholder_path), caption=f"{mood} Moodboard (placeholder)", use_column_width=True)

# -------------------------
# 9️⃣ Suggested Music Playlist
# -------------------------
st.subheader("🎵 Suggested Music Playlist")
playlist_displayed = False
try:
    results = spotify.search(q=mood, type='playlist', limit=1)
    if results['playlists']['items']:
        playlist = results['playlists']['items'][0]
        st.markdown(f"[{playlist['name']}]({playlist['external_urls']['spotify']})")
        playlist_displayed = True
except:
    playlist_displayed = False

# Fallback text if no playlist
if not playlist_displayed:
    st.info(f"Spotify playlist for {mood} mood not found. You can use a placeholder playlist link.")

# -------------------------
# 10️⃣ Scene Summary
# -------------------------
st.subheader("📝 Scene Summary")
st.write(f"Scene: {scene_description}")
st.write(f"Mood: {mood}")
