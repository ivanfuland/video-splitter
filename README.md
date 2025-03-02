# Video Splitter

A tool to split video files into multiple clips using ffmpeg.

## Usage

### Using the new manifest.json format

1. Create a manifest.json file with the following format:

```json
{
  "input_file": "C:/path/to/your/video.mp4",
  "output_clips": [
    { "start_time": 0, "length": 34 },
    { "start_time": 35, "length": 22 }
  ]
}
```

2. Run the script with the manifest option:

```
python ffmpeg-split.py -m manifest.json
```

The script will:
- Use the input_file path specified in the manifest
- Create a folder named "Clip-[filename]" (without extension) in the same directory as the input file
- Create output files named "clip-0.mp4", "clip-1.mp4", etc. based on the index in the output_clips array
- Each clip will start at the specified start_time and have the specified length
- All clip files will be placed in the created folder

### Using command line options

You can also use command line options to split a video:

```
python ffmpeg-split.py -f input.mp4 -s 10
```

This will split the video into 10-second segments.

For more options, run:

```
python ffmpeg-split.py --help
```

## Merging Video Clips

After splitting a video into multiple clips, you can merge them back together using the `ffmpeg-merge.py` script:

```
python ffmpeg-merge.py <directory_path>
```

For example:
```
python ffmpeg-merge.py E:\CondaList\video-splitter\input
```

> **Note for PowerShell users**: Always use the `python` command to run the scripts. Running `ffmpeg-merge.py` directly in PowerShell will result in an error because PowerShell doesn't run scripts from the current directory by default.

The script will:
- Find all video files in the specified directory
- Sort them by name
- Check if they have compatible encoding
- Merge them into a single file named "output.mp4" in the same directory as the input clips
- Use copy mode to avoid re-encoding the videos

## Handling Non-ASCII Characters

Both scripts have been improved to handle paths with non-ASCII characters (such as Chinese, Japanese, etc.) by:
- Setting the locale to handle UTF-8 encoding
- Using the `pathlib` module for better Unicode path handling
- Using absolute paths to avoid encoding issues

## Requirements

- Python
- ffmpeg (must be in your PATH)
