# send.py

import numpy as np
from scipy.io.wavfile import write
import json
from setup_constants import START_FREQ, END_FREQ, freq_maps, NUM_CHANNELS, BITS_PER_TONE

with open("config.json") as f:
    config = json.load(f)

SAMPLE_RATE = config["sample_rate"]
TONE_DURATION = config["tone_duration"]
VOLUME = config["volume"]
MAX_INT16 = 32767 # Max number a 16 bit signed int can hold (2^15 - 1)



def _generate_tone(frequency: float) -> np.ndarray:
    # Generates a pure sine wave at a specific frequency
    t = np.linspace(0, TONE_DURATION, int(SAMPLE_RATE * TONE_DURATION), endpoint=False)
    tone = np.sin(2 * np.pi * frequency * t)
    return tone * VOLUME

def _create_audio(frequencies: list[float]) -> np.ndarray:
    # Generates an audio of chained sine waves
    if not frequencies:
        return np.array([])
    tones = []
    for freq in frequencies:
        tones.append(_generate_tone(freq))
    return np.concatenate(tones)

def _save_audio(audio_data: np.ndarray, file_name: str = "audio") -> None:
    """
    Saves the audio data on a .wav file
    Changes the audio data from a normalized (-1, 1) value to 16-bit signed integers (standard WAV format)
    """
    audio_int16 = np.int16(audio_data * MAX_INT16)
    write(f"{file_name}.wav", SAMPLE_RATE, audio_int16)

def _text_to_bits(text: str) -> str:
    # Converts string message to a bit string
    return "".join(format(ord(c), "08b") for c in text)

def _divide_binary_str(bits: str) -> list[str]:
    # Divides a binary string into chunks for each channel
    total_len = len(bits)
    
    if total_len % BITS_PER_TONE != 0:
        raise ValueError("Total number of bits isn't dividable by the number of bits per chunk.")
    
    num_chunks = total_len // BITS_PER_TONE
    # Each channel gets at least this many bit chunks
    base_units = num_chunks // NUM_CHANNELS
    # Remainder chunks
    extra_units = num_chunks % NUM_CHANNELS
    chunks = []
    i = 0
    for channel in range(NUM_CHANNELS):
        units_in_channel = base_units + (1 if channel < extra_units else 0)
        chunk_len = BITS_PER_TONE * units_in_channel
        chunks.append(bits[i:i + chunk_len])
        i += chunk_len
    return chunks
    
def _message_to_audio(freq_map: dict[str, int], message: str) -> np.ndarray:
    # Encodes a message string into an audio signal based on a frequency map
    freqs = []
    for i in range(0, len(message), BITS_PER_TONE):
        chunk = message[i:i+BITS_PER_TONE]
        freq = freq_map[chunk]
        if freqs and freqs[-1]==freq:
            freqs.append(freq_map["SEPARATE"])
        freqs.append(freq)
    return _create_audio(freqs)

def _fragments_to_audio(fragments: list[str]) -> np.ndarray:
    # Combines multiple bit strings into a single audio signal by layering them on top of each other
    audios = []
    max_len = 0
    for i in range(len(fragments)):
        audio = _message_to_audio(freq_maps[i], fragments[i]) # Encode the ith fragment with the ith frequency map
        audios.append(audio)
        max_len = max(max_len, len(audio))
    
    # Pad each audio with the SEPARATOR tone (skipped when decoding)
    padded_audios = []
    for i, audio in enumerate(audios):
        sep_freq = freq_maps[i]["SEPARATE"]
        sep_tone = _generate_tone(sep_freq)

        # Calculate how many samples are needed to pad
        pad_len = max_len - len(audio)
        if pad_len > 0:
            # Repeat the separator tone to cover the padding length
            padding_audio = np.resize(sep_tone, pad_len)
            padded_audio = np.concatenate([audio, padding_audio])
        else:
            padded_audio = audio
        padded_audios.append(padded_audio)
    
    combined = np.sum(padded_audios, axis=0) # Add up all the audios
    combined /= np.max(np.abs(combined)) # Normalize
    
    return np.concatenate([
        _generate_tone(START_FREQ), combined, _generate_tone(END_FREQ)
    ])
    
# The main function the cli.py will call
def create_audio_file(text: str, output_file_name: str = "audio") -> None:
    '''
    Encodes a text message into an audio file
    
    Args:
        text (str): The message to encode
        output_file_name (str): The name of the output WAV file
    '''
    bits = _text_to_bits(text)
    fragmetns = _divide_binary_str(bits)
    audio = _fragments_to_audio(fragmetns)
    
    _save_audio(audio, output_file_name)
