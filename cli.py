# cli.py

import argparse
from send import create_audio_file
from receive import listen_and_decode

def main():
    parser = argparse.ArgumentParser(description="APCP: A sound-based communication protocol.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Send command
    send_parser = subparsers.add_parser("send", help="Encode text into audio data")
    
    send_parser.add_argument("text", type=str, help="The message to encode")
    
    send_parser.add_argument("--play", action="store_true", help="Play the generated audio data") # Defaults to False
    send_parser.add_argument("--save", action="store_true", help="Save the generated audio data in a WAV file") # Defaults to False
    
    send_parser.add_argument("--file-name", type=str, default="output_audio", help="File name of the outputted WAV file")
    

    # Receive command
    recieve_parser = subparsers.add_parser("receive", help="Decode frequencies from microphone")

    args = parser.parse_args() 

    if args.command == "send":
        create_audio_file(args.text, args.play, args.save, args.file_name)
        if args.save:
            print(f"Audio data saved to {args.file_name}.wav")
        if args.play:
            print(f"Audio data played")
    elif args.command == "receive":
        print("Listening... (Ctrl+C to stop)")
        message = listen_and_decode()
        print(f"Decoded message: {message}")

if __name__ == "__main__":
    main()