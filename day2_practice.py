
from pathlib import Path

video_path = Path("first_video.mp4")
audio_path = Path("voiceover.wav")

if video_path.exists() and audio_path.exists():
    print("Project files are ready!")
else:
    print("Some project files are missing.")
