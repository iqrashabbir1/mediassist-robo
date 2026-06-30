from PIL import Image
import io


_yolo_model = None


def get_yolo_model():
    """
    Load YOLO lazily so the FastAPI app can start even before the model is loaded.

    The first call may download yolo11n.pt if it is not already available.
    """
    global _yolo_model

    if _yolo_model is None:
        from ultralytics import YOLO

        _yolo_model = YOLO("yolo11n.pt")

    return _yolo_model


def analyze_scene_local(image_bytes: bytes) -> dict:
    """
    Analyze an image using local YOLO detection.

    Returns whether a person is visible and a list of detected objects.
    This local component supports the social robot check-in scenario.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    model = get_yolo_model()
    results = model(image)

    objects = []
    person_present = False

    for result in results:
        names = result.names
        boxes = result.boxes

        for box in boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            label = names[class_id]

            objects.append(
                {
                    "class": label,
                    "confidence": round(confidence, 3),
                }
            )

            if label == "person" and confidence >= 0.5:
                person_present = True

    social_context = "ready_for_reminder" if person_present else "no_person_visible"

    return {
        "person_present": person_present,
        "objects": objects,
        "social_context": social_context,
    }
