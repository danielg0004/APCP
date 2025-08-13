# receive.py

import numpy as np
import pyaudio
import json
from setup_constants import START_FREQ, END_FREQ, FREQ_STEPS, NUM_CHANNELS, freq_maps, freq_ranges

with open("config.json") as f:
    config = json.load(f)

SAMPLE_RATE = config["sample_rate"]
DURATION_PER_SAMPLE = config["duration_per_sample"]
MIN_MAGNITUDE = config["min_magnitude"]
CHUNK_SIZE = config["chunk_size"]
FFT_SIZE = config["fft_size"]

REVERSE_FREQ_MAPS = [{freq: bits for bits, freq in freq_map.items()} for freq_map in freq_maps]

FFT_FREQUENCIES = np.fft.fftfreq(FFT_SIZE, 1/SAMPLE_RATE)[:FFT_SIZE//2] # Precomputed

def _get_audio_stream() -> tuple[pyaudio.PyAudio, pyaudio.Stream]:
    # Initializes and returns a PyAudio instance and an audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)
    return p, stream

def _record_audio_from_stream(stream: pyaudio.Stream) -> np.ndarray:
    # Records and returns an audio segment from the stream
    frames = []
    for _ in range(0, int(SAMPLE_RATE / CHUNK_SIZE * DURATION_PER_SAMPLE)):
        data = stream.read(CHUNK_SIZE)
        frames.append(data)
    audio_data = np.frombuffer(b"".join(frames), dtype=np.int16)
    return audio_data

def _extract_frequency(audio_data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Uses FFT and a hanning window to get a list of detected frequencies in the audio data and their associated magnitudes
    windowed = audio_data * np.hanning(len(audio_data))
    spectrum = np.fft.fft(windowed, n=FFT_SIZE)[:FFT_SIZE//2]
    freqs = FFT_FREQUENCIES
    
    return freqs, np.abs(spectrum)

def _filter_frequency_range(freqs: np.ndarray, magnitude: np.ndarray, freq_range: tuple[int, int]) -> tuple[int | None, float | None]:
    # Filters by a specific frequency range and returns the dominant frequency and its magnitude (confidence)
    
    # Mask to get the frequencies within the specified range
    freq_range_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
    
    # Filter both freqs and magnitude arrays based on the mask
    filtered_freqs = freqs[freq_range_mask]
    filtered_mags = magnitude[freq_range_mask]
    
    if len(filtered_freqs) == 0:
        return None, None  # No frequency detected within range
    
    # Find the dominant frequency within the range
    dominant_freq = filtered_freqs[np.argmax(filtered_mags)]
    confidence = np.max(filtered_mags)  # Confidence is the magnitude of the dominant frequency
    return dominant_freq, confidence

def _get_channel_frequencies() -> list[list[int]]:
    # Listens to the audio stream and extracts the frequencies for each channel
    freqs_received = [[] for _ in range(NUM_CHANNELS)]
    p, stream = _get_audio_stream()
    started = False
    ended = False
    audios = []
    
    print("Listening for a signal...")
    
    while not ended:
        audio_data = _record_audio_from_stream(stream)
        freqs, magnitude = _extract_frequency(audio_data) # Uses FFT to get list of frequencies and their magnitudes
        dominant_freq, confidence = _filter_frequency_range(freqs, magnitude, freq_ranges[0]) # Filters by the control range and returns dominant frequency
        if dominant_freq and confidence >= MIN_MAGNITUDE: # Disregard noise
            dominant_freq = round(dominant_freq / FREQ_STEPS) * FREQ_STEPS # Round it to the nearest possible value
            if dominant_freq==START_FREQ:
                started = True
            elif dominant_freq==END_FREQ:
                ended = True
        elif started:
            audios.append(audio_data)
            
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    for audio_data in audios:
        freqs, magnitude = _extract_frequency(audio_data)
        for i in range(NUM_CHANNELS):
            dominant_freq, _ = _filter_frequency_range(freqs, magnitude, freq_ranges[i+1]) # Filters by the (i+1)th range (ignoring the 0th, the control range) and returns dominant frequency
            if dominant_freq:
                dominant_freq = round(dominant_freq / FREQ_STEPS) * FREQ_STEPS # Round it to the nearest possible value
                freqs_received[i].append(dominant_freq)
    return freqs_received

def _filter_channel_frequencies(freqs: list[list[int]]) -> list[list[int]]:
    # Filters the recorded frequencies by eliminating neighboring identical frequencies (until one remains) and ignoring the "SEPARATE" frequencies
    filtered_freqs = [[] for _ in range(NUM_CHANNELS)]
    for i in range(NUM_CHANNELS):
        for j in range(len(freqs[i])):
            if freqs[i][j] != freq_maps[i]["SEPARATE"]:
                if j==0 or freqs[i][j] != freqs[i][j-1]:
                    filtered_freqs[i].append(freqs[i][j])
    return filtered_freqs
    

def _frequencies_to_bits(freqs: list[list[int]]) -> str:
    # Converts a list of frequencies for each channel into a string of bits
    message = ""
    for i in range(NUM_CHANNELS):
        for freq in freqs[i]:
            message += REVERSE_FREQ_MAPS[i][freq]
    return message

def _bits_to_text(bits: str) -> str:
    # Converts a string of bits into a human-readable message
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return "".join(chr(int(c, 2)) for c in chars)

# The main function the cli.py will call
def listen_and_decode() -> str:
    '''
    Listens for and decodes an audio message
    
    Returns:
        str: The decoded text message
    '''
    
    print("Starting to decode audio message...")
    
    received_freqs = _get_channel_frequencies()
    filtered_freqs = _filter_channel_frequencies(received_freqs) # Filter the frequencies

    binary_str = _frequencies_to_bits(filtered_freqs)
    text = _bits_to_text(binary_str)
    
    return text
