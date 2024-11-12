from termcolor import colored
import pyaudio
import wave

# ------------------------------------------- CONSTANTS ------------------------------------------- #

# Default sampling rate for audio files (in Hz). Sampling rate determines how many times per second
# an audio signal is measured. Higher rates capture more detail but increase file size.
# 22050 Hz provides a balance between quality and file size, suitable for most audio applications.
DEFAULT_SAMPLING_RATE = 22050

# Default chunk size. This defines how many audio frames are read per buffer.
# Larger chunk sizes increase efficiency but may introduce latency.
DEFAULT_CHUNK_SIZE = 1024

# Default number of channels (1 = mono, 2 = stereo).
DEFAULT_CHANNELS = 1

# Default recording duration in seconds. This is the maximum recording time before automatic stop.
DEFAULT_RECORDING_DURATION = 10

# ------------------------------------------------------------------------------------------------- #


class AudioCapture:
    def __init__(
        self,
        chunk_size=DEFAULT_CHUNK_SIZE,
        sample_rate=DEFAULT_SAMPLING_RATE,
        channels=DEFAULT_CHANNELS,
        duration=DEFAULT_RECORDING_DURATION,
    ):
        """
        :param chunk_size: Number of frames per buffer.
        :param sample_rate: Sampling rate in Hz.
        :param channels: Number of audio channels (1 for mono, 2 for stereo).
        :param duration: Maximum duration of the recording in seconds.
        """
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.channels = channels
        self.duration = duration
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start_recording(self, verbose: bool = True):
        """Start the audio recording stream."""
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )

        if verbose:
            print(
                colored(
                    f"Recording started. Press Ctrl+C to stop manually or wait {self.duration} seconds...",
                    color="yellow",
                )
            )

    def stop_recording(self):
        """Stop the audio recording stream."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

    def record_to_file(
        self, file_path: str = "data/recordings/output.wav", verbose: bool = True
    ):
        """Record audio for a maximum duration but allow manual interruption."""
        frames = []
        self.start_recording()

        try:
            # Record audio for the set duration or until manually interrupted
            for _ in range(0, int(self.sample_rate / self.chunk_size * self.duration)):
                data = self.stream.read(self.chunk_size)
                frames.append(data)

        except KeyboardInterrupt:
            if verbose:
                print(colored("\nRecording manually interrupted.", color="red"))

        finally:
            self.stop_recording()

            with wave.open(file_path, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b"".join(frames))

            if verbose:
                print(colored(f"Audio recorded to {file_path}", color="green"))
