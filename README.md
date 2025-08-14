# APCP: a sound-based communication protocol
## Introduction
APCP is a protocol that transmits data between devices through sound.
It's based on Frequency-Shift Keying ([FSK](https://en.wikipedia.org/wiki/Frequency-shift_keying)), which encodes data by shifting between different frequencies.
## Setting up
Requires Python 3.10+.
1. Clone the repository. Use `git clone https://github.com/danielg0004/APCP` to download the code.
2. Install dependencies by running `pip install -r requirements.txt`.
3. Use the CLI to send and receive messages:
  - **Sending messages:** `python cli.py send "[Message to send]" (additional arguments)`. Example: `python cli.py "Hello World!" --save --filename "output"`.
  - **Receiving messages:** `python cli.py receive`. Add the argument `--realtime` afterwards to use the alternative architecture (may be slower or more prone to error).
  - Use `python cli.py --help`, `python cli.py send --help`, or `python cli.py receive --help` to view the descriptions of the fields.
## How it works
- **Encoding:** The system converts text into binary data and maps these bits to specific frequencies. To increase the data rate, it uses multiple channels to transmit various frequencies simultaneously.
- **Synchronization:** Special `START` and `END` frequencies are used to ensure the receiver records the intended stream of data.
- **Decoding:** The receiver records audio and uses the Fast Fourier Transform ([FFT](https://en.wikipedia.org/wiki/Fast_Fourier_transform)) to analyze it and detect the dominant frequencies, which are converted back into bits and, finally, into text.
## Features
- The core parameters are adjustable within the `config.json` file.
- Runs reliably at 120 bps with the parameters in `config.json`, though they may need change depending on the system and environment.
- The receiver ignores repeated readings of the same frequency. A special `SEPARATOR` frequency is included so that intended consecutive instances of the same frequency aren't deleted.
- There is an alternative architecture for decoding that allows real-time visualization of the decoded message (read the decoded data as it's being streamed into the receiver).
- There is a CLI (command-line interface) for easy usage.
