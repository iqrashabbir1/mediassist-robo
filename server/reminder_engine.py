import json
from pathlib import Path


SCHEDULE_PATH = Path("data/demo_schedule.json")


def load_schedule():
    with open(SCHEDULE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def check_due_medication(user_id: str, current_time: str):
    schedule = load_schedule()

    if schedule["user_id"] != user_id:
        return {
            "due_now": False,
            "reason": "Unknown user_id",
            "medication": None
        }

    for med in schedule["medications"]:
        if med["time"] == current_time:
            return {
                "due_now": True,
                "medication": med
            }

    return {
        "due_now": False,
        "medication": None
    }


def build_robot_reply(user_id: str, message: str, current_time: str, confirmation=None):
    result = check_due_medication(user_id, current_time)

    if confirmation == "taken":
        return {
            "due_now": False,
            "robot_action": "confirm_taken",
            "robot_reply": "Thank you. I have recorded that you confirmed taking your scheduled medication.",
            "safety_note": "This is only a reminder log, not medical advice."
        }

    if result["due_now"]:
        med = result["medication"]
        return {
            "due_now": True,
            "medication_label": med["label"],
            "scheduled_time": med["time"],
            "instruction": med["instruction"],
            "robot_action": "friendly_reminder",
            "robot_reply": (
                f"It is time for your scheduled {med['label']} {med['instruction']}. "
                "Please confirm once you have taken it."
            ),
            "safety_note": "This is only a reminder based on your saved schedule, not medical advice."
        }

    return {
        "due_now": False,
        "robot_action": "no_reminder_needed",
        "robot_reply": "There is no medication scheduled at this time.",
        "safety_note": "This is only based on the saved demo schedule."
    }