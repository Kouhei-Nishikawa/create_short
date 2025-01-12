from fastapi import FastAPI, Query
import os
from download_youtube import download_youtube_video
from get_best_clip import get_best_clips
from create_short_clip import create_short_clips

app = FastAPI()

@app.get("/")
def home():
    return {"message": "YouTube Shorts Generator API"}

# http://0.0.0.0:8000/create_short/?url=https://www.youtube.com/watch?v=XXXXXXXXXXX
@app.get("/create_short/")
def generate_short_clip(url: str = Query(..., description="YouTube video URL")):
    """YouTubeの動画をショートクリップ化"""
    try:
        video_path = download_youtube_video(url)
        best_clips = get_best_clips(video_path)

        short_clip_path = os.path.join("downloads", "short_clip")
        output_files = create_short_clips(video_path, best_clips, short_clip_path)

        if not output_files:
            return {"error": "No clips available"}

        return {"message": "Clips created successfully", "files": output_files}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)