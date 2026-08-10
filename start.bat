@echo off
echo Starting YouTube Audio Downloader...
echo.
echo Starting Streamlit server...
start /B streamlit run app.py --server.port 8501 --server.headless true
timeout /t 3 /nobreak >nul
echo.
echo Starting Cloudflare Tunnel...
echo Your public URL will appear below (look for the .trycloudflare.com link):
echo.
"C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:8501
