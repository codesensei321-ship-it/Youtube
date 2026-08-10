import streamlit as st
import yt_dlp
import os

st.title("Free YouTube Video Downloader")
st.write("Enter a YouTube link below to download the video.")

# User input for the video link
url = st.text_input("YouTube URL:", placeholder="https://youtube.com...")

if url:
    try:
        # Configuration to save file locally in the current directory
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video information without downloading yet
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)
            
            st.image(info.get('thumbnail'), width=300)
            st.subheader(info.get('title'))
            
            # Trigger download on button click
            if st.button("Download Video"):
                with st.spinner("Downloading..."):
                    ydl.download([url])
                st.success("Downloaded successfully to your local folder!")
                
    except Exception as e:
        st.error(f"An error occurred: {e}")
