from gtts import gTTS
from pathlib import Path
import uuid


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def text_to_speech(text: str):
    filename = OUTPUT_DIR / f"reply_{uuid.uuid4().hex}.mp3"
    tts = gTTS(text=text, lang="en")
    tts.save(str(filename))
    return str(filename)