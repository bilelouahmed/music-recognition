import numpy as np
import librosa
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from termcolor import colored
from scipy.ndimage import maximum_filter
from scipy.ndimage import (
    generate_binary_structure,
    iterate_structure,
    binary_erosion,
)

DEFAULT_SR = 44100

PEAK_NEIGHBORHOOD_SIZE = 20

DEFAULT_AMP_MIN = -50


def read_audio(file_path, sr=DEFAULT_SR, duration=10):
    """
    Read an audio file and return up to 10 seconds of audio.
    """
    y, sr = librosa.load(path=file_path, sr=sr, duration=duration)
    return y, sr


def create_spectrogram(y, sr, wsize=4096, wratio=0.5, visualize=False):
    """
    Create a spectrogram using matplotlib's specgram function.
    If visualize is True, display a plot of the spectrogram.
    """

    spectrogram, freqs, times = mlab.specgram(
        y, NFFT=wsize, Fs=sr, window=mlab.window_hanning, noverlap=int(wsize * wratio)
    )

    # Convert to dB scale
    spectrogram_db = 10 * np.log10(spectrogram)

    if visualize:
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


def get_2D_peaks(spectrogram, plot=False, amp_min=DEFAULT_AMP_MIN):
    """
    Extract peaks from a 2D array of spectrogram data.
    """

    struct = generate_binary_structure(2, 1)

    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)
    local_max = maximum_filter(spectrogram, footprint=neighborhood) == spectrogram

    # Filter out background
    background_threshold = np.percentile(
        spectrogram, 5
    )  # les 5% des valeurs les plus basses
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
        if spectrogram[x, y] > amp_min
    ]

    if plot:
        plt.figure(figsize=(12, 8))
        plt.imshow(spectrogram, aspect="auto", origin="lower")
        plt.colorbar(label="Intensity (dB)")
        plt.scatter([p[1] for p in peaks], [p[0] for p in peaks], c="r", s=10)
        plt.title("Spectrogram with Detected Peaks")
        plt.show()

    return peaks


def create_fingerprint(peaks, freqs, times):
    """
    Create a fingerprint from the peaks.
    """
    return [(freqs[f], times[t], amp) for f, t, amp in peaks]


def process_audio_file(file_path, duration=10, visualize=False):
    """
    Process an audio file through all steps to create a fingerprint.
    """
    y, sr = read_audio(file_path, duration=duration)
    spectrogram, freqs, times = create_spectrogram(y, sr, visualize=visualize)
    peaks = get_2D_peaks(spectrogram, plot=visualize)
    fingerprint = create_fingerprint(peaks, freqs, times)
    return fingerprint


def main():
    file_path = "audio/Tant pis.mp3"
    fingerprint = process_audio_file(file_path, duration=10, visualize=True)
    print(
        colored(
            f"Generated fingerprint with {len(fingerprint)} points.", color="green"
        ),
    )
    for i, (freq, time, amp) in enumerate(fingerprint, 1):
        print(
            colored(
                f"Peak {i}: Frequency = {freq:.2f} Hz, Magnitude = {amp:.2f} dB",
                color="yellow",
            )
        )


if __name__ == "__main__":
    main()
