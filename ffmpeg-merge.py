#!/usr/bin/env python

import os
import sys
import subprocess
import json
import re
import locale
from operator import itemgetter
from pathlib import Path

# Set the locale to handle UTF-8
try:
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

def get_video_info(file_path):
    """Get video codec and format information using ffprobe."""
    try:
        cmd = [
            "ffprobe", 
            "-v", "quiet", 
            "-print_format", "json", 
            "-show_format", 
            "-show_streams", 
            file_path
        ]
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        info = json.loads(result)
        
        # Find the video stream
        video_stream = None
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "video":
                video_stream = stream
                break
        
        if not video_stream:
            return None
        
        return {
            "codec_name": video_stream.get("codec_name"),
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
            "format_name": info.get("format", {}).get("format_name"),
            "file_path": file_path
        }
    except subprocess.CalledProcessError as e:
        print(f"Error analyzing {file_path}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing ffprobe output for {file_path}: {e}")
        return None

def check_videos_compatibility(video_files):
    """Check if all videos have compatible encoding for merging."""
    if not video_files:
        return False, "No video files found"
    
    video_infos = []
    for file_path in video_files:
        info = get_video_info(file_path)
        if info:
            video_infos.append(info)
        else:
            return False, f"Could not get information for {file_path}"
    
    if not video_infos:
        return False, "Could not get information for any video files"
    
    # Check if all videos have the same codec, resolution, and format
    reference = video_infos[0]
    for info in video_infos[1:]:
        if info["codec_name"] != reference["codec_name"]:
            return False, f"Incompatible codec: {reference['codec_name']} vs {info['codec_name']}"
        if info["width"] != reference["width"] or info["height"] != reference["height"]:
            return False, f"Incompatible resolution: {reference['width']}x{reference['height']} vs {info['width']}x{info['height']}"
    
    return True, video_infos

def merge_videos(video_infos, output_path):
    """Merge video files using ffmpeg concat demuxer."""
    # Create a temporary file with the list of files to concatenate
    temp_file = "concat_list.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        for info in video_infos:
            # Use Path object for better handling of Unicode paths
            file_path = Path(info["file_path"]).absolute()
            # Escape single quotes in file paths
            escaped_path = str(file_path).replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
    
    # Get the extension from the first file
    first_file_path = Path(video_infos[0]["file_path"])
    ext = first_file_path.suffix
    if not ext:
        ext = ".mp4"  # Default to mp4 if no extension found
    
    # If output_path doesn't have an extension, add the same extension as the input files
    output_path_obj = Path(output_path)
    if not output_path_obj.suffix:
        output_path = str(output_path_obj) + ext
    
    # Merge the videos using ffmpeg concat demuxer
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", temp_file,
        "-c", "copy",  # Use copy mode to avoid re-encoding
        "-y",  # Overwrite output file if it exists
        output_path
    ]
    
    try:
        subprocess.check_call(cmd)
        os.remove(temp_file)  # Clean up the temporary file
        return True, f"Successfully merged videos to {output_path}"
    except subprocess.CalledProcessError as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)  # Clean up the temporary file
        return False, f"Error merging videos: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python ffmpeg-merge.py <directory_path>")
        sys.exit(1)
    
    # Use Path object for better handling of Unicode paths
    directory_path = Path(sys.argv[1])
    
    if not directory_path.is_dir():
        print(f"Error: {directory_path} is not a valid directory")
        sys.exit(1)
    
    # Get all video files in the directory
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp']
    video_files = []
    
    for file_path in directory_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in video_extensions:
            video_files.append(str(file_path))
    
    # Sort video files by name
    video_files.sort()
    
    if not video_files:
        print(f"No video files found in {directory_path}")
        sys.exit(1)
    
    print(f"Found {len(video_files)} video files in {directory_path}")
    for file in video_files:
        print(f"  - {os.path.basename(file)}")
    
    # Check if videos can be merged
    compatible, result = check_videos_compatibility(video_files)
    
    if not compatible:
        print(f"Error: {result}")
        sys.exit(1)
    
    # Merge videos
    # Output to the same directory as the input clips with name "output"
    output_path = directory_path / "output"
    success, message = merge_videos(result, str(output_path))
    
    if success:
        print(message)
    else:
        print(f"Error: {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
