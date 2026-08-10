import streamlit as st
import yt_dlp
import re


st.set_page_config(page_title="YouTube Audio Downloader", layout="centered")

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
    .download-link {
        display: block;
        text-align: center;
        background: #ff4b4b;
        color: white !important;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 1rem;
    }
    .download-link:hover {
        background: #e03e3e;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("YouTube Audio Downloader")
st.markdown(
    '<p class="subtitle">Paste a YouTube link and get a direct download link</p>',
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


def get_audio_info(url: str) -> dict:
    """Extract video info and best audio stream URL."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'bestaudio[ext=m4a]/bestaudio',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info


# --- Main UI ---

url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

if "audio_info" not in st.session_state:
    st.session_state.audio_info = None

fetch_btn = st.button("Get Download Link", use_container_width=True, type="primary")

if fetch_btn and url:
    if not is_valid_youtube_url(url):
        st.error("Please enter a valid YouTube URL.")
    else:
        with st.spinner("Extracting audio link..."):
            try:
                info = get_audio_info(url)
                st.session_state.audio_info = info
            except Exception as e:
                error_msg = str(e)
                if "403" in error_msg:
                    st.error(
                        "YouTube blocked the server request. "
                        "The direct link method may still work - try again."
                    )
                else:
                    st.error(f"Failed: {error_msg}")
                st.session_state.audio_info = None

if st.session_state.audio_info:
    info = st.session_state.audio_info
    st.markdown("---")

    thumbnail = info.get("thumbnail")
    if thumbnail:
        st.image(thumbnail)

    title = info.get('title', 'Unknown Title')
    channel = info.get('uploader', 'Unknown')
    duration = format_duration(info.get('duration'))

    st.markdown(f"""
    <div class="video-info">
        <h4>{title}</h4>
        <p><strong>Channel:</strong> {channel}</p>
        <p><strong>Duration:</strong> {duration}</p>
    </div>
    """, unsafe_allow_html=True)

    # Get the direct audio URL
    audio_url = info.get('url')
    if not audio_url:
        # Try from requested_formats or formats
        formats = info.get('requested_formats') or info.get('formats') or []
        for f in reversed(formats):
            if f.get('acodec') and f['acodec'] != 'none':
                audio_url = f.get('url')
                break

    if audio_url:
        st.markdown(
            f'<a class="download-link" href="{audio_url}" target="_blank">'
            f'Download Audio'
            f'</a>',
            unsafe_allow_html=True,
        )
        st.caption(
            "This link opens the audio stream directly. "
            "Long-press or right-click to save. "
            "Link expires in a few hours."
        )
    else:
        st.error("Could not extract a direct audio URL.")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#999; font-size:0.8rem;">'
    'Built with yt-dlp and Streamlit. For personal use only.'
    '</p>',
    unsafe_allow_html=True,
)
