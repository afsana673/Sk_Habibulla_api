import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# HTML সাইট বা অন্য যেকোনো ডোমেইন থেকে কল করার অনুমতি (CORS Fix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _extract_video(url: str):
    ydl_opts = {
        # ভিডিও ও অডিও একসাথে থাকা বেস্ট ফাইলটি খোঁজার চেষ্টা করবে
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

@app.get("/download")
async def get_video_info(url: str = Query(..., description="Target video URL")):
    try:
        # yt_dlp-এর ভারী প্রসেসটি আলাদা থ্রেডে চালানো যেন সার্ভার ফ্রিজ না হয়
        info = await asyncio.to_thread(_extract_video, url)

        # সরাসরি লিঙ্ক না পেলে ফরম্যাট তালিকা থেকে সেরা লিঙ্কটি খুঁজে বের করা
        download_url = info.get("url")
        if not download_url and info.get("formats"):
            download_url = info["formats"][-1].get("url")

        return {
            "title": info.get("title"),
            "duration": info.get("duration"),
            "download_url": download_url,
            "thumbnail": info.get("thumbnail")
        }
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"ভিডিও পাওয়া যায়নি: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"সার্ভার সমস্যা: {str(e)}")
        
