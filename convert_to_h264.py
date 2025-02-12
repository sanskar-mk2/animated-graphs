import os
import subprocess
from pathlib import Path


def get_video_codec(file_path):
    """Check the video codec of an MP4 file using FFmpeg"""
    try:
        cmd = ["ffmpeg", "-i", str(file_path)]
        result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)

        # FFmpeg outputs to stderr
        output = result.stderr

        # Look for Video: line
        if "Video:" in output:
            # If h264 is found in the Video line, it's already converted
            return "h264" if "h264" in output.lower() else "other"
    except Exception as e:
        print(f"Error checking codec: {str(e)}")
    return "unknown"


def convert_videos():
    # Get the current directory where the script is located
    current_dir = Path(__file__).parent.absolute()

    # Set input and output directories
    input_dir = current_dir / "outputs"
    output_dir = input_dir / "h264"

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all MP4 files in the outputs directory
    mp4_files = list(input_dir.glob("*.mp4"))

    if not mp4_files:
        print("No MP4 files found in the outputs directory.")
        return

    # Counters
    converted = 0
    skipped = 0
    failed = 0

    for input_file in mp4_files:
        try:
            # Skip if file is in h264 subdirectory
            if "h264" in input_file.parts:
                continue

            # Create output filename (maintain original filename)
            output_file = output_dir / input_file.name

            # Skip if output file already exists and is h264
            if output_file.exists():
                if get_video_codec(output_file) == "h264":
                    print(f"Skipping {input_file.name} - already converted")
                    skipped += 1
                    continue

            # Check input file codec
            if get_video_codec(input_file) == "h264":
                print(f"Skipping {input_file.name} - already in h264 format")
                skipped += 1
                continue

            # FFmpeg command
            ffmpeg_cmd = [
                "ffmpeg",
                "-i",
                str(input_file),
                "-c:v",
                "libx264",  # Video codec
                "-preset",
                "medium",  # Encoding speed preset
                "-crf",
                "23",  # Quality (lower = better, 18-28 is good range)
                "-c:a",
                "aac",  # Audio codec
                "-b:a",
                "128k",  # Audio bitrate
                "-movflags",
                "+faststart",  # Optimize for web playback
                "-y",  # Overwrite output file if exists
                str(output_file),
            ]

            # Run FFmpeg command
            print(f"\nConverting: {input_file.name}")
            process = subprocess.run(
                ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if process.returncode == 0:
                print(f"Successfully converted: {input_file.name}")
                converted += 1
            else:
                print(f"Error converting {input_file.name}")
                print(f"Error message: {process.stderr}")
                failed += 1

        except Exception as e:
            print(f"Error processing {input_file.name}: {str(e)}")
            failed += 1

    # Print summary
    print("\nConversion Summary:")
    print(f"Total files found: {len(mp4_files)}")
    print(f"Successfully converted: {converted}")
    print(f"Skipped (already converted): {skipped}")
    print(f"Failed conversions: {failed}")
    print(f"\nConverted files are saved in: {output_dir}")


if __name__ == "__main__":
    # Check if FFmpeg is installed
    try:
        subprocess.run(
            ["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except FileNotFoundError:
        print("Error: FFmpeg is not installed or not in system PATH.")
        print("Please install FFmpeg and make sure it's added to your system PATH.")
        print("Download FFmpeg from: https://ffmpeg.org/download.html")
        exit(1)

    print("Starting video conversion...")
    convert_videos()
    input("\nPress Enter to exit...")
