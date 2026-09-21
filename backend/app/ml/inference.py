"""Unified inference engine for images, videos, and live frames."""

from __future__ import annotations

import base64
import time
import uuid
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from app.core.config import get_settings
from app.ml.audio import AUDIO_EXTS, analyze_audio
from app.ml.audio_detector import AudioDeepfakeDetector
from app.ml.av_sync import estimate_av_consistency
from app.ml.document import DOCUMENT_EXTS, DocumentForgeryDetector, analyze_document
from app.ml.provenance import analyze_image_provenance
from app.ml.architectures.factory import (
    HuggingFaceDeepfakeDetector,
    build_model,
    load_checkpoint,
)
from app.ml.face_detector import FaceDetector
from app.ml.forensics import forensic_fake_probability, forensic_heatmap
from app.ml.gradcam import GradCAM, find_last_conv, overlay_heatmap
from app.ml.preprocessing import read_image, to_tensor
from app.ml.risk import explain_result, file_sha256, risk_level
from app.ml.video import sample_video_frames


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
ALL_MEDIA_EXTS = IMAGE_EXTS | VIDEO_EXTS | AUDIO_EXTS | DOCUMENT_EXTS


@dataclass
class InferenceResult:
    prediction: str
    confidence: float
    model_name: str
    model_version: str
    media_type: str
    frames_analyzed: int
    suspicious_frames: int
    processing_time_sec: float
    heatmap_path: str | None = None
    heatmap_b64: str | None = None
    mode: str = "pytorch"
    details: dict = field(default_factory=dict)


