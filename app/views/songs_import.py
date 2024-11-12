import sys
import os

import streamlit as st

sys.path.append("app/controllers")
from songs_import_controller import (
    load_metadata,
    save_metadata,
    get_audio_files,
    initialize_metadata,
    check_metadata,
    store_audio_folder,
)


def import_songs():
    """
    Interface for importing songs and managing their metadata.

    This function provides a Streamlit interface for users to input the folder
    containing audio files, retrieves those files, and allows users to view or
    edit metadata for each file. Users can save changes and check for incomplete
    metadata across all files.
    """

    # Input for the folder path containing songs
    folder_path = st.text_input(
        "Enter the path to the folder containing your audio files :"
    )

    if folder_path:
        # Retrieve audio files in the folder
        audio_files = get_audio_files(folder_path)
        nb_of_songs = len(audio_files)

        if audio_files:
            st.success(f"{nb_of_songs} songs found !")
            json_path = os.path.join(folder_path, "song_details.json")
            song_metadata = load_metadata(json_path)

            incomplete_files = []

            # Initialize metadata for each audio file if not already present
            initialize_metadata(folder_path, audio_files, song_metadata)

            # Loop over each audio file to check and display metadata
            for file in audio_files:
                file_name = os.path.splitext(file)[0]
                metadata_complete = check_metadata(song_metadata, file_name)

                # Determine title for each song section in the interface
                expander_title = (
                    f"🟢 {file_name}" if metadata_complete else f"🔴 {file_name}"
                )
                if not metadata_complete:
                    incomplete_files.append(file_name)

                # Create a form inside an expander for each song
                with st.expander(expander_title):
                    with st.form(key=f"form_{file_name}"):
                        title = st.text_input(
                            "Title", value=song_metadata[file_name]["title"]
                        )
                        artists = st.text_input(
                            "Artists", value=song_metadata[file_name]["artists"]
                        )
                        album = st.text_input(
                            "Album", value=song_metadata[file_name]["album"]
                        )
                        lyrics = st.text_area(
                            "Lyrics", value=song_metadata[file_name]["lyrics"]
                        )
                        cover = st.text_input(
                            "Cover URL", value=song_metadata[file_name]["cover"]
                        )
                        url = st.text_input(
                            "Video URL", value=song_metadata[file_name]["url"]
                        )
                        submit_button = st.form_submit_button("Save")

                        if submit_button:
                            # Update metadata with user inputs
                            song_metadata[file_name] = {
                                "title": title,
                                "artists": artists,
                                "album": album,
                                "lyrics": lyrics,
                                "cover": cover,
                                "url": url,
                            }
                            save_metadata(json_path, song_metadata)
                            st.success(f"Metadata for '{file_name}' saved !")

            # Button to check for incomplete metadata across all songs
            if st.button("Check for incomplete metadata"):
                if incomplete_files:
                    st.warning(
                        f"Songs without complete metadata : {', '.join(incomplete_files)}"
                    )
                else:
                    st.success("All songs have complete metadata.")

                    st.button(
                        "Store all audio files",
                        on_click=lambda: store_audio_folder(folder_path=folder_path),
                    )
