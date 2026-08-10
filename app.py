import streamlit as st
import yt_dlp
import os
import tempfile
import re
import shutil


st.set_page_config(page_title="YouTube Audio Downloader", layout="centered")

# Custom CSS for clean UI
st.markdown("""
<style>
    .block-container {
        max-width: 700px;
        padding-top: 2rem;
    }
    h1 {
        text-align: center;
        color: #1a1a2e;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #555;
        margin-bottom: 2rem;
        font-size: 1.05rem;
    }
    .video-info {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    .video-info h4 {
        margin: 0 0 0.5rem 0;
        color: #1a1a2e;
    }
    .video-info p {
        margin: 0.25rem 0;
        color: #444;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("YouTube Audio Downloader")
st.markdown(
    '<p class="subtitle">Paste a YouTube link below and download the audio</p>',
    unsafe_allow_html=True,
)


def is_valid_youtube_url(url: str) -> bool:
    patterns = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(https?://)?(www\.)?youtu\.be/[\w-]+',
        r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+',
    ]
    return any(re.match(p, url.strip()) for p in patterns)


def format_duration(seconds) -> str:
    if seconds is None:
        return "Unknown"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def is_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def get_video_info(url: str) -> dict:
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info


def download_audio(url: str, temp_dir: str) -> str:
    """Download audio from a YouTube URL."""
    has_ffmpeg = is_ffmpeg_available()

    if has_ffmpeg:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        # No FFmpeg: download best audio as M4A directly
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
        }

    ydl_opts.update({
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    files = os.listdir(temp_dir)
    if files:
        return os.path.join(temp_dir, files[0])
    return None


# --- Main UI ---

url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

# Session state
if "video_info" not in st.session_state:
    st.session_state.video_info = None
if "downloaded_file" not in st.session_state:
    st.session_state.downloaded_file = None
if "downloaded_data" not in st.session_state:
    st.session_state.downloaded_data = None
if "last_url" not in st.session_state:
    st.session_state.last_url = ""

fetch_btn = st.button("Fetch Info", use_container_width=True)

if not is_ffmpeg_available():
    st.info(
        "FFmpeg not found. Audio will download as M4A instead of MP3. "
        "Install FFmpeg for MP3 conversion."
    )

# Fetch video info
if fetch_btn and url:
    if not is_valid_youtube_url(url):
        st.error("Please enter a valid YouTube URL.")
    else:
        with st.spinner("Fetching info..."):
            try:
                info = get_video_info(url)
                st.session_state.video_info = info
                st.session_state.last_url = url
                st.session_state.downloaded_file = None
                st.session_state.downloaded_data = None
            except Exception as e:
                st.error(f"Could not fetch video info: {str(e)}")
                st.session_state.video_info = None

# Display info and download
if st.session_state.video_info:
    info = st.session_state.video_info
    st.markdown("---")

    thumbnail = info.get("thumbnail")
    if thumbnail:
        st.image(thumbnail)

    title = info.get('title', 'Unknown Title')
    channel = info.get('uploader', 'Unknown')
    duration = format_duration(info.get('duration'))
    views = info.get('view_count')
    views_str = f"{views:,}" if views else "N/A"

    st.markdown(f"""
    <div class="video-info">
        <h4>{title}</h4>
        <p><strong>Channel:</strong> {channel}</p>
        <p><strong>Duration:</strong> {duration}</p>
        <p><strong>Views:</strong> {views_str}</p>
    </div>
    """, unsafe_allow_html=True)

    # Download button
    if st.button("Download Audio", use_container_width=True, type="primary"):
        with st.spinner("Downloading audio..."):
            try:
                temp_dir = tempfile.mkdtemp()
                filepath = download_audio(st.session_state.last_url, temp_dir)
                if filepath and os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        st.session_state.downloaded_data = f.read()
                    st.session_state.downloaded_file = os.path.basename(filepath)
                    os.remove(filepath)
                    os.rmdir(temp_dir)
                else:
                    st.error("Download failed. File not found.")
            except Exception as e:
                error_msg = str(e)
                if "403" in error_msg:
                    st.error(
                        "YouTube blocked this request (HTTP 403). "
                        "This typically happens on cloud-hosted servers. "
                        "Try running this app locally instead."
                    )
                else:
                    st.error(f"Download failed: {error_msg}")

    # Save button
    if st.session_state.downloaded_data and st.session_state.downloaded_file:
        st.success("Ready to save.")
        filename = st.session_state.downloaded_file
        if filename.endswith(".mp3"):
            mime = "audio/mpeg"
        elif filename.endswith(".m4a"):
            mime = "audio/mp4"
        elif filename.endswith(".webm"):
            mime = "audio/webm"
        else:
            mime = "application/octet-stream"
        st.download_button(
            label=f"Save: {filename}",
            data=st.session_state.downloaded_data,
            file_name=filename,
            mime=mime,
            use_container_width=True,
        )

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#999; font-size:0.8rem;">'
    'Built with yt-dlp and Streamlit. For personal use only.'
    '</p>',
    unsafe_allow_html=True,
)