class DeepfakeEngine:
    def __init__(self, model_name: str | None = None):
        self.settings = get_settings()
        requested_model = model_name or self.settings.default_model
        self.device = torch.device(self.settings.device)
        self.face_detector = FaceDetector()
        self.model = None
        self.hf_detector = None
        self.has_finetuned_weights = False
        self.detector_backend = "forensic-heuristic"
        self.audio_detector = None
        self.document_detector = None

        # The old EfficientNet path could run an ImageNet backbone with a random
        # binary head and still report 100% confidence. That is not a detector.
        # By default use a genuinely fine-tuned Real/Fake classifier from HF.
        if self.settings.detector_backend.lower() == "huggingface":
            try:
                self.hf_detector = HuggingFaceDeepfakeDetector(
                    self.settings.hf_model_id, self.device
                )
                self.model_name = "vit-deepfake"
                self.model_version = "hf-dima806"
                self.detector_backend = "huggingface-vit"
            except Exception:
                self.hf_detector = None
                self.model_name = "forensic-fallback"
                self.model_version = "1.1-heuristic"
        else:
            self.model_name = requested_model
            self.model = build_model(self.model_name, pretrained=True)
            weights = self.settings.weights_dir / f"{self.model_name.replace('-', '_')}.pth"
            self.model, self.has_finetuned_weights = load_checkpoint(
                self.model, weights, self.device
            )
            if self.has_finetuned_weights and self.settings.use_local_checkpoint:
                self.model_version = "1.1-local-finetuned"
                self.detector_backend = "local-finetuned"
            else:
                # Never use an ImageNet/random binary head as a deepfake detector.
                self.model = None
                self.model_version = "1.1-heuristic"
                self.has_finetuned_weights = False
                self.detector_backend = "forensic-heuristic"

    def predict_file(self, path: str | Path, model_override: str | None = None) -> InferenceResult:
        path = Path(path)
        ext = path.suffix.lower()
        if model_override and model_override != self.model_name and self.settings.detector_backend.lower() != "huggingface":
            return DeepfakeEngine(model_override).predict_file(path)

        if ext in IMAGE_EXTS:
            result = self.predict_image(path)
        elif ext in VIDEO_EXTS:
            result = self.predict_video(path)
        elif ext in AUDIO_EXTS:
            result = self.predict_audio(path)
        elif ext in DOCUMENT_EXTS:
            result = self.predict_document(path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        return enrich_result(result, path)

    def predict_ensemble(self, path: str | Path, models: list[str] | None = None) -> InferenceResult:
        """Run multiple configured detectors and vote on their probabilities."""
        path = Path(path)
        ext = path.suffix.lower()
        if ext in AUDIO_EXTS:
            return self.predict_file(path)

        if self.settings.detector_backend.lower() == "huggingface":
            # There is one validated deepfake detector in the default runtime.
            # Do not pretend three ImageNet heads are independent detectors.
            result = self.predict_file(path)
            result.model_name = "vit-deepfake"
            result.model_version = "hf-dima806"
            result.mode = "huggingface-vit"
            result.details["aggregation"] = "single_validated_detector"
            return result

        models = models or ["efficientnet", "xception", "vit"]
        t0 = time.perf_counter()
        votes: list[InferenceResult] = []
        for name in models:
            try:
                votes.append(DeepfakeEngine(name).predict_file(path))
            except Exception:
                continue
        if not votes:
            raise ValueError("Ensemble failed — no model produced a result")

        probs = [float(v.details.get("fake_probability", 0.5)) for v in votes]
        avg = float(np.mean(probs))
        fake_votes = sum(1 for v in votes if v.prediction == "FAKE")
        prediction = "FAKE" if fake_votes > len(votes) / 2 or avg >= self.settings.fake_threshold else "REAL"
        confidence = avg if prediction == "FAKE" else 1.0 - avg
        best = max(votes, key=lambda v: float(v.details.get("fake_probability", 0)))

        result = InferenceResult(
            prediction=prediction,
            confidence=round(float(confidence), 4),
            model_name="ensemble",
            model_version="1.0",
            media_type=votes[0].media_type,
            frames_analyzed=votes[0].frames_analyzed,
            suspicious_frames=votes[0].suspicious_frames,
            processing_time_sec=round(time.perf_counter() - t0, 3),
            heatmap_path=best.heatmap_path,
            mode="ensemble",
            details={
                "fake_probability": round(avg, 4),
                "ensemble": [
                    {
                        "model": v.model_name,
                        "prediction": v.prediction,
                        "confidence": v.confidence,
                        "fake_probability": v.details.get("fake_probability"),
                    }
                    for v in votes
                ],
                "votes_fake": fake_votes,
                "votes_total": len(votes),
                "frame_probabilities": votes[0].details.get("frame_probabilities"),
                "signals": votes[0].details.get("signals"),
                "aggregation": "majority_vote+mean_probability",
            },
        )
        return enrich_result(result, path)

    def _get_audio_detector(self):
        if self.audio_detector is None and self.settings.enable_audio_model:
            try:
                self.audio_detector = AudioDeepfakeDetector(self.settings.audio_model_id, str(self.device))
            except Exception:
                self.audio_detector = None
        return self.audio_detector

    def _get_document_detector(self):
        if self.document_detector is None and self.settings.enable_document_model:
            try:
                self.document_detector = DocumentForgeryDetector(self.settings.document_model_id, str(self.device))
            except Exception:
                self.document_detector = None
        return self.document_detector

    def predict_audio(self, path: Path) -> InferenceResult:
        t0 = time.perf_counter()
        heuristic = analyze_audio(path)
        audio_detector = self._get_audio_detector()
        model_result = audio_detector.predict(path) if audio_detector is not None else None
        if model_result is not None:
            fake_prob = float(model_result["fake_probability"])
            mode = "audio-wav2vec2+forensics"
            signals = {
                **heuristic["signals"],
                "model_fake_probability": round(fake_prob, 4),
                "model_real_probability": round(model_result["real_probability"], 4),
                "chunk_probabilities": model_result["chunk_probabilities"],
                "chunks_analyzed": model_result["chunks_analyzed"],
                "model_id": model_result["model_id"],
            }
            model_name = "wav2vec2-audio-deepfake"
            model_version = "hf-vansh180"
        else:
            fake_prob = float(heuristic["fake_probability"])
            mode = "audio-forensics"
            signals = heuristic["signals"]
            model_name = "audio-forensics"
            model_version = "heuristic-1.0"
        prediction = "FAKE" if fake_prob >= self.settings.fake_threshold else "REAL"
        confidence = fake_prob if prediction == "FAKE" else 1.0 - fake_prob
        elapsed = time.perf_counter() - t0
        return InferenceResult(
            prediction=prediction,
            confidence=round(confidence, 4),
            model_name=model_name,
            model_version=model_version,
            media_type="audio",
            frames_analyzed=1,
            suspicious_frames=1 if prediction == "FAKE" else 0,
            processing_time_sec=round(elapsed, 3),
            mode=mode,
            details={
                "fake_probability": round(fake_prob, 4),
                "signals": signals,
                "finetuned_weights": model_result is not None,
                "detector_backend": "wav2vec2" if model_result is not None else "forensic-heuristic",
                "detector_model_id": self.settings.audio_model_id if model_result is not None else None,
                "modality": "audio",
            },
        )

    def predict_document(self, path: Path) -> InferenceResult:
        t0 = time.perf_counter()
        document_detector = self._get_document_detector()
        if document_detector is None:
            raise RuntimeError("Document forgery model is not available")
        result = analyze_document(path, document_detector, max_pages=self.settings.max_document_pages)
        elapsed = time.perf_counter() - t0
        return InferenceResult(
            prediction=result["prediction"],
            confidence=round(float(result["confidence"]), 4),
            model_name="document-forgery-vit",
            model_version="hf-zodumair",
            media_type="document",
            frames_analyzed=result["pages_analyzed"],
            suspicious_frames=sum(1 for p in result["page_results"] if p["label"] == "FAKE"),
            processing_time_sec=round(elapsed, 3),
            mode="document-vit+pdf-forensics",
            details={
                "fake_probability": round(float(result["fake_probability"]), 4),
                "signals": result["signals"],
                "pages": result["page_results"],
                "structure": result["structure"],
                "detector_backend": "document-vit",
                "detector_model_id": result["model_id"],
                "finetuned_weights": True,
                "modality": "document",
            },
        )

    def predict_image(self, path: Path) -> InferenceResult:
        t0 = time.perf_counter()
        image = read_image(str(path))
        face = self.face_detector.detect_or_full(image)
        face_prob, mode, signals, heatmap = self._predict_face(face.image_rgb)
        full_frame_prob = None
        if self.hf_detector is not None and face.confidence > 0:
            full_frame_prob = float(np.clip(self.hf_detector.predict(image), 0.0, 1.0))
            fake_prob = float(np.clip(0.75 * face_prob + 0.25 * full_frame_prob, 0.0, 1.0))
            signals = {**signals, "full_frame_fake_prob": round(full_frame_prob, 4), "face_fake_prob": round(face_prob, 4), "view_fusion": "75% face + 25% full-frame"}
        else:
            fake_prob = face_prob

        provenance = analyze_image_provenance(path)
        prediction = "FAKE" if fake_prob >= self.settings.fake_threshold else "REAL"
        confidence = fake_prob if prediction == "FAKE" else 1.0 - fake_prob
        heatmap_path = self._save_heatmap(face.image_rgb, heatmap)
        elapsed = time.perf_counter() - t0

        return InferenceResult(
            prediction=prediction,
            confidence=round(float(confidence), 4),
            model_name=self.model_name,
            model_version=self.model_version,
            media_type="image",
            frames_analyzed=1,
            suspicious_frames=1 if prediction == "FAKE" else 0,
            processing_time_sec=round(elapsed, 3),
            heatmap_path=str(heatmap_path) if heatmap_path else None,
            mode=mode,
            details={
                "face_backend": self.face_detector.backend,
                "face_bbox": list(face.bbox),
                "face_confidence": float(face.confidence),
                "fake_probability": round(float(fake_prob), 4),
                "signals": signals,
                "finetuned_weights": self.has_finetuned_weights,
                "detector_backend": self.detector_backend,
                "detector_model_id": self.settings.hf_model_id if self.hf_detector else None,
                "realtime": False,
                "provenance": provenance,
                "originality_note": "Classifier evidence is not proof of original source ownership or first capture.",
            },
        )

    def predict_video(self, path: Path) -> InferenceResult:
        t0 = time.perf_counter()
        sample = sample_video_frames(str(path), max_frames=self.settings.max_video_frames)
        probs: list[float] = []
        heatmaps: list[np.ndarray] = []
        faces_used = 0
        face_bboxes: list[tuple[int, int, int, int] | None] = []
        mode = self.detector_backend
        last_signals: dict = {}

        for frame in sample.frames:
            face = self.face_detector.detect_or_full(frame)
            if face.confidence > 0:
                faces_used += 1
                face_bboxes.append(tuple(face.bbox))
            else:
                face_bboxes.append(None)
            fake_prob, mode, last_signals, heat = self._predict_face(face.image_rgb)
            probs.append(fake_prob)
            heatmaps.append(heat)

        avg_prob = float(np.mean(probs)) if probs else 0.5
        suspicious = sum(1 for p in probs if p >= self.settings.fake_threshold)
        prediction = "FAKE" if avg_prob >= self.settings.fake_threshold else "REAL"
        confidence = avg_prob if prediction == "FAKE" else 1.0 - avg_prob

        heatmap_path = None
        if heatmaps and sample.frames:
            idx = int(np.argmax(probs))
            face = self.face_detector.detect_or_full(sample.frames[idx])
            heatmap_path = self._save_heatmap(face.image_rgb, heatmaps[idx])

        audio_result = None
        audio_tmp = None
        av_consistency = {"available": False, "reason": "audio unavailable"}
        try:
            audio_tmp = self._extract_video_audio(path)
            if audio_tmp:
                av_consistency = estimate_av_consistency(sample.frames, face_bboxes, audio_tmp, sample.fps)
            audio_detector = self._get_audio_detector()
            if audio_tmp and audio_detector is not None:
                audio_result = audio_detector.predict(audio_tmp)
                audio_fake = float(audio_result["fake_probability"])
                visual_fake = avg_prob
                wv = float(self.settings.video_audio_visual_weight)
                wa = float(self.settings.video_audio_weight)
                total_w = max(wv + wa, 1e-6)
                fused = float(np.clip((wv * visual_fake + wa * audio_fake) / total_w, 0.0, 1.0))
                prediction = "FAKE" if fused >= self.settings.fake_threshold else "REAL"
                confidence = fused if prediction == "FAKE" else 1.0 - fused
        finally:
            if audio_tmp:
                try:
                    audio_tmp.unlink(missing_ok=True)
                except Exception:
                    pass

        elapsed = time.perf_counter() - t0
        return InferenceResult(
            prediction=prediction,
            confidence=round(float(confidence), 4),
            model_name=self.model_name,
            model_version=self.model_version,
            media_type="video",
            frames_analyzed=len(probs),
            suspicious_frames=suspicious,
            processing_time_sec=round(elapsed, 3),
            heatmap_path=str(heatmap_path) if heatmap_path else None,
            mode=mode,
            details={
                "face_backend": self.face_detector.backend,
                "faces_detected_frames": faces_used,
                "fake_probability": round(avg_prob, 4),
                "frame_probabilities": [round(p, 4) for p in probs],
                "video_total_frames": sample.total_frames,
                "video_fps": sample.fps,
                "video_duration_sec": round(sample.duration_sec, 2),
                "finetuned_weights": self.has_finetuned_weights,
                "detector_backend": self.detector_backend,
                "detector_model_id": self.settings.hf_model_id if self.hf_detector else None,
                "signals": {
                    **last_signals,
                    "audio_fake_probability": round(float(audio_result["fake_probability"]), 4) if audio_result else None,
                    "audio_visual_fusion": "70% visual + 30% audio" if audio_result else "visual-only",
                },
                "aggregation": "mean_frame_probability",
                "audio_detector": audio_result.get("model_id") if audio_result else None,
                "audio_fake_probability": round(float(audio_result["fake_probability"]), 4) if audio_result else None,
                "audio_visual_fusion": "70% visual + 30% audio" if audio_result else "visual-only (audio unavailable)",
                "audio_video_consistency": av_consistency,
                "realtime": False,
            },
        )

    def predict_frame_bgr(self, frame_bgr: np.ndarray, *, include_heatmap: bool = True) -> InferenceResult:
        """Fast path for live webcam frames."""
        t0 = time.perf_counter()
        image = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        face = self.face_detector.detect_or_full(image)
        fake_prob, mode, signals, heatmap = self._predict_face(face.image_rgb)
        prediction = "FAKE" if fake_prob >= self.settings.fake_threshold else "REAL"
        confidence = fake_prob if prediction == "FAKE" else 1.0 - fake_prob

        heatmap_b64 = None
        heatmap_path = None
        if include_heatmap:
            overlay = overlay_heatmap(face.image_rgb, heatmap)
            ok, buf = cv2.imencode(
                ".jpg",
                cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR),
                [int(cv2.IMWRITE_JPEG_QUALITY), 80],
            )
            if ok:
                heatmap_b64 = base64.b64encode(buf.tobytes()).decode("ascii")

        elapsed = time.perf_counter() - t0
        result = InferenceResult(
            prediction=prediction,
            confidence=round(float(confidence), 4),
            model_name=self.model_name,
            model_version=self.model_version,
            media_type="live",
            frames_analyzed=1,
            suspicious_frames=1 if prediction == "FAKE" else 0,
            processing_time_sec=round(elapsed, 3),
            heatmap_path=heatmap_path,
            heatmap_b64=heatmap_b64,
            mode=mode,
            details={
                "face_backend": self.face_detector.backend,
                "face_bbox": list(face.bbox),
                "face_confidence": float(face.confidence),
                "fake_probability": round(float(fake_prob), 4),
                "signals": signals,
                "finetuned_weights": self.has_finetuned_weights,
                "detector_backend": self.detector_backend,
                "detector_model_id": self.settings.hf_model_id if self.hf_detector else None,
                "realtime": True,
            },
        )
        return enrich_result(result)

    def _predict_face(self, face_rgb: np.ndarray) -> tuple[float, str, dict, np.ndarray]:
        """Run a validated deepfake classifier, never an untrained ImageNet head."""
        forensic = forensic_fake_probability(face_rgb)
        forensic_p = forensic["fake_probability"]
        cam = forensic_heatmap(face_rgb)

        if self.hf_detector is not None:
            model_fake = self.hf_detector.predict(face_rgb)
            fake_prob = float(np.clip(model_fake, 0.0, 1.0))
            mode = "huggingface-vit"
            signals = {
                "model_fake_prob": round(model_fake, 4),
                "model_real_prob": round(1.0 - model_fake, 4),
                "forensic_fake_prob": round(forensic_p, 4),
                **{f"forensic_{k}": v for k, v in forensic["signals"].items()},
            }
            return fake_prob, mode, signals, cam

        if self.model is not None and self.has_finetuned_weights:
            tensor = to_tensor(face_rgb, self.settings.image_size).unsqueeze(0).to(self.device)
            with torch.enable_grad():
                logits = self.model(tensor)
                probs = F.softmax(logits, dim=1)[0]
                model_fake = float(probs[1].item())
                layer = find_last_conv(self.model)
                if layer is not None:
                    cam_engine = GradCAM(self.model, layer)
                    try:
                        cam = cam_engine.generate(tensor, class_idx=1 if model_fake >= 0.5 else 0)
                    finally:
                        cam_engine.close()
            signals = {
                "model_fake_prob": round(model_fake, 4),
                "model_real_prob": round(float(probs[0].item()), 4),
                "forensic_fake_prob": round(forensic_p, 4),
                **{f"forensic_{k}": v for k, v in forensic["signals"].items()},
            }
            return float(np.clip(model_fake, 0.0, 1.0)), "pytorch", signals, cam

        # Safe fallback: forensic cues only. This is intentionally not fused with
        # an untrained classifier because that created the false 100% results.
        signals = {
            "model_fake_prob": None,
            "model_real_prob": None,
            "forensic_fake_prob": round(forensic_p, 4),
            **{f"forensic_{k}": v for k, v in forensic["signals"].items()},
        }
        return forensic_p, "forensic-heuristic", signals, cam

    def _extract_video_audio(self, path: Path) -> Path | None:
        try:
            fd, name = tempfile.mkstemp(suffix=".wav")
            import os
            os.close(fd)
            out = Path(name)
            cmd = ["ffmpeg", "-y", "-i", str(path), "-vn", "-ac", "1", "-ar", "16000", "-t", "180", str(out)]
            completed = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            if completed.returncode != 0 or not out.exists() or out.stat().st_size < 1024:
                out.unlink(missing_ok=True)
                return None
            return out
        except (FileNotFoundError, subprocess.SubprocessError, OSError):
            return None

    def _save_heatmap(self, image_rgb: np.ndarray, cam: np.ndarray) -> Path | None:
        try:
            out_dir = self.settings.upload_dir / "heatmaps"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{uuid.uuid4().hex}_heatmap.jpg"
            overlay = overlay_heatmap(image_rgb, cam)
            cv2.imwrite(str(out_path), cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
            return out_path
        except Exception:
            return None


_engine: DeepfakeEngine | None = None


def enrich_result(result: InferenceResult, path: Path | None = None) -> InferenceResult:
    """Attach risk tier, SHA-256, and plain-language explanation."""
    fake_p = float(
        result.details.get(
            "fake_probability",
            result.confidence if result.prediction == "FAKE" else 1 - result.confidence,
        )
    )
    ratio = result.suspicious_frames / max(result.frames_analyzed, 1)
    risk = risk_level(fake_p, ratio)
    explanation = explain_result(
        prediction=result.prediction,
        fake_probability=fake_p,
        media_type=result.media_type,
        mode=result.mode,
        signals=result.details.get("signals") if isinstance(result.details.get("signals"), dict) else None,
        frames_analyzed=result.frames_analyzed,
        suspicious_frames=result.suspicious_frames,
    )
    result.details = {
        **result.details,
        "risk": risk,
        "explanation": explanation,
        "sha256": file_sha256(path) if path and Path(path).exists() else None,
    }
    return result


def get_engine() -> DeepfakeEngine:
    global _engine
    if _engine is None:
        _engine = DeepfakeEngine()
    return _engine


def reload_engine() -> DeepfakeEngine:
    global _engine
    _engine = DeepfakeEngine()
    return _engine
