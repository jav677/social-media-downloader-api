from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import subprocess
import os
import requests

app = FastAPI(title="Social Media Downloader API", version="1.0")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # سب domains allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Proxy from Environment Variable ---
PROXY = os.getenv("PROXY")  # set in Railway Variables if needed

@app.get("/")
def home():
    return {"message": "Welcome to the Social Media Downloader API", "usage": "/api?url=VIDEO_LINK"}

@app.get("/api")
def download(url: str = Query(..., description="Paste any video URL from YouTube, TikTok, Instagram, Facebook")):
    try:
        cmd = ["yt-dlp", "-g", url]

        # اگر proxy set ہے تو add کرو
        if PROXY:
            cmd = ["yt-dlp", "--proxy", PROXY, "-g", url]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # prevent hanging
        )

        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        return {"video_url": result.stdout.strip()}

    except subprocess.TimeoutExpired:
        return {"error": "Request timed out."}
    except Exception as e:
        return {"error": str(e)}


# --- Optional: server-side streaming download (for direct device download, avoids CORS issues)
@app.get("/download_file")
def download_file(url: str = Query(..., description="Video URL from /api endpoint")):
    try:
        r = requests.get(url, stream=True, timeout=60)
        return StreamingResponse(
            r.iter_content(chunk_size=1024),
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=video.mp4"}
        )
    except Exception as e:
        return {"error": str(e)}
