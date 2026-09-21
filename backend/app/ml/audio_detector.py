"""Trained speech anti-spoof detector with chunk aggregation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForAudioClassification, AutoProcessor


DEFAULT_AUDIO_MODEL = "Vansh180/deepfake-audio-wav2vec2"


class AudioDeepfakeDetector:
    def __init__(self, model_id: str = DEFAULT_AUDIO_MODEL, device: str = "cpu"):
        self.model_id = model_id
        self.device = torch.device(device)
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForAudioClassification.from_pretrained(model_id)
        self.model.to(self.device)
        self.model.eval()

        labels = {int(k): str(v).lower() for k, v in self.model.config.id2label.items()}
        fake = [i for i, v in labels.items() if any(x in v for x in ("fake", "spoof", "synthetic"))]
        real = [i for i, v in labels.items() if any(x in v for x in ("real", "bonafide", "bona_fide", "genuine"))]
        if not fake or not real:
            raise RuntimeError(f"Audio model labels are not understood: {labels}")
        self.fake_index = fake[0]
        self.real_index = real[0]
        self.labels = labels

    @staticmethod
    def _load_audio(path: Path) -> tuple[np.ndarray, int]:
        import librosa
        audio, sr = librosa.load(str(path), sr=16000, mono=True)
        audio = np.asarray(audio, dtype=np.float32)
        if audio.size == 0:
            raise ValueError("Audio contains no samples")
        return audio, 16000

    def predict(self, path: str | Path, chunk_seconds: float = 4.0, max_chunks: int = 12) -> dict:
        audio, sr = self._load_audio(Path(path))
        chunk = int(sr * chunk_seconds)
        if len(audio) < chunk:
            padded = np.pad(audio, (0, chunk - len(audio)))
            chunks = [padded]
        else:
            starts = np.linspace(0, len(audio) - chunk, num=min(max_chunks, max(1, len(audio) // chunk)), dtype=int)
            chunks = [audio[s:s + chunk] for s in starts]

        probs = []
        for sample in chunks:
            inputs = self.processor(
                sample,
                sampling_rate=sr,
                return_tensors="pt",
                padding=True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.model(**inputs).logits
                p = F.softmax(logits, dim=-1)[0]
            probs.append(float(p[self.fake_index].item()))

        fake_probability = float(np.mean(probs))
        prediction = "FAKE" if fake_probability >= 0.5 else "REAL"
        return {
            "prediction": prediction,
            "confidence": fake_probability if prediction == "FAKE" else 1.0 - fake_probability,
            "fake_probability": fake_probability,
            "real_probability": 1.0 - fake_probability,
            "chunk_probabilities": [round(x, 4) for x in probs],
            "chunks_analyzed": len(probs),
            "sample_rate": sr,
            "duration_sec": round(len(audio) / sr, 2),
            "model_id": self.model_id,
        }
