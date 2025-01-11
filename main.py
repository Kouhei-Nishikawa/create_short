from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import os
from download_youtube import download_youtube_video
from transcribe_audio import transcribe_audio
from get_best_clip import get_best_clips
from create_short_clip import create_short_clips
import nltk
import zipfile

app = FastAPI()

@app.get("/")
def home():
    return {"message": "YouTube Shorts Generator API"}

@app.get("/create_short/")
def generate_short_clip(url: str = Query(..., description="YouTube video URL")):
    """YouTubeの動画をショートクリップ化"""
    try:
        video_path = download_youtube_video(url)
        transcript = transcribe_audio(video_path)
        best_clips = get_best_clips(video_path, transcript)

        short_clip_path = os.path.join("downloads", "short_clip.mp4")
        output_files = create_short_clips(video_path, best_clips, short_clip_path)

        if not output_files:
            return {"error": "No clips available"}

        zip_path = "clips_output/short_clips.zip"
        zip_file = create_zip_from_files(output_files, zip_path)

        return FileResponse(path=zip_file, filename="short_clips.zip", media_type="application/zip")

    except Exception as e:
        return {"error": str(e)}

def create_zip_from_files(file_paths, zip_output_path):
    """複数の動画ファイルをZIPにまとめる"""
    zip_dir = os.path.dirname(zip_output_path)
    if not os.path.exists(zip_dir):
        os.makedirs(zip_dir)  # ディレクトリが存在しない場合は作成

    with zipfile.ZipFile(zip_output_path, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, os.path.basename(file_path))  # ZIP内のファイル名を指定
    return zip_output_path

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)