"""CLI interface for MP3 Recorder."""

import argparse
import sys
import time

from mp3recorder.devices import get_default_device, get_device_by_name, list_audio_devices
from mp3recorder.recorder import AudioRecorder


def cmd_list_devices(_args: argparse.Namespace) -> int:
    """List all available audio input devices."""
    devices = list_audio_devices()

    if not devices:
        print("No audio input devices found.")
        return 1

    print("\nAvailable Audio Input Devices:")
    print("-" * 60)

    for device in devices:
        default_marker = " (default)" if device.is_default else ""
        print(f"  [{device.index}] {device.name}{default_marker}")
        print(f"      Channels: {device.channels}, Sample Rate: {device.sample_rate:.0f} Hz")

    print("-" * 60)
    print(f"Total: {len(devices)} device(s)\n")
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    """Record audio to MP3 file."""
    # Resolve device
    device = None
    device_name = "default"

    if args.device:
        device_info = get_device_by_name(args.device)
        if device_info is None:
            print(f"Error: Device '{args.device}' not found.")
            print("Use 'mp3recorder list-devices' to see available devices.")
            return 1
        device = device_info.index
        device_name = device_info.name
    else:
        default_device = get_default_device()
        if default_device:
            device_name = default_device.name

    # Create recorder
    recorder = AudioRecorder(
        device=device,
        sample_rate=args.sample_rate,
        channels=args.channels,
        bitrate=f"{args.bitrate}k",
    )

    # Print recording info
    print(f"\n🎙️  Recording from: {device_name}")
    print(f"   Duration: {args.duration} seconds")
    print(f"   Output: {args.output}")
    print(f"   Bitrate: {args.bitrate}k")
    print()

    # Record with progress indicator
    print("Recording", end="", flush=True)
    start_time = time.time()

    try:
        recorder.record(args.duration)

        # Show elapsed time during recording
        while time.time() - start_time < args.duration:
            elapsed = time.time() - start_time
            print(f"\rRecording... {elapsed:.1f}s / {args.duration}s", end="", flush=True)
            time.sleep(0.1)

        print(f"\rRecording... {args.duration}s / {args.duration}s ✓")

    except RuntimeError as e:
        print(f"\n\nError: {e}")
        return 1

    # Save MP3
    print("Encoding to MP3...", end=" ", flush=True)
    try:
        output_path = recorder.save_mp3(args.output)
        print("✓")
        print(f"\n✅ Saved to: {output_path.absolute()}\n")
    except RuntimeError as e:
        print(f"\n\nError: {e}")
        return 1

    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="mp3recorder",
        description="Minimal terminal-based MP3 audio recorder",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list-devices command
    list_parser = subparsers.add_parser(
        "list-devices",
        help="List available audio input devices",
    )
    list_parser.set_defaults(func=cmd_list_devices)

    # record command
    record_parser = subparsers.add_parser(
        "record",
        help="Record audio to MP3 file",
    )
    record_parser.add_argument(
        "-d", "--duration",
        type=float,
        required=True,
        help="Recording duration in seconds",
    )
    record_parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Output MP3 file path",
    )
    record_parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Audio input device name (partial match)",
    )
    record_parser.add_argument(
        "--sample-rate",
        type=int,
        default=44100,
        help="Sample rate in Hz (default: 44100)",
    )
    record_parser.add_argument(
        "--channels",
        type=int,
        default=2,
        choices=[1, 2],
        help="Number of channels: 1=mono, 2=stereo (default: 2)",
    )
    record_parser.add_argument(
        "--bitrate",
        type=int,
        default=192,
        choices=[128, 192, 256, 320],
        help="MP3 bitrate in kbps (default: 192)",
    )
    record_parser.set_defaults(func=cmd_record)

    return parser


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
