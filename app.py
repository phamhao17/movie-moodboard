import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

# Load API keys
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Optional: Initialize TMDb
from tmdbv3api import TMDb, Movie
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
tmdb.language = 'en'

movie = Movie()

# Optional: Initialize Spotify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

spotify_auth = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
spotify = spotipy.Spotify(auth_manager=spotify_auth)

# Streamlit app config
st.set_page_config(page_title="Movie Moodboard", layout="wide")
st.title("🎬 Movie Moodboard")

# Input scene description
scene_description = st.text_area("Describe your movie scene:", "")

# Select mood
mood = st.selectbox("Choose a mood:", ["Happy", "Sad", "Suspenseful", "Romantic"])

if scene_description:
    st.subheader("🎨 Movie Poster / Concept Art")
    
    # TMDb: Search for movie poster matching mood or keyword
    try:
        results = movie.search(scene_description)
        if results:
            poster_url = f"https://image.tmdb.org/t/p/w500{results[0].poster_path}"
            response = requests.get(poster_url)
            poster_img = Image.open(BytesIO(response.content))
            st.image(poster_img, caption=f"Poster: {results[0].title}", use_column_width=True)
        else:
            st.info("No movie poster found. Using placeholder.")
            placeholder_path = "assets/placeholder.jpg"
            if os.path.exists(placeholder_path):
                st.image(Image.open(placeholder_path), caption="Placeholder", use_column_width=True)
    except Exception as e:
        st.error(f"Error fetching TMDb poster: {e}")

    st.subheader("🖌️ AI Concept Art (OpenAI DALL·E)")
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
    except Exception as e:
        st.info("OpenAI API error or placeholder used.")
        placeholder_path = "assets/placeholder.jpg"
        if os.path.exists(placeholder_path):
            st.image(Image.open(placeholder_path), caption="Placeholder", use_column_width=True)

    st.subheader("🎵 Suggested Music Playlist")
    try:
        results = spotify.search(q=mood, type='playlist', limit=1)
        if results['playlists']['items']:
            playlist = results['playlists']['items'][0]
            st.markdown(f"[{playlist['name']}]({playlist['external_urls']['spotify']})")
        else:
            st.info("No playlist found for this mood.")
    except Exception as e:
        st.info("Spotify API error or placeholder used.")
        st.write(f"Suggested playlist for {mood} mood: 🎵 Example Playlist Link")

    st.subheader("📝 Scene Summary")
    st.write(f"Scene: {scene_description}")
    st.write(f"Mood: {mood}")
