"""真实本地语音转写；要求预先准备模型目录，不默认下载模型。"""
import argparse
import os
import wave
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("audio", type=Path, help="有权处理的PCM WAV音频，最多60秒")
args = parser.parse_args()
model_path = os.environ.get("WHISPER_MODEL_DIR")
if not model_path or not Path(model_path).is_dir():
    raise SystemExit("请设置WHISPER_MODEL_DIR指向本地转换模型目录")
with wave.open(str(args.audio), "rb") as audio:
    duration = audio.getnframes() / audio.getframerate()
    if not 0 < duration <= 60:
        raise SystemExit("音频为空或超过60秒教学限制")
# 可选依赖延迟导入，默认课程验证不会要求下载模型。
from faster_whisper import WhisperModel

model = WhisperModel(model_path, device="cpu", compute_type="int8", local_files_only=True)
segments, info = model.transcribe(str(args.audio), beam_size=1)
print("识别语言：", info.language)
for segment in segments:
    print(f"{segment.start:.2f}-{segment.end:.2f}: {segment.text}")
# 转写有不确定性：关键业务字段需要校验或人工确认。
