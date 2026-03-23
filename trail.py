# import assemblyai as aai
# from dotenv import load_dotenv
# import os

# load_dotenv()

# aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# transcriber = aai.Transcriber()

# config = aai.TranscriptionConfig(
#     speaker_labels=True,
#     speech_models=["universal"]   # ✅ NEW FORMAT
# )

# transcript = transcriber.transcribe(
#     "Recording.mp3",
#     config=config
# )

# print(transcript.text)


import assemblyai as aai
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os

load_dotenv()

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

transcriber = aai.Transcriber()

config = aai.TranscriptionConfig(
    speaker_labels=True,
    language_detection=True,
    speech_models=["universal-2"]
)

print("Processing file...")

transcript = transcriber.transcribe(
    "Screen Recording 2026-01-13 190332.mp4",
    config=config
)

print("\n✅ English Transcript:\n")

for u in transcript.utterances:
    english_text = GoogleTranslator(source="auto", target="en").translate(u.text)
    print(f"Speaker {u.speaker}: {english_text}")