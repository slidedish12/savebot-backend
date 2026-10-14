import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import HttpUrl
import yt_dlp

app = FastAPI(title="SaveBot Pro API", version="1.0.0")

# Enable CORS so your Framer frontend can communicate with this backend securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your exact Framer domain (e.g., https://yourdomain.com)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_media_info(url: str):
    """
    Robust background extraction using yt-dlp.
    Handles format selection, metadata gathering, and fallback checks.
    """
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", "Downloaded File"),
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail"),
                "direct_url": info.get("url") or (info.get("requested_formats")[0].get("url") if info.get("requested_formats") else None),
                "ext": info.get("ext", "mp4")
            }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/resolve")
async def resolve_url(payload: dict):
    """
    API Endpoint called by your Framer frontend when a user submits a URL.
    """
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")
    
    # Extract metadata using the downloader bot engine
    result = extract_media_info(url)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=f"Failed to process URL: {result['error']}")
        
    return {
        "status": "success",
        "data": result
    }

@app.get("/")
def health_check():
    return {"status": "online", "bot": "SaveBot Pro Engine Active"}
