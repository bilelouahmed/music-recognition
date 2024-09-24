from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from termcolor import colored
from scipy.ndimage import maximum_filter
from scipy.ndimage import (
    generate_binary_structure,
    iterate_structure,
    binary_erosion,
)
from core.database import FingerprintsDatabase
from models.song_fingerprint import SongHashPair, SongFingerprint

# ------------------------------------------- CONSTANTS ------------------------------------------- #

# Default window size (in samples) for the Fast Fourier Transform (FFT) used in creating the spectrogram.
# A window size of 4096 is a balance between frequency and time resolution,
# making it suitable for general audio analysis. Larger window sizes provide better frequency resolution
# but poorer time resolution, while smaller sizes do the opposite.
DEFAULT_WINDOW_SIZE = 4096

# Default ratio of overlap between consecutive windows in the spectrogram.
# A ratio of 0.5 means each window overlaps the next by 50%, which provides a good balance
# between time and frequency resolution and helps reduce spectral leakage.
DEFAULT_WINDOW_RATIO = 0.5

# Size of the neighborhood around each peak used for peak detection in the spectrogram.
# A value of 20 indicates a 20x20 region around each peak is considered for identifying local maxima,
# helping to distinguish significant peaks from minor variations in the data.
PEAK_NEIGHBORHOOD_SIZE = 20

# Default minimum amplitude threshold (in dB) for peak detection in the spectrogram.
# Peaks with amplitude values below this threshold will be ignored to reduce noise and focus on more prominent features.
DEFAULT_AMPLITUDE_THRESHOLD = -50

# Default number of neighboring peaks to consider when creating hash pairs for the audio fingerprint.
# A value of 30 means each peak will be paired with the next 30 closest peaks in time.
DEFAULT_FAN_VALUE = 30


# ------------------------------------------------------------------------------------------------- #


def create_spectrogram(
    y: np.ndarray,
    sr: int,
    wsize: int = DEFAULT_WINDOW_SIZE,
    wratio: float = DEFAULT_WINDOW_RATIO,
    plot: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create a spectrogram using matplotlib's specgram function.
    If visualize is True, display a plot of the spectrogram.
    """

    spectrogram, freqs, times = mlab.specgram(
        y, NFFT=wsize, Fs=sr, window=mlab.window_hanning, noverlap=int(wsize * wratio)
    )

    # Convert to dB scale
    spectrogram_db = 10 * np.log10(spectrogram)

    if plot:
        plt.figure(figsize=(12, 8))
        plt.imshow(
            spectrogram_db,
            aspect="auto",
            origin="lower",
            extent=[times.min(), times.max(), freqs.min(), freqs.max()],
        )
        plt.colorbar(label="Intensity (dB)")
        plt.ylabel("Frequency (Hz)")
        plt.xlabel("Time (s)")
        plt.title("Spectrogram")
        plt.show()

    return spectrogram_db, freqs, times


def get_peaks(
    spectrogram: np.ndarray,
    plot: bool = False,
    neighborhood_size: int = PEAK_NEIGHBORHOOD_SIZE,
    amp_thres: int = DEFAULT_AMPLITUDE_THRESHOLD,
) -> list:
    """
    Extract peaks from an array of spectrogram data.
    """

    struct = generate_binary_structure(2, 1)

    neighborhood = iterate_structure(struct, neighborhood_size)
    local_max = maximum_filter(spectrogram, footprint=neighborhood) == spectrogram

    # Filter out background
    background_threshold = np.percentile(spectrogram, 5)
    background = spectrogram <= background_threshold

    eroded_background = binary_erosion(
        background, structure=neighborhood, border_value=1
    )

    # Identify peaks
    detected_peaks = local_max ^ eroded_background

    # Filter out peaks below amplitude threshold
    peaks_x, peaks_y = np.where(detected_peaks)
    peaks = [
        (x, y, spectrogram[x, y])
        for x, y in zip(peaks_x, peaks_y)
        if spectrogram[x, y] > amp_thres
    ]

    if plot:
        plt.figure(figsize=(12, 8))
        plt.imshow(spectrogram, aspect="auto", origin="lower")
        plt.scatter([p[1] for p in peaks], [p[0] for p in peaks], c="r", s=10)
        plt.colorbar(label="Intensity (dB)")
        plt.ylabel("Frequency (Hz)")
        plt.xlabel("Time (s)")
        plt.title("Spectrogram with detected peaks")
        plt.show()

    return peaks


def create_fingerprint(
    peaks: list, freqs: list, times: list, fan_value: int = DEFAULT_FAN_VALUE
) -> SongFingerprint:
    """
    Create hash pairs from the peaks.
    """

    fingerprint = SongFingerprint()

    # Iterate over each peak
    for i in range(len(peaks)):
        # Consider `fan_value` neighboring peaks for pairing
        for j in range(1, fan_value):
            if (i + j) < len(peaks):
                # Get frequencies and times for the current pair of peaks
                freq1 = freqs[peaks[i][0]]
                freq2 = freqs[peaks[i + j][0]]
                time1 = times[peaks[i][1]]
                time2 = times[peaks[i + j][1]]

                # Calculate time difference between the pair
                time_delta = time2 - time1

                if 0 <= time_delta <= 200:
                    # Create a hash string for the pair and append it to the list
                    hash_pair = SongHashPair(
                        hash=f"{freq1:.2f}|{freq2:.2f}|{time_delta}", offset=time1
                    )

                    fingerprint.add_hash_pair(hash_pair)

    return fingerprint


def store_fingerprint(
    db: FingerprintsDatabase, song_details: dict, fingerprint: SongFingerprint
) -> int:
    """
    Store the fingerprint in the database.
    """
    song_id = db.insert_song(song_details)
    fingerprint.set_song_id(song_id)
    db.insert_fingerprint(fingerprint)
    print(colored("Stored fingerprint in the database.", color="green"))

    return song_id
