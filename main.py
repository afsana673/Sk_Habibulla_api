from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI()

@app.get("/download")
def get_video_info(url: str):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "duration": info.get("duration"),
                "download_url": info.get("url"),
                "thumbnail": info.get("thumbnail")
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
      
