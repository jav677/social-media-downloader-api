from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
import os
import tempfile

app = FastAPI(title="Social Media Downloader API", version="1.0")

# --- CORS Middleware for frontend fetch
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Proxy from Environment Variable (optional)
PROXY = os.getenv("PROXY")  # set in Railway variables if needed

@app.get("/")
def home():
    return {"message": "Welcome to the Social Media Downloader API", "usage": "/api?url=VIDEO_LINK"}

@app.get("/api")
def download(url: str = Query(..., description="Paste a video URL from YouTube, TikTok, Instagram, Facebook")):
    try:
        # --- create a temporary file
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, "video.mp4")

        # base command to download the best mp4 format
        cmd = ["yt-dlp", "-f", "best[ext=mp4]", "-o", temp_file_path, url]

        # add proxy if set
        if PROXY:
            cmd.insert(1, "--proxy")
            cmd.insert(2, PROXY)

        # run yt-dlp to download the file server-side
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # increase timeout for bigger files
        )

        # check for errors
        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        # serve the downloaded file to browser
        if os.path.exists(temp_file_path):
            return FileResponse(temp_file_path, media_type="video/mp4", filename="video.mp4")
        else:
            return {"error": "Failed to download video."}

    except subprocess.TimeoutExpired:
        return {"error": "Request timed out."}
    except Exception as e:
        return {"error": str(e)}
