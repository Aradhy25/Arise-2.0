"""Non-authoritative provenance signals for media originality analysis."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ExifTags


def analyze_image_provenance(path: str | Path) -> dict:
    path = Path(path)
    result = {
        "format": path.suffix.lower().lstrip("."),
        "file_size_bytes": path.stat().st_size if path.exists() else None,
        "exif": {},
        "editing_software": None,
        "camera_make": None,
        "camera_model": None,
        "timestamp": None,
        "provenance_notes": [],
    }
    try:
        with Image.open(path) as img:
            raw = img.getexif()
            tags = {}
            for key, value in raw.items():
                tags[ExifTags.TAGS.get(key, str(key))] = str(value)
            result["exif"] = tags
            result["editing_software"] = tags.get("Software")
            result["camera_make"] = tags.get("Make")
            result["camera_model"] = tags.get("Model")
            result["timestamp"] = tags.get("DateTimeOriginal") or tags.get("DateTime")
            if not tags:
                result["provenance_notes"].append("No EXIF metadata was present.")
            if result["editing_software"]:
                result["provenance_notes"].append("Software metadata identifies the application that last wrote EXIF.")
            if result["camera_make"] and result["camera_model"]:
                result["provenance_notes"].append("Camera make/model metadata is present, but metadata can be copied or altered.")
    except Exception as exc:
        result["provenance_notes"].append(f"Metadata parsing failed: {exc}")
    return result
