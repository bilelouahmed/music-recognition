import streamlit as st

import __init__
from app.views.songs_import import import_songs
from app.views.guess_songs import identify_song


def app():
    st.title("Music Recognition App")

    identifying, importing = st.tabs(["Identify a song", "Import songs"])

    with identifying:
        st.write("This app can identify a song by listening to a 10-second audio clip.")
        identify_song()

    with importing:
        st.write("Import songs from a folder.")
        import_songs()


if __name__ == "__main__":
    app()
