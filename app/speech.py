import assemblyai as aai
from deep_translator import GoogleTranslator
import os
from dotenv import load_dotenv

load_dotenv()

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

transcriber = aai.Transcriber()

config = aai.TranscriptionConfig(
    speaker_labels=True,
    language_detection=True,
    speech_models=["universal-2"]
)

def transcribe_call(file_path: str):

    transcript = transcriber.transcribe(file_path, config=config)

    if transcript.status != "completed":
        raise Exception("Transcription failed")

    utterances = []

    for u in transcript.utterances:
        text = GoogleTranslator(source="auto", target="en").translate(u.text)

        utterances.append({
            "speaker": u.speaker,
            "text": text
        })

    return utterances