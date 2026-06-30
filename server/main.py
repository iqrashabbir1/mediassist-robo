import time
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from server.reminder_engine import build_robot_reply
from server.vision_local import analyze_scene_local
from server.dialogue import generate_social_reply
from server.speech import text_to_speech


app = FastAPI(
    title="mediassist-robo",
    description=(
        "Cloud-local social robot service for medication reminders "
        "and companion check-ins."
    ),
    version="1.0",
)


class ReminderRequest(BaseModel):
    user_id: str = "demo_user"
    message: str = "Do I need to take anything now?"
    current_time: str = "09:00"
    confirmation: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "demo_user",
                "message": "Do I need to take anything now?",
                "current_time": "09:00",
                "confirmation": None,
            }
        }
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to mediassist-robo",
        "description": (
            "Cloud-local social robot service for medication reminders "
            "and companion check-ins."
        ),
        "available_browser_endpoints": {
            "health": "http://127.0.0.1:8000/health",
            "docs": "http://127.0.0.1:8000/docs",
            "medication_due_demo": "http://127.0.0.1:8000/reminder/demo",
            "medication_no_due_demo": "http://127.0.0.1:8000/reminder/demo/no-due",
            "medication_confirmed_demo": (
                "http://127.0.0.1:8000/reminder/demo/confirmed"
            ),
            "scene_demo": "http://127.0.0.1:8000/scene/demo",
        },
        "note": (
            "POST endpoints such as /reminder/assist and /scene/analyze "
            "should be tested through /docs or curl."
        ),
    }


@app.get("/health")
def health():
    start = time.time()

    return {
        "status": "ok",
        "service": "mediassist-robo",
        "version": "1.0",
        "local_component": "YOLO",
        "remote_ai": "Gemini",
        "latency_ms": round((time.time() - start) * 1000, 2),
    }


@app.get("/reminder/demo")
def reminder_demo():
    """
    Browser-friendly demo endpoint for medication due case.
    """
    reminder_context = build_robot_reply(
        user_id="demo_user",
        message="Do I need to take anything now?",
        current_time="09:00",
        confirmation=None,
    )

    reminder_context["demo_note"] = (
        "This is a browser-friendly GET demo showing medication due. "
        "The full JSON endpoint is POST /reminder/assist."
    )

    return reminder_context


@app.get("/reminder/demo/no-due")
def reminder_demo_no_due():
    """
    Browser-friendly demo endpoint for no medication due case.
    """
    reminder_context = build_robot_reply(
        user_id="demo_user",
        message="Do I need to take anything now?",
        current_time="14:00",
        confirmation=None,
    )

    reminder_context["demo_note"] = (
        "This is a browser-friendly GET demo showing no medication due."
    )

    return reminder_context


@app.get("/reminder/demo/confirmed")
def reminder_demo_confirmed():
    """
    Browser-friendly demo endpoint for user confirmation case.
    """
    reminder_context = build_robot_reply(
        user_id="demo_user",
        message="I have taken it.",
        current_time="09:00",
        confirmation="taken",
    )

    reminder_context["demo_note"] = (
        "This is a browser-friendly GET demo showing user confirmation."
    )

    return reminder_context


@app.post("/reminder/assist")
def reminder_assist(request: ReminderRequest):
    """
    Main medication reminder endpoint.

    Test through:
    http://127.0.0.1:8000/docs
    """
    reminder_context = build_robot_reply(
        user_id=request.user_id,
        message=request.message,
        current_time=request.current_time,
        confirmation=request.confirmation,
    )

    try:
        ai_reply = generate_social_reply(
            user_message=request.message,
            reminder_context=reminder_context,
        )

        reminder_context["ai_robot_reply"] = ai_reply
        reminder_context["cloud_ai_status"] = "Gemini response generated successfully."

    except Exception:
        reminder_context["ai_robot_reply"] = reminder_context["robot_reply"]
        reminder_context["cloud_ai_status"] = (
            "Gemini unavailable or quota exceeded; fallback rule-based reply used."
        )

    return reminder_context


@app.post("/scene/analyze")
async def scene_analyze(file: UploadFile = File(...)):
    """
    Main local vision endpoint using YOLO.

    This is a POST endpoint. Test through /docs or with curl.
    """
    image_bytes = await file.read()
    result = analyze_scene_local(image_bytes)

    if result["person_present"]:
        result["robot_action"] = "person_visible_continue_interaction"
        result["robot_reply"] = (
            "I can see someone nearby. I am ready to provide the reminder."
        )
    else:
        result["robot_action"] = "wait_or_call_again"
        result["robot_reply"] = (
            "I cannot see the user clearly. I will wait before giving the reminder."
        )

    return result


@app.get("/scene/demo")
def scene_demo():
    """
    Browser-friendly GET endpoint for local YOLO scene analysis.

    It uses samples/demo_scene.jpg.
    """
    image_path = "samples/demo_scene.jpg"

    try:
        with open(image_path, "rb") as file:
            image_bytes = file.read()

        result = analyze_scene_local(image_bytes)

        if result["person_present"]:
            result["robot_action"] = "person_visible_continue_interaction"
            result["robot_reply"] = (
                "I can see someone nearby. I am ready to provide the reminder."
            )
        else:
            result["robot_action"] = "wait_or_call_again"
            result["robot_reply"] = (
                "I cannot see the user clearly. I will wait before giving the reminder."
            )

        result["demo_note"] = (
            "This is a browser-friendly GET demo using samples/demo_scene.jpg. "
            "The full file-upload endpoint is POST /scene/analyze."
        )

        return result

    except FileNotFoundError:
        return {
            "error": "samples/demo_scene.jpg not found.",
            "fix": (
                "Copy an image to samples/demo_scene.jpg, then reload this endpoint."
            ),
        }


@app.post("/speak")
def speak(request: ReminderRequest):
    """
    Text-to-speech endpoint.

    It creates an MP3 file from the robot reminder reply.
    """
    reminder_context = build_robot_reply(
        user_id=request.user_id,
        message=request.message,
        current_time=request.current_time,
        confirmation=request.confirmation,
    )

    try:
        audio_path = text_to_speech(reminder_context["robot_reply"])

        return {
            "robot_reply": reminder_context["robot_reply"],
            "audio_path": audio_path,
            "tts_status": "MP3 file generated successfully.",
        }

    except Exception as error:
        return {
            "robot_reply": reminder_context["robot_reply"],
            "audio_path": None,
            "tts_status": f"Text-to-speech failed: {error}",
        }
