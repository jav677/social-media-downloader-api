from fastapi import FastAPI, Query
import subprocess

app = FastAPI(title="Social Media Downloader API", version="1.0")

@app.get("/")
def home():
    return {"message": "Welcome to the Social Media Downloader API", "usage": "/api?url=VIDEO_LINK"}

@app.get("/api")
def download(url: str = Query(..., description="Paste any video URL from YouTube, TikTok, Instagram, Facebook")):
    try:
        # yt-dlp سے ویڈیو لنک نکالنا
        result = subprocess.run(
            ["yt-dlp", "-g", url],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return {"error": result.stderr}
        return {"video_url": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}
