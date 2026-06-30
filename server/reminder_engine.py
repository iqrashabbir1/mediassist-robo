import json
from pathlib import Path


SCHEDULE_PATH = Path("data/demo_schedule.json")


def load_schedule() -> dict:
    """Load the predefined demo medication schedule."""
    with open(SCHEDULE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def check_due_medication(user_id: str, current_time: str) -> dict:
    """
    Check whether any medication is due at the provided time.

    This function uses a predefined demo schedule only.
    It does not provide medical advice.
    """
    schedule = load_schedule()

    if schedule.get("user_id") != user_id:
        return {
            "due_now": False,
            "reason": "Unknown user_id",
            "medication": None,
        }

    for medication in schedule.get("medications", []):
        if medication.get("time") == current_time:
            return {
                "due_now": True,
                "medication": medication,
            }

    return {
        "due_now": False,
        "medication": None,
    }


def build_robot_reply(
    user_id: str,
    message: str,
    current_time: str,
    confirmation: str | None = None,
) -> dict:
    """
    Build a safe social robot reminder response.

    The robot only reminds based on a saved schedule.
    It does not diagnose, prescribe, or change medication.
    """
    result = check_due_medication(user_id=user_id, current_time=current_time)

    if confirmation == "taken":
        return {
            "due_now": False,
            "robot_action": "confirm_taken",
            "robot_reply": (
                "Thank you. I have recorded that you confirmed taking your "
                "scheduled medication."
            ),
            "safety_note": "This is only a reminder log, not medical advice.",
        }

    if result["due_now"]:
        medication = result["medication"]

        return {
            "due_now": True,
            "medication_label": medication["label"],
            "scheduled_time": medication["time"],
            "instruction": medication["instruction"],
            "robot_action": "friendly_reminder",
            "robot_reply": (
                f"It is time for your scheduled {medication['label']} "
                f"{medication['instruction']}. Please confirm once you have "
                "taken it."
            ),
            "safety_note": (
                "This is only a reminder based on your saved schedule, "
                "not medical advice."
            ),
        }

    return {
        "due_now": False,
        "robot_action": "no_reminder_needed",
        "robot_reply": "There is no medication scheduled at this time.",
        "safety_note": "This is only based on the saved demo schedule.",
    }
