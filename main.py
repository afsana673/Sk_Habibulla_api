import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(
    title="Social Media Media Extractor API",
    description="Extract direct video and audio links using yt-dlp"
)

# যেকোনো ডোমেইন বা ফ্রন্টএন্ড থেকে কল করার অনুমতি (CORS Fix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _extract_media(url: str):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'noplaylist': True,
        'geo_bypass': True,
        # ব্লক এড়াতে আধুনিক ব্রাউজারের User-Agent ব্যবহার
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

@app.get("/")
async def root():
    return {
        "status": "running",
        "usage": "/download?url=VIDEO_URL&type=all (or video / audio)"
    }

@app.get("/download")
async def get_media_info(
    url: str = Query(..., description="Target social media video URL"),
    media_type: str = Query("all", enum=["all", "video", "audio"], description="Filter by video, audio, or all")
):
    try:
        # সার্ভার যেন ফ্রিজ না হয় তাই আলাদা থ্রেডে চালানো
        info = await asyncio.to_thread(_extract_media, url)

        # যদি লিঙ্কটি কোনো পোস্ট বা প্লেলিস্টের হয়, তবে প্রথম ভিডিওটি নেওয়া হবে
        if "entries" in info:
            entries = list(info["entries"])
            if not entries:
                raise HTTPException(status_code=404, detail="কোনো মিডিয়া পাওয়া যায়নি।")
            info = entries[0]

        formats = info.get("formats", [])
        
        video_with_audio = []
        audio_only = []

        for f in formats:
            f_url = f.get("url")
            if not f_url:
                continue

            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")
            ext = f.get("ext", "")

            # ১. ভিডিও + অডিও একসাথে আছে এমন ফাইল (Direct Download-এর জন্য সেরা)
            if vcodec != "none" and acodec != "none":
                video_with_audio.append({
                    "quality": f.get("format_note") or f"{f.get('height', 'Default')}p",
                    "ext": ext,
                    "height": f.get("height") or 0,
                    "filesize": f.get("filesize") or f.get("filesize_approx"),
                    "url": f_url
                })

            # ২. শুধুমাত্র অডিও ফাইল (MP3/M4A/WebM)
            elif vcodec == "none" and acodec != "none":
                audio_only.append({
                    "bitrate": f"{int(f.get('abr', 0))}kbps" if f.get('abr') else "Default",
                    "ext": ext,
                    "abr": f.get("abr") or 0,
                    "filesize": f.get("filesize") or f.get("filesize_approx"),
                    "url": f_url
                })

        # রেজোলিউশন এবং অডিও কোয়ালিটি অনুযায়ী সেরা ফাইলগুলোকে সবার উপরে সাজানো
        video_with_audio.sort(key=lambda x: x["height"], reverse=True)
        audio_only.sort(key=lambda x: x["abr"], reverse=True)

        # সেরা ভিডিও এবং সেরা অডিও লিঙ্ক সিলেক্ট করা
        best_video_url = video_with_audio[0]["url"] if video_with_audio else info.get("url")
        best_audio_url = audio_only[0]["url"] if audio_only else None

        # যদি আলাদা অডিও স্ট্রিম না থাকে (যেমন TikTok বা Instagram রিলস), তবে মূল লিঙ্কটিই ফলব্যাক হিসেবে দেওয়া
        if not best_audio_url and best_video_url:
            best_audio_url = best_video_url

        response_data = {
            "success": True,
            "platform": info.get("extractor_key"),
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
        }

        if media_type in ["all", "video"]:
            response_data["best_video_url"] = best_video_url
            response_data["video_formats"] = video_with_audio

        if media_type in ["all", "audio"]:
            response_data["best_audio_url"] = best_audio_url
            response_data["audio_formats"] = audio_only

        return response_data

    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"মিডিয়া পাওয়া যায়নি বা প্রাইভেট লিঙ্ক: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"সার্ভার সমস্যা: {str(e)}")
        
