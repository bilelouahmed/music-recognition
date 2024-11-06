import __init__
from core.audio_processing import *
from core.database import FingerprintsDatabase
from utils.audio_utils import *
from core.audio_capture import AudioCapture
from core.store_songs import store_audio_folder

import streamlit as st
import json
import os


def guess_song():
    # Identify a song from an audio sample
    file_path = "data/recordings/temp.wav"

    audio_capture = AudioCapture()
    audio_capture.start_recording()
    print("Listening for 10 seconds...")
    audio_capture.record_to_file(file_path)

    audio_data, sampling_rate = load_audio(file_path)
    spectrogram, freqs, times = create_spectrogram(audio_data, sampling_rate)
    peaks = get_peaks(spectrogram, plot=True, amp_thres=-50, neighborhood_size=100)
    fingerprint = create_fingerprint(peaks, freqs, times, fan_value=150)

    with FingerprintsDatabase() as db:
        song_title = db.identify_song(fingerprint)

    if not song_title:
        print("Song not identified.")
        st.error("Song not identified.")

    if song_title:
        print(f"Song identified : {song_title}")
        st.success(f"Song identified : {song_title}")

    os.remove(file_path)


def import_song():
    pass


def app():
    st.title("Music Recognition App")

    identifying, importing = st.tabs(["Identify a song", "Import songs"])

    if identifying:
        st.write("This app can identify a song by listening to a 10-second audio clip.")
        if st.button("Identify song"):
            guess_song()
    elif importing:
        st.write("Import songs from a folder.")
        import_song()


if __name__ == "__main__":
    app()
