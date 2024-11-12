from typing import Union

import numpy as np
import librosa

# ------------------------------------------- CONSTANTS ------------------------------------------- #

# Default sampling rate for audio files (in Hz). Sampling rate determines how many times per second
# an audio signal is measured. Higher rates capture more detail but increase file size.
# 22050 Hz provides a balance between quality and file size, suitable for most audio applications.
DEFAULT_SAMPLING_RATE = 22050


def load_audio(
    file_path: str,
    sr: int = DEFAULT_SAMPLING_RATE,
    duration: Union[int, None] = None,
    offset: Union[float, None] = None,
    verbose: int = 0,
) -> tuple:
    """
    Read an audio file and return up to 'duration' seconds of audio starting from 'offset' (default: all the song).

    Parameters:
    file_path (str): The path to the audio file.
    sr (int, optional): The target sampling rate of the audio file. Defaults to DEFAULT_SAMPLING_RATE.
    duration (int or None, optional): The duration of audio to read in seconds. If None, reads the entire audio file. Defaults to None.
    offset (float or None, optional): The starting position of the audio in seconds. If None, starts from the beginning of the file. Defaults to None.

    Returns:
    tuple: A tuple containing the audio data and the sampling rate.
    """
    if offset is not None:
        total_duration = librosa.get_duration(path=file_path)
        if offset >= total_duration:
            if verbose:
                print(
                    f"Offset {offset} seconds is greater than the total duration {total_duration} seconds. Returning empty audio."
                )
            return np.array([]), sr

    if duration is None and offset is None:
        y, sr = librosa.load(file_path, sr=sr)
    elif duration is None:
        y, sr = librosa.load(file_path, sr=sr, offset=offset)
    elif offset is None:
        y, sr = librosa.load(file_path, sr=sr, duration=duration)
    else:
        y, sr = librosa.load(file_path, sr=sr, duration=duration, offset=offset)

    return y, sr
