import os
import json

from core.database import FingerprintsDatabase
from core.audio_processing import *
from utils.audio_utils import *


def process_audio_file(
    file_name: str,
    folder_path: str,
    verbose: int = 1,
    store_in_db: bool = False,
    plot_spectrogram: bool = False,
    plot_peaks: bool = False,
) -> list:
    """
    Process an audio file through all steps to create a fingerprint.
    """

    file_path = os.path.join(folder_path, file_name)
    song_details_path = os.path.join(folder_path, "song_details.json")

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
        with open(song_details_path, "r") as f:
            song_details = json.load(f)

        with FingerprintsDatabase() as db:
            store_fingerprint(
                db,
                song_details[os.path.splitext(os.path.basename(file_path))[0]],
                fingerprint,
            )

    return fingerprint
