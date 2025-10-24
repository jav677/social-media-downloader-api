from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess

app = FastAPI(title="Social Media Downloader API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read proxy from environment variable (example: "socks5://user:pass@host:port")
PROXY = os.getenv("PROXY")  # set this in Railway environment variables if needed

@app.get("/")
def home():
    return {"message": "Welcome to the Social Media Downloader API", "usage": "/api?url=VIDEO_LINK"}

@app.get("/api")
def download(url: str = Query(..., description="Paste any video URL from YouTube, TikTok, Instagram, Facebook")):
    try:
        cmd = ["yt-dlp", "-g", url]

        # If PROXY is set, add proxy option
        if PROXY:
            # yt-dlp uses --proxy <protocol://host:port>
            cmd = ["yt-dlp", "--proxy", PROXY, "-g", url]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # optional: avoid very long blocking
        )

        if result.returncode != 0:
            return {"error": result.stderr}

        return {"video_url": result.stdout.strip()}
    except subprocess.TimeoutExpired:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": str(e)}
