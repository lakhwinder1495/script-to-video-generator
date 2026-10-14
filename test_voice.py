
import pyttsx3
from pathlib import Path
import time

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

audio_path = output_dir / "voice_test.wav"

print("Initializing voice engine...")
engine = pyttsx3.init()
print("Voice engine initialized.")

engine.setProperty("rate", 150)
engine.save_to_file(
    "Hello! This is a short voice generation test.",
    str(audio_path)
)

print("Generating voice...")
start_time = time.time()

engine.runAndWait()
engine.stop()

print(f"Finished in {time.time() - start_time:.1f} seconds.")
print(f"Audio file exists: {audio_path.exists()}")
