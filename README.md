# YouTube Downloader

A simple YouTube video/audio downloader with a clean web interface.

## Prerequisites

- Python 3.8+
- FFmpeg (required for merging video+audio and MP3 conversion)

### Install FFmpeg on Windows

Download from https://ffmpeg.org/download.html and add to PATH,
or use winget:

```
winget install FFmpeg
```

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

The app will open at http://localhost:8501

## Usage

1. Paste a YouTube URL in the input field
2. Select Video (MP4) or Audio (MP3)
3. Click "Fetch Video Info" to preview the video
4. Click "Download" to process the video
5. Click "Save" to download the file to your machine
