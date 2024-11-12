import sys
import os
import json
import re
from typing import Dict, List, Any

import streamlit as st

sys.path.append("core")
from core.store_songs import process_audio_file

# Regular expression for validating URLs
URL_REGEX = re.compile(
    r"^(https?:\/\/)?"  # Scheme (http or https)
    r"(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})"  # Domain name
    r"(:[0-9]{1,5})?"  # Optional port
    r"(\/[^\s]*)?$"  # Path
)


def is_valid_url(url: str) -> bool:
    """
    Checks if a URL is valid according to a regex pattern.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    return bool(URL_REGEX.match(url))


def load_metadata(json_path: str) -> Dict[str, Any]:
    """
    Loads metadata from a JSON file.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        Dict[str, Any]: A dictionary containing metadata if the file exists, empty dictionary otherwise.
    """
    if os.path.exists(json_path):
        with open(json_path, "r") as json_file:
            return json.load(json_file)
    return {}


def save_metadata(json_path: str, metadata: Dict[str, Any]) -> None:
    """
    Saves metadata to a JSON file.

    Args:
        json_path (str): Path to the JSON file.
        metadata (Dict[str, Any]): Metadata to be saved.
    """
    with open(json_path, "w") as json_file:
        json.dump(metadata, json_file, indent=4)


def get_audio_files(folder_path: str) -> List[str]:
    """
    Retrieves a list of audio files in a given folder.

    Args:
        folder_path (str): Path to the folder containing audio files.

    Returns:
        List[str]: List of audio file names with extensions `.mp3`, `.wav`, or `.flac`.
    """
    try:
        files = os.listdir(folder_path)
        return [f for f in files if f.endswith((".mp3", ".wav", ".flac"))]
    except FileNotFoundError:
        st.write("The folder path provided does not exist. Please enter a valid path.")
        return []


def initialize_metadata(
    folder_path: str, audio_files: List[str], metadata: Dict[str, Any]
) -> None:
    """
    Initializes metadata for each audio file in the folder if it does not exist.

    Args:
        folder_path (str): Path to the folder containing audio files.
        audio_files (List[str]): List of audio file names.
        metadata (Dict[str, Any]): Metadata dictionary to update.
    """
    json_path = os.path.join(folder_path, "song_details.json")
    for file in audio_files:
        file_name = os.path.splitext(file)[0]
        if file_name not in metadata:
            metadata[file_name] = {
                "title": file_name,
                "artists": "Unknown",
                "album": "Unknown",
                "lyrics": "Lyrics not available",
                "cover": "URL for cover image",
                "url": "URL for song video",
            }
    save_metadata(json_path, metadata)


def check_metadata(metadata: Dict[str, Any], file_name: str) -> bool:
    """
    Vérifie si les métadonnées d'un fichier audio sont complètes et respectent les contraintes de longueur.

    Args:
        metadata (Dict[str, Any]): Dictionnaire contenant les métadonnées.
        file_name (str): Nom du fichier audio.

    Returns:
        bool: True si les métadonnées sont complètes et respectent les contraintes de longueur, False sinon.
    """
    """
    Checks if the metadata for an audio file is complete and meets length constraints.

    Args:
        metadata (Dict[str, Any]): Dictionary containing the metadata.
        file_name (str): Name of the audio file.

    Returns:
        bool: True if the metadata is complete and adheres to length constraints, False otherwise.
    """
    # Length constraints for each field
    length_constraints = {
        "title": 50,
        "artists": 50,
        "album": 50,
        "lyrics": 10000,
        "cover": 500,
        "url": 500,
    }

    # Default values for each field
    default_values = {
        "artists": "Unknown",
        "album": "Unknown",
        "lyrics": "Lyrics not available",
        "cover": "URL for cover image",
        "url": "URL for song video",
    }

    # Get the song's metadata
    song_data = metadata.get(file_name, {})

    # Check if the fields are not empty and are different from default values
    for key, default in default_values.items():
        if song_data.get(key) == default:
            return False

    # Check that the length of each field does not exceed the maximum allowed
    for key, max_length in length_constraints.items():
        value = song_data.get(key, "")
        if len(value) > max_length:
            st.warning(
                f"The {key} field for '{file_name}' exceeds the maximum length of {max_length} characters."
            )
            return False

    # Check that the URLs are valid
    cover_url = song_data.get("cover", "")
    video_url = song_data.get("url", "")
    return is_valid_url(cover_url) and is_valid_url(video_url)


def store_audio_folder(folder_path: str = "data/audio", verbose: int = 1):
    """
    Process all audio files in a folder and store them in a database.

    Args:
        folder_path (str): The folder where audio files are stored.
        verbose (int): The verbosity level, to control log messages.
    """

    audio_files = [
        file_name for file_name in os.listdir(folder_path) if file_name.endswith(".mp3")
    ]
    total_files = len(audio_files)

    my_bar = st.progress(0, text="Processing audio files...")

    if total_files == 0:
        st.warning("No audio files found in the specified folder.")
        return

    with st.expander("Processing audio files..."):
        for i, file_name in enumerate(audio_files):
            if verbose:
                print(f"Processing file : {file_name}")

            progress = (i + 1) / total_files
            my_bar.progress(
                progress, text=f"Processing {file_name} ({i + 1}/{total_files})"
            )

            process_audio_file(
                file_name, folder_path, store_in_db=True, verbose=verbose
            )

        st.success("All audio files have been processed and stored successfully !")
