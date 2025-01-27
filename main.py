import tkinter as tk
import customtkinter as ctk
from lyricsgenius import Genius
from PIL import Image, ImageTk
import requests
import io
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser
import os
import json

GENIUS_API_TOKEN = #your GENIUS_API_TOKEN goes here
SPOTIFY_CLIENT_ID = #your SPOTIFY_CLIENT_ID goes here 
SPOTIFY_CLIENT_SECRET = #your SPOTIFY_CLIENT_SECRETgoes here 

genius = Genius(GENIUS_API_TOKEN)
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
window.title("Lyrics Extractor")
window.geometry("600x750")

SEARCH_HISTORY_FILE = "search_history.json"
search_history = []

def load_search_history():
    global search_history
    if os.path.exists(SEARCH_HISTORY_FILE):
        with open(SEARCH_HISTORY_FILE, "r") as file:
            search_history = json.load(file)
            history_list.delete(0, tk.END)
            for entry in search_history:
                history_list.insert(tk.END, entry)

def save_search_history():
    with open(SEARCH_HISTORY_FILE, "w") as file:
        json.dump(search_history, file)

def extract_lyrics():
    song = song_entry.get()
    artist = artist_entry.get()

    if not song or not artist:
        status_label.configure(text="Please enter both song and artist.", text_color="red")
        return

    status_label.configure(text="Searching for lyrics...", text_color="yellow")
    song_data = genius.search_song(song, artist)

    if song_data:
        lyrics_text.delete(1.0, tk.END)
        lyrics_text.insert(tk.END, song_data.lyrics)
        status_label.configure(text="Lyrics found!", text_color="green")
        add_to_history(song, artist)
        display_album_art(song_data.song_art_image_url)
    else:
        lyrics_text.delete(1.0, tk.END)
        lyrics_text.insert(tk.END, "Lyrics not found.")
        status_label.configure(text="Lyrics not found.", text_color="red")

def add_to_history(song, artist):
    entry = f"{song} - {artist}"
    if entry not in search_history:
        search_history.append(entry)
        history_list.insert(tk.END, entry)
        save_search_history()

def display_album_art(url):
    if url:
        response = requests.get(url)
        img_data = Image.open(io.BytesIO(response.content)).resize((150, 150))
        album_image = ImageTk.PhotoImage(img_data)
        album_art_label.configure(image=album_image)
        album_art_label.image = album_image

def open_spotify_song():
    song = song_entry.get()
    artist = artist_entry.get()

    if not song or not artist:
        status_label.configure(text="Please enter both song and artist.", text_color="red")
        return

    try:
        results = sp.search(q=f"track:{song} artist:{artist}", type="track", limit=1)
        if results["tracks"]["items"]:
            track = results["tracks"]["items"][0]
            spotify_url = track["external_urls"]["spotify"]
            webbrowser.open(spotify_url)
            status_label.configure(text="Opening Spotify...", text_color="green")
        else:
            status_label.configure(text="Song not found on Spotify.", text_color="red")
    except Exception as e:
        status_label.configure(text=f"Error opening Spotify: {e}", text_color="red")

def open_genius_page():
    song = song_entry.get()
    artist = artist_entry.get()

    if not song or not artist:
        status_label.configure(text="Please enter both song and artist.", text_color="red")
        return

    try:
        song_data = genius.search_song(song, artist)
        if song_data and song_data.url:
            webbrowser.open(song_data.url)
            status_label.configure(text="Opening Genius page...", text_color="green")
        else:
            status_label.configure(text="Genius page not found.", text_color="red")
    except Exception as e:
        status_label.configure(text=f"Error opening Genius page: {e}", text_color="red")

def toggle_mode():
    current_mode = ctk.get_appearance_mode()
    new_mode = "Light" if current_mode == "Dark" else "Dark"
    ctk.set_appearance_mode(new_mode)

ctk.CTkLabel(window, text=" Lyrics Extractor", font=("Arial", 20)).pack(pady=10)

frame = ctk.CTkFrame(window)
frame.pack(pady=10)

ctk.CTkLabel(frame, text="Song Name:").grid(row=0, column=0, padx=10, pady=5)
song_entry = ctk.CTkEntry(frame, width=200)
song_entry.grid(row=0, column=1, padx=10, pady=5)

ctk.CTkLabel(frame, text="Artist Name:").grid(row=1, column=0, padx=10, pady=5)
artist_entry = ctk.CTkEntry(frame, width=200)
artist_entry.grid(row=1, column=1, padx=10, pady=5)

extract_button = ctk.CTkButton(frame, text="Extract Lyrics", command=extract_lyrics)
extract_button.grid(row=2, column=0, columnspan=2, pady=10)

spotify_button = ctk.CTkButton(frame, text="Open on Spotify", command=open_spotify_song)
spotify_button.grid(row=3, column=0, columnspan=2, pady=10)

genius_button = ctk.CTkButton(frame, text="Open on Genius", command=open_genius_page)
genius_button.grid(row=4, column=0, columnspan=2, pady=10)

toggle_button = ctk.CTkButton(frame, text="Dark/Light Mode", command=toggle_mode)
toggle_button.grid(row=5, column=0, columnspan=2, pady=10)

album_art_label = ctk.CTkLabel(window, text="")
album_art_label.pack()

lyrics_text = tk.Text(window, height=15, wrap=tk.WORD)
lyrics_text.pack(pady=10)

status_label = ctk.CTkLabel(window, text="")
status_label.pack(pady=5)

history_label = ctk.CTkLabel(window, text="Search History")
history_label.pack(pady=5)

history_frame = ctk.CTkFrame(window)
history_frame.pack(pady=5)

history_list = tk.Listbox(history_frame, height=10, width=50)
history_list.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)

scrollbar = tk.Scrollbar(history_frame, orient=tk.VERTICAL, command=history_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
history_list.config(yscrollcommand=scrollbar.set)

load_search_history()
window.mainloop()
