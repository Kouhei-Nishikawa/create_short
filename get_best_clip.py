from clipsai import ClipFinder, Transcriber

def get_best_clips(video_path: str, max_clips=10, clip_length=60) -> list:
    """盛り上がり部分の 1 分間の動画クリップを複数抽出"""

    transcriber = Transcriber()
    transcription = transcriber.transcribe(audio_file_path=video_path)

    transcription = split_sentences_with_timestamps(
        transcription.get_sentence_info()[0]["sentence"],
        transcription.get_sentence_info()[0]["start_time"],
        transcription.get_sentence_info()[0]["end_time"]
    )

    clipfinder = ClipFinder()
    clips = clipfinder.find_clips(transcription=transcription)

    if not clips:
        return [(0, clip_length)]  # クリップが見つからなかった場合、最初の60秒を返す

    # スコアではなくクリップの長さでソート（長い順）
    clips.sort(key=lambda x: x.end_time - x.start_time, reverse=True)

    best_clips = []
    for clip in clips[:max_clips]:
        start_time = clip.start_time
        end_time = min(clip.start_time + clip_length, clip.end_time)

        best_clips.append((start_time, end_time))

    return best_clips

import re
import nltk
nltk.download("punkt")
from nltk.tokenize import sent_tokenize

# **Transcription クラスを定義**
class Transcription:
    def __init__(self, sentences_info):
        self.sentences_info = sentences_info
        self.end_time = sentences_info[-1]["end_time"] if sentences_info else 0.0  # 最後の文の end_time をセット

    def get_sentence_info(self):
        return self.sentences_info

    def get_char_info(self):
        return "".join([info["sentence"] for info in self.sentences_info])

# **修正関数**
def split_sentences_with_timestamps(transcription_text: str, start_time: float, end_time: float) -> Transcription:
    """
    長文を文単位に分割し、それぞれに時間情報を割り当てる
    """
    sentences = split_sentences_manual(transcription_text)  # 文章を適切に分割

    sentence_info_list = []

    total_chars = len(transcription_text)  # 文字数
    avg_time_per_char = (end_time - start_time) / total_chars if total_chars > 0 else 0  # 1 文字あたりの時間

    current_start_time = start_time
    current_start_char = 0

    for sentence in sentences:
        sentence_length = len(sentence)
        sentence_end_time = current_start_time + (sentence_length * avg_time_per_char)
        sentence_end_char = current_start_char + sentence_length

        sentence_info_list.append({
            "sentence": sentence,
            "start_time": current_start_time,
            "end_time": sentence_end_time,
            "start_char": current_start_char,
            "end_char": sentence_end_char
        })

        # 次の文の開始時間と文字位置を更新
        current_start_time = sentence_end_time
        current_start_char = sentence_end_char

    # **Transcription 型に変換**
    return Transcription(sentence_info_list)

def split_sentences_manual(text: str):
    """
    句点（。）または改行（\n）で文を分割
    """
    sentences = re.split(r'(?<=[。！？])\s*', text)  # 句点・感嘆符・改行を基準に分割
    return [s.strip() for s in sentences if s.strip()]  # 空白を削除し、空の要素を除去

