import os
import json
from pathlib import Path
from django.conf import settings

# Load YOLO model once at startup
_model = None

def get_model():
    global _model
    if _model is None:
        from ultralytics import YOLO
        model_path = settings.YOLO_MODEL_PATH
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found at {model_path}. "
                "Please download best.pt and place it in api/models/"
            )
        _model = YOLO(str(model_path))
    return _model


CLASS_NAMES = {
    0: 'Caries',
    1: 'Gingivitis',
    2: 'Tartar',
    3: 'Mouth Ulcer',
}

CLASS_DESCRIPTIONS = {
    'Caries': 'Tooth decay caused by bacterial acids eroding enamel. Requires filling or restoration.',
    'Gingivitis': 'Inflammation of the gums due to plaque buildup. Treatable with professional cleaning.',
    'Tartar': 'Hardened plaque (calculus) on teeth. Requires professional scaling to remove.',
    'Mouth Ulcer': 'Painful sores on the soft tissues inside the mouth. Usually heals within 1-2 weeks.',
}


def run_detection(image_path: str) -> dict:
    """
    Run YOLOv8 detection on a dental image.
    Returns a dict with detections and annotated image path.
    """
    model = get_model()
    results = model(image_path, conf=0.25)
    result = results[0]

    detections = []
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = CLASS_NAMES.get(class_id, f'Unknown_{class_id}')
        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]

        detections.append({
            'class_id': class_id,
            'class_name': class_name,
            'confidence': round(confidence * 100, 2),
            'bbox': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2},
            'description': CLASS_DESCRIPTIONS.get(class_name, ''),
        })

    # Save annotated image
    base_name = Path(image_path).stem
    processed_dir = Path(settings.MEDIA_ROOT) / 'processed' / base_name
    processed_dir.mkdir(parents=True, exist_ok=True)
    annotated_path = processed_dir / f"{base_name}_detected.jpg"
    result.save(str(annotated_path))

    # Save detection JSON
    detection_dir = Path(settings.MEDIA_ROOT) / 'detections'
    detection_dir.mkdir(parents=True, exist_ok=True)
    json_path = detection_dir / f"{base_name}.json"
    with open(json_path, 'w') as f:
        json.dump(detections, f, indent=2)

    return {
        'detections': detections,
        'annotated_image_path': str(annotated_path),
        'total_detected': len(detections),
        'conditions_found': list(set(d['class_name'] for d in detections)),
    }
