import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_social_reply(user_message: str, reminder_context: dict):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a polite social robot assistant for medication reminders.

Safety rules:
- Do not give medical advice.
- Do not diagnose.
- Do not change dosage.
- Only remind based on the provided schedule.
- Keep the response short, friendly, and clear.

User message:
{user_message}

Reminder context:
{reminder_context}

Generate one short robot reply.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text