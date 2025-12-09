import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
import random

# Load API keys from Streamlit secrets
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

# Streamlit page config
st.set_page_config(page_title="Movie Moodboard", layout="wide")
st.title("🎬 Movie Moodboard")

# Input scene description
scene_description = st.text_area("Describe your movie scene:", "")

# Select mood
mood = st.selectbox("Choose a mood:", ["Happy", "Sad", "Suspenseful", "Romantic"])

# -----------------------------
# TMDb: Search movie poster
# -----------------------------
if scene_description:
    st.subheader("🎨 Movie Poster / Concept Art")
    try:
        tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={scene_description}"
        response = requests.get(tmdb_url).json()
        if response["results"]:
            poster_path = response["results"][0]["poster_path"]
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            poster_img = Image.open(BytesIO(requests.get(poster_url).content))
            st.image(poster_img, caption=f"Poster: {response['results'][0]['title']}", use_column_width=True)
        else:
            st.info("No movie poster found. Using placeholder.")
            placeholder_path = "assets/placeholder.jpg"
            if os.path.exists(placeholder_path):
                st.image(Image.open(placeholder_path), caption="Placeholder", use_column_width=True)
    except Exception as e:
        st.error(f"Error fetching TMDb poster: {e}")

# -----------------------------
# OpenAI DALL·E: Concept Art
# -----------------------------
if scene_description:
    st.subheader("🖌️ AI Concept Art (OpenAI DALL·E)")
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        prompt = f"Concept art for a {mood.lower()} movie scene: {scene_description}"
        response = openai.Image.create(prompt=prompt, n=1, size="512x512")
        image_url = response['data'][0]['url']
        ai_image = Image.open(BytesIO(requests.get(image_url).content))
        st.image(ai_image, caption="AI Concept Art", use_column_width=True)
    except Exception as e:
        st.info("OpenAI API error or placeholder used.")
        placeholder_path = "assets/placeholder.jpg"
        if os.path.exists(placeholder_path):
            st.image(Image.open(placeholder_path), caption="Placeholder", use_column_width=True)

# -----------------------------
# Spotify: Suggested Playlist
# -----------------------------
st.subheader("🎵 Suggested Music Playlist")
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    spotify_auth = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    spotify = spotipy.Spotify(auth_manager=spotify_auth)

    results = spotify.search(q=mood, type='playlist', limit=1)
    if results['playlists']['items']:
        playlist = results['playlists']['items'][0]
        st.markdown(f"[{playlist['name']}]({playlist['external_urls']['spotify']})")
    else:
        st.info("No playlist found for this mood.")
except Exception as e:
    st.info("Spotify API error or placeholder used.")
    st.write(f"Suggested playlist for {mood} mood: 🎵 Example Playlist Link")

# -----------------------------
# Scene Summary
# -----------------------------
st.subheader("📝 Scene Summary")
st.write(f"Scene: {scene_description}")
st.write(f"Mood: {mood}")

# -----------------------------
# Fallback Mood Images
# -----------------------------
mood_images = {
    "Happy": ["assets/happy1.jpg", "assets/happy2.jpg"],
    "Sad": ["assets/sad1.jpg", "assets/sad2.jpg"],
    "Romantic": ["assets/romantic1.jpg"],
    "Suspenseful": ["assets/suspense1.jpg"]
}

# Display random mood image if API fails
try:
    raise Exception("Simulate API fail")  # For testing fallback
except:
    selected_image = random.choice(mood_images[mood])
    img = Image.open(selected_image)
    st.image(img, caption=f"{mood} Moodboard (placeholder)", use_column_width=True)
