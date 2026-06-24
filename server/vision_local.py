from ultralytics import YOLO
from PIL import Image
import io


model = YOLO("yolo11n.pt")


def analyze_scene_local(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = model(image)

    objects = []
    person_present = False

    for result in results:
        names = result.names
        boxes = result.boxes

        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = names[cls_id]

            objects.append({
                "class": label,
                "confidence": round(conf, 3)
            })

            if label == "person" and conf >= 0.5:
                person_present = True

    social_context = "ready_for_reminder" if person_present else "no_person_visible"

    return {
        "person_present": person_present,
        "objects": objects,
        "social_context": social_context
    }