# Final formatted source file
from pathlib import Path
import uuid
from gtts import gTTS


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def text_to_speech(text: str) -> str:
    """
    Convert robot reply text into an MP3 file using gTTS.

    The generated file is saved in the local outputs/ folder.
    """
    filename = OUTPUT_DIR / f"reply_{uuid.uuid4().hex}.mp3"

    tts = gTTS(text=text, lang="en")
    tts.save(str(filename))

    return str(filename)
