# cli.py

import argparse
from send import create_audio_file
from receive import listen_and_decode
import os

def main() -> None:
    parser = argparse.ArgumentParser(description="APCP: A sound-based communication protocol.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Send command
    send_parser = subparsers.add_parser("send", help="Send a message through audio data")
    
    send_parser.add_argument("text", type=str, help="The message to send")
    
    send_parser.add_argument("--play", action="store_true", help="Play the generated audio data") # Defaults to False
    send_parser.add_argument("--save", action="store_true", help="Save the generated audio data in a WAV file") # Defaults to False
    
    send_parser.add_argument("--filename", type=str, default="output_audio", help="File name of the outputted WAV file (if the save argument is present)")
    
    # Receive command
    receive_parser = subparsers.add_parser("receive", help="Receive frequencies from microphone")

    receive_parser.add_argument("--realtime", action="store_true", help="Enable real-time decoding as the message is received using a different architecture")
    
    args = parser.parse_args()

    if args.command == "send":
        create_audio_file(args.text, args.play, args.save, args.filename)
        if args.save:
            print(f"Audio data saved to {args.filename}.wav.")
        if args.play:
            print(f"Audio data played.")
    elif args.command == "receive":
        print("Listening... (Ctrl+C to stop)")
        for result in listen_and_decode(args.realtime): # Generator
            os.system("cls")
            print(f"Decoded message: {result}")
                
if __name__ == "__main__":
    main()
