import os

from typing import Union
from termcolor import colored

from core.audio_processing import *
from core.audio_capture import AudioCapture
from core.database import FingerprintsDatabase
from utils.audio_utils import *


def process_identify_song() -> Union[dict, None]:
    """Identify a song from an audio sample."""

    file_path = "data/recordings/temp.wav"

    audio_capture = AudioCapture()

    audio_capture.start_recording()

    audio_capture.record_to_file(file_path)

    audio_data, sampling_rate = load_audio(file_path=file_path)

    print(colored("Processing audio...", color="yellow"))
    spectrogram, freqs, times = create_spectrogram(y=audio_data, sr=sampling_rate)
    peaks = get_peaks(spectrogram=spectrogram, amp_thres=-50, neighborhood_size=100)
    fingerprint = create_fingerprint(peaks, freqs, times, fan_value=150)

    os.remove(file_path)

    if not fingerprint.check_empty():
        with FingerprintsDatabase() as db:
            song_title = db.identify_song(fingerprint)

        if not song_title:
            print(colored("No song detected...", color="red", attrs=["bold"]))

        else:
            print(
                colored(
                    f"Song identified : {song_title}", color="green", attrs=["bold"]
                )
            )

            with FingerprintsDatabase() as db:
                return db.get_song_details(song_title)

    else:
        print(colored("No fingerprint detected...", color="red", attrs=["bold"]))
