from core.database import FingerprintsDatabase
from core.audio_processing import *
from utils.audio_utils import *
import json
import os

with open("data/songs/song_details.json", "r") as f:
    song_details = json.load(f)


def process_audio_file(
    file_path: str,
    verbose: int = 1,
    store_in_db: bool = False,
    plot_spectrogram: bool = False,
    plot_peaks: bool = False,
) -> list:
    """
    Process an audio file through all steps to create a fingerprint.
    """

    if verbose not in [0, 1, 2]:
        raise Exception("Verbose should be 0, 1 or 2.")

    # Read the audio file
    y, sr = load_audio(file_path=file_path, verbose=verbose)

    # Create a spectrogram
    spectrogram, freqs, times = create_spectrogram(y=y, sr=sr, plot=plot_spectrogram)

    # Get peaks from the spectrogram
    peaks = get_peaks(spectrogram=spectrogram, plot=plot_peaks)

    # Create a fingerprint from the peaks
    fingerprint = create_fingerprint(peaks, freqs, times)

    if verbose >= 1:
        print(
            colored(
                f"Generated fingerprint for song : {os.path.basename(file_path)} ({len(fingerprint)} points).",
                color="green",
            ),
        )
    if verbose == 2:
        for i, hash_pair in enumerate(fingerprint, 1):
            print(
                colored(
                    f"Time : {hash_pair.get_offset} - Hash : {hash_pair.get_hash}",
                    color="yellow",
                )
            )

    if store_in_db:
        with FingerprintsDatabase() as db:
            store_fingerprint(
                db,
                song_details[os.path.splitext(os.path.basename(file_path))[0]],
                fingerprint,
            )

    return fingerprint


def store_audio_folder(folder_path: str = "audio", verbose: int = 1):
    """
    Process all audio files in a folder.
    """

    for file in os.listdir(folder_path):
        if file.endswith(".mp3"):
            # to do : check if the song is already in the database
            process_audio_file(
                os.path.join(folder_path, file), store_in_db=True, verbose=verbose
            )
