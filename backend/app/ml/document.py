"""Document forgery detection using a fine-tuned ViT plus PDF integrity checks."""

from __future__ import annotations

import io
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageChops
from transformers import AutoImageProcessor, AutoModelForImageClassification


DOCUMENT_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
DOCUMENT_EXTS = DOCUMENT_IMAGE_EXTS | {".pdf"}
DOCUMENT_MODEL_ID = "zodumair/document-forgery-detector"


def _ela_blend(image: Image.Image, quality: int = 90, alpha: float = 0.30) -> Image.Image:
    rgb = image.convert("RGB")
    buf = io.BytesIO()
    rgb.save(buf, "JPEG", quality=quality)
    buf.seek(0)
    recompressed = Image.open(buf).convert("RGB")
    diff = ImageChops.difference(rgb, recompressed)
    extrema = diff.getextrema()
    max_diff = max(channel[1] for channel in extrema) or 1
    ela = diff.point(lambda px: min(255, int(px * (255.0 / max_diff) * 1.5)))
    return Image.blend(rgb, ela, alpha=alpha)


class DocumentForgeryDetector:
    def __init__(self, model_id: str = DOCUMENT_MODEL_ID, device: str = "cpu"):
        self.model_id = model_id
        self.device = torch.device(device)
        self.processor = AutoImageProcessor.from_pretrained(model_id)
        self.model = AutoModelForImageClassification.from_pretrained(model_id)
        self.model.to(self.device)
        self.model.eval()

        labels = {int(k): str(v).lower() for k, v in self.model.config.id2label.items()}
        fake_candidates = [i for i, label in labels.items() if any(x in label for x in ("fake", "forg", "tamper", "fraud"))]
        real_candidates = [i for i, label in labels.items() if any(x in label for x in ("real", "authentic", "genuine"))]
        if not fake_candidates or not real_candidates:
            raise RuntimeError(f"Document model labels are not understood: {labels}")
        self.fake_index = fake_candidates[0]
        self.real_index = real_candidates[0]
        self.labels = labels

    def predict_image(self, image_rgb: np.ndarray) -> dict:
        image = Image.fromarray(image_rgb.astype(np.uint8)).convert("RGB")
        blended = _ela_blend(image)
        inputs = self.processor(images=blended, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            probs = F.softmax(self.model(**inputs).logits, dim=-1)[0]
        fake_probability = float(probs[self.fake_index].item())
        real_probability = float(probs[self.real_index].item())
        return {
            "fake_probability": fake_probability,
            "real_probability": real_probability,
            "confidence": max(fake_probability, real_probability),
            "label": "FAKE" if fake_probability >= real_probability else "REAL",
            "model_id": self.model_id,
            "model_labels": self.labels,
        }


def _pdf_structure(path: Path) -> dict:
    try:
        import pymupdf

        doc = pymupdf.open(str(path))
        meta = doc.metadata or {}
        pages = len(doc)
        text_chars = 0
        image_count = 0
        font_names: set[str] = set()
        image_xrefs: list[int] = []
        duplicate_text_blocks = 0
        text_block_count = 0
        page_metrics: list[dict] = []

        for page_number, page in enumerate(doc, 1):
            text = page.get_text("text")
            blocks = page.get_text("blocks")
            text_chars += len(text)
            text_block_count += len(blocks)

            normalized_blocks = []
            for block in blocks:
                if len(block) >= 5 and block[4].strip():
                    normalized_blocks.append(block[4].strip().lower())
            counts: dict[str, int] = {}
            for block_text in normalized_blocks:
                counts[block_text] = counts.get(block_text, 0) + 1
            duplicate_text_blocks += sum(max(0, count - 1) for count in counts.values())

            page_images = page.get_images(full=True)
            image_count += len(page_images)
            for image in page_images:
                if image and image[0]:
                    image_xrefs.append(int(image[0]))

            for font in page.get_fonts(full=True):
                if font and font[3]:
                    font_names.add(str(font[3]))

            page_metrics.append({
                "page": page_number,
                "text_characters": len(text),
                "text_blocks": len(blocks),
                "embedded_images": len(page_images),
            })

        xref_count = getattr(doc, "xref_length", lambda: 0)()
        repaired = bool(getattr(doc, "is_repaired", False))
        unique_image_xrefs = len(set(image_xrefs))
        duplicate_image_refs = max(0, len(image_xrefs) - unique_image_xrefs)
        doc.close()

        suspicious = []
        if repaired:
            suspicious.append("PDF parser reported a repaired/corrected structure.")
        if pages and image_count > pages * 25:
            suspicious.append("Unusually high embedded-image count per page.")
        if duplicate_image_refs:
            suspicious.append("Repeated embedded-image references were found; this can be normal in templates but is worth review.")
        if duplicate_text_blocks:
            suspicious.append("Repeated text blocks were found; this can be normal in forms but may indicate copy/paste or overlay editing.")
        if meta.get("creationDate") and meta.get("modDate") and meta["creationDate"] != meta["modDate"]:
            suspicious.append("Creation and modification timestamps differ.")

        provenance_notes = []
        software = str(meta.get("producer") or meta.get("creator") or "").strip()
        if software:
            provenance_notes.append(f"PDF producer/creator metadata: {software}")
        else:
            provenance_notes.append("No producer/creator metadata was exposed by the PDF parser.")
        if meta.get("creationDate") and meta.get("modDate"):
            provenance_notes.append("Creation and modification timestamps are both present.")
        elif meta.get("creationDate") or meta.get("modDate"):
            provenance_notes.append("Only one of creation/modification timestamps is present.")

        return {
            "pages": pages,
            "text_characters": text_chars,
            "text_blocks": text_block_count,
            "duplicate_text_blocks": duplicate_text_blocks,
            "embedded_images": image_count,
            "unique_embedded_images": unique_image_xrefs,
            "duplicate_image_references": duplicate_image_refs,
            "embedded_fonts": sorted(font_names)[:100],
            "xref_objects": xref_count,
            "parser_repaired": repaired,
            "metadata": meta,
            "provenance_notes": provenance_notes,
            "page_metrics": page_metrics,
            "structural_flags": suspicious,
        }
    except Exception as exc:
        return {"structural_error": str(exc)}


def _render_pdf(path: Path, max_pages: int = 8) -> list[np.ndarray]:
    import pymupdf

    doc = pymupdf.open(str(path))
    pages: list[np.ndarray] = []
    for i in range(min(len(doc), max_pages)):
        pix = doc[i].get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        pages.append(arr[:, :, :3].copy())
    doc.close()
    return pages


def analyze_document(path: str | Path, detector: DocumentForgeryDetector, max_pages: int = 8) -> dict:
    path = Path(path)
    ext = path.suffix.lower()
    if ext == ".pdf":
        pages = _render_pdf(path, max_pages=max_pages)
        structure = _pdf_structure(path)
    elif ext in DOCUMENT_IMAGE_EXTS:
        pages = [np.array(Image.open(path).convert("RGB"))]
        structure = {"format": ext.lstrip(".")}
    else:
        raise ValueError(f"Unsupported document type: {ext}")

    page_results = []
    for index, page in enumerate(pages, 1):
        result = detector.predict_image(page)
        gray = cv2.cvtColor(page, cv2.COLOR_RGB2GRAY).astype(np.float32)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = gray - blur
        page_results.append({
            "page": index,
            **result,
            "noise_std": round(float(noise.std()), 4),
            "resolution": [int(page.shape[1]), int(page.shape[0])],
        })

    fake_probs = [float(x["fake_probability"]) for x in page_results]
    max_fake = max(fake_probs) if fake_probs else 0.5
    mean_fake = float(np.mean(fake_probs)) if fake_probs else 0.5
    # Page-level evidence: prioritize the most suspicious page, while retaining a
    # smaller contribution from the document-wide mean.
    fake_probability = float(np.clip(0.70 * max_fake + 0.30 * mean_fake, 0.0, 1.0))
    prediction = "FAKE" if fake_probability >= 0.5 else "REAL"

    return {
        "prediction": prediction,
        "confidence": fake_probability if prediction == "FAKE" else 1.0 - fake_probability,
        "fake_probability": fake_probability,
        "model_id": detector.model_id,
        "pages_analyzed": len(page_results),
        "page_results": page_results,
        "structure": structure,
        "signals": {
            "max_page_fake_probability": round(max_fake, 4),
            "mean_page_fake_probability": round(mean_fake, 4),
            "structural_flag_count": len(structure.get("structural_flags", [])),
            "pages_analyzed": len(page_results),
        },
    }
