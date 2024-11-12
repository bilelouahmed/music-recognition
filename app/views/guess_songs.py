import sys

import streamlit as st
from termcolor import colored

sys.path.append("app/controllers")
from guess_song_controller import process_identify_song


def identify_song():
    if st.button("Identify song"):
        result = process_identify_song()
        if result:
            st.success(f"Song identified !")

            cover_column, details_column = st.columns([1, 1])

            with cover_column:
                try:
                    st.image(result["cover"], caption="Cover")
                except:
                    st.write("Cover not available.")

            with details_column:
                st.write(f"Title : {result['title']}")
                st.write(f"Artist : {result['artist']}")
                st.write(f"Album : {result['album']}")

            try:
                st.video(result["url"])
            except:
                st.write("Youtube video not available.")

            st.write(f"Lyrics :\n {result['lyrics']}")

        else:
            print(
                colored(
                    "Song not identified. Please, retry.",
                    color="red",
                    attrs=["bold"],
                )
            )
