"""Lightweight audio-video consistency analysis.

This is an auxiliary signal, not a lip-reading model. It compares frame-level
lower-face motion with the audio energy envelope and reports correlation and
duration alignment. It should be used as supporting evidence, not as proof.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def estimate_av_consistency(
    frames_rgb: list[np.ndarray],
    face_bboxes: list[tuple[int, int, int, int] | None],
    audio_path: str | Path,
    fps: float,
) -> dict:
    try:
        import librosa

        audio, sr = librosa.load(str(audio_path), sr=16000, mono=True)
        if audio.size < 1600 or not frames_rgb:
            return {"available": False, "reason": "insufficient audio/video samples"}

        # RMS energy sampled at the video frame rate.
        hop = max(1, int(sr / max(fps, 1.0)))
        rms = librosa.feature.rms(y=audio, frame_length=1024, hop_length=hop)[0]
        if len(rms) < 3:
            return {"available": False, "reason": "insufficient audio envelope"}

        motion: list[float] = []
        previous = None
        for frame, bbox in zip(frames_rgb, face_bboxes):
            if bbox is None:
                motion.append(0.0)
                previous = None
                continue
            x1, y1, x2, y2 = bbox
            h, w = frame.shape[:2]
            x1, x2 = max(0, x1), min(w, x2)
            y1, y2 = max(0, y1), min(h, y2)
            if x2 <= x1 or y2 <= y1:
                motion.append(0.0)
                previous = None
                continue
            # Lower half of detected face is a rough mouth-region proxy.
            crop = frame[y1 + (y2 - y1) // 2:y2, x1:x2]
            if crop.size == 0:
                motion.append(0.0)
                continue
            crop = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY), (32, 24))
            crop = cv2.GaussianBlur(crop, (3, 3), 0).astype(np.float32)
            if previous is None:
                motion.append(0.0)
            else:
                motion.append(float(np.mean(np.abs(crop - previous))) / 255.0)
            previous = crop

        n = min(len(motion), len(rms))
        if n < 3:
            return {"available": False, "reason": "insufficient aligned samples"}

        m = np.asarray(motion[:n], dtype=np.float32)
        a = np.asarray(rms[:n], dtype=np.float32)
        if m.std() < 1e-6 or a.std() < 1e-6:
            corr = 0.0
        else:
            corr = float(np.corrcoef(m, a)[0, 1])
            if not np.isfinite(corr):
                corr = 0.0

        duration_sec = len(audio) / sr
        return {
            "available": True,
            "motion_audio_correlation": round(corr, 4),
            "alignment_score": round(float((corr + 1.0) / 2.0), 4),
            "video_duration_sec": round(len(frames_rgb) / max(fps, 1.0), 2),
            "audio_duration_sec": round(duration_sec, 2),
            "duration_delta_sec": round(abs(duration_sec - len(frames_rgb) / max(fps, 1.0)), 2),
            "note": "Lower-face motion/audio correlation is only an auxiliary consistency cue; speech, pose, and editing can affect it.",
        }
    except Exception as exc:
        return {"available": False, "reason": str(exc)}
