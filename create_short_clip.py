import subprocess
import os

def create_short_clips(video_path: str, clips: list, output_dir: str) -> list:
    """
    複数の動画クリップを FFmpeg でカットし、YouTube Shorts 用にリサイズ

    :param video_path: 元動画のパス
    :param clips: [(start_time, end_time), ...] のリスト
    :param output_dir: 切り抜いた動画の保存先ディレクトリ
    :return: 出力ファイルのリスト
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 出力フォルダが存在しない場合は作成

    output_files = []

    for idx, (start_time, end_time) in enumerate(clips):
        output_path = os.path.join(output_dir, f"clip_{idx+1}.mp4")

        # FFmpeg でクリップを作成しリサイズ
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", str(start_time), "-to", str(end_time),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "copy", output_path
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output_files.append(output_path)
            print(f"✅ {output_path} を作成しました")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ クリップ作成に失敗: {output_path}")
            print(f"エラー: {e.stderr.decode()}")

    return output_files
