from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os

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
        # base command
        cmd = ["yt-dlp", "-g", url]

        # add proxy if set
        if PROXY:
            cmd = ["yt-dlp", "--proxy", PROXY, "-g", url]

        # run yt-dlp
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # prevent server hang
        )

        # check for errors
        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        return {"video_url": result.stdout.strip()}

    except subprocess.TimeoutExpired:
        return {"error": "Request timed out."}
    except Exception as e:
        return {"error": str(e)}
