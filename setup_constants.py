# setup_constants.py

import json

with open("config.json") as f:
    config = json.load(f)

NUM_CHANNELS = config["num_channels"]
BITS_PER_TONE = config["bits_per_tone"]
FREQ_STEPS = config["freq_steps"]
STARTING_FREQUENCY = config["starting_frequency"]

# The first 2 frequencies are the start/end control frequencies
START_FREQ = STARTING_FREQUENCY
END_FREQ = STARTING_FREQUENCY + FREQ_STEPS

def generate_freq_map_template(bits_per_tone: int) -> dict[str, None]:
    # Generates a dictionary with a key for every combination of bits_per_tone bits (and for "SEPARATE")
    
    # Generate all bit strings of length bits_per_tone
    keys = [format(i, f"0{bits_per_tone}b") for i in range(2**bits_per_tone)]
    # Add the SEPARATOR key
    keys.append("SEPARATE")
    
    freq_map = {k: None for k in keys} # None as default since it's a template
    return freq_map

freq_maps = []
freq_ranges = [(START_FREQ - FREQ_STEPS//2, END_FREQ + FREQ_STEPS//2)] # first range is the control range

template = generate_freq_map_template(BITS_PER_TONE)

last_assigned_freq = END_FREQ

# Main loop that generates all frequency maps and their associated ranges
for i in range(NUM_CHANNELS):
    start_range = last_assigned_freq + FREQ_STEPS//2
    
    temp = template.copy()
    
    for key in temp.keys():
        temp[key] = last_assigned_freq + FREQ_STEPS
        last_assigned_freq += FREQ_STEPS
    freq_maps.append(temp)
    
    end_range = last_assigned_freq + FREQ_STEPS//2
    
    freq_ranges.append((start_range, end_range))