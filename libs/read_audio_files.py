from typing import Union
import librosa

# ------------------------------------------- CONSTANTS ------------------------------------------- #

# Default sampling rate for audio files (in Hz). Sampling rate determines how many times per second an audio signal is measured.
# Higher rates capture more detail but increase file size. 11025 Hz provides acceptable quality
# for speech while keeping file sizes relatively small.
DEFAULT_SAMPLING_RATE = 11025


def read_audio(
    file_path: str, sr: str = DEFAULT_SAMPLING_RATE, duration: Union[int, None] = None
):
    """
    Read an audio file and return up to 'duration' seconds of audio (default: all the song).

    Parameters:
        file_path (str): The path to the audio file.
        sr (str, optional): The target sampling rate of the audio file. Defaults to DEFAULT_SAMPLING_RATE.
        duration (int or None, optional): The duration of audio to read in seconds. If None, reads the entire audio file. Defaults to None.

    Returns:
        tuple: A tuple containing the audio data and the sampling rate.
    """
    if duration is None:
        y, sr = librosa.load(file_path, sr=sr)
    else:
        y, sr = librosa.load(path=file_path, sr=sr, duration=duration)

    return y, sr
