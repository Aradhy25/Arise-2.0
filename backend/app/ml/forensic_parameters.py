"""Machine-readable forensic parameter registry for DeepGuard AI.

This module describes what each modality should measure and what is currently
implemented. It intentionally separates trained-model probabilities from
forensic evidence so the UI never presents a heuristic as proof of authenticity.
"""

from __future__ import annotations

from typing import Any


DETECTION_PARAMETERS: dict[str, dict[str, Any]] = {
    "image": {
        "decision": "trained Real/Fake probability + auxiliary forensic evidence",
        "implemented_now": [
            "Vision Transformer Real/Fake probability",
            "face + full-frame multi-view fusion",
            "ELA/recompression inconsistency",
            "frequency-domain anomaly",
            "local noise inconsistency",
            "RGB channel correlation",
            "face detection confidence and crop location",
            "EXIF/provenance signals",
            "Grad-CAM / forensic heatmap",
        ],
        "additional_high_accuracy_signals": [
            "pixel-level texture statistics",
            "generator fingerprint / frequency residuals",
            "face-landmark geometry consistency",
            "lighting and shadow consistency",
            "reflection/specular consistency",
            "camera/codec/provenance metadata",
            "source-image hash and known-origin matching",
        ],
        "real_explanation": [
            "The classifier assigns a Real-leaning probability.",
            "Forensic auxiliary signals can be reported as supporting or conflicting evidence.",
            "Originality means no detected manipulation signal, not proof that the image is the original source.",
        ],
        "fake_explanation": [
            "The classifier assigns a Fake-leaning probability.",
            "Local forensic anomalies identify regions or properties that differ from expected image statistics.",
            "A fake verdict should state which signals contributed and whether they agree.",
        ],
    },
    "document": {
        "decision": "document-integrity evidence + trained page/document forgery classifier",
        "implemented_now": [
            "PDF rendering and page sampling",
            "ELA-assisted document ViT classification",
            "PDF metadata and structural checks",
            "page-level probability aggregation",
            "page-level forensic evidence",
            "PDF provenance notes",
            "repeated text-block analysis",
            "repeated embedded-image reference analysis",
            "per-page text/image structure metrics",
        ],
        "parameters": [
            "PDF object/xref structure consistency",
            "incremental-update and revision history anomalies",
            "embedded font and font-substitution anomalies",
            "metadata creation/modification timestamp consistency",
            "embedded-image recompression / ELA anomalies",
            "page-level pixel and noise inconsistencies",
            "OCR text versus rendered text consistency",
            "layout/alignment/spacing anomalies",
            "signature/certificate validity",
            "QR/barcode payload consistency",
            "copy-paste / duplicated-region artifacts",
            "document-origin hash and provenance",
        ],
        "real_explanation": [
            "A document is real/authentic-leaning when its cryptographic signatures, structure, metadata, rendering, OCR, and visual evidence are mutually consistent.",
            "A scanned document can be genuine even without a digital signature; absence of a signature is not itself proof of forgery.",
        ],
        "fake_explanation": [
            "A forgery finding should identify page/region and the concrete structural, visual, metadata, or signature inconsistencies detected.",
            "Document detection must distinguish ordinary re-saving/compression from evidence of intentional alteration.",
        ],
    },
    "audio": {
        "decision": "trained anti-spoof probability + signal-level forensic evidence",
        "implemented_now": [
            "fine-tuned Wav2Vec2 Real/Spoof classifier",
            "multi-chunk probability aggregation",
            "spectral flatness",
            "high-frequency energy ratio",
            "zero-crossing-rate statistics",
            "sample rate and duration",
        ],
        "additional_high_accuracy_signals": [
            "mel-spectrogram embeddings",
            "F0/pitch contour naturalness",
            "formant trajectories",
            "prosody and rhythm consistency",
            "phase/group-delay artifacts",
            "codec and resampling traces",
            "speaker-embedding consistency",
            "ASVspoof-style trained anti-spoof classifier",
        ],
        "real_explanation": [
            "The anti-spoof model should classify the waveform as bona-fide/real-leaning.",
            "Signal-level evidence should show whether spectral, prosodic, phase, and codec cues agree.",
        ],
        "fake_explanation": [
            "A fake/clone finding should identify the anti-spoof score and the signal features that support it.",
            "A high score from one heuristic alone is not sufficient for a production-grade voice-clone conclusion.",
        ],
    },
    "video_audio": {
        "decision": "temporal visual detector + audio anti-spoof detector + audio-visual consistency fusion",
        "implemented_now": [
            "frame sampling",
            "per-frame image deepfake probability",
            "suspicious-frame ratio",
            "frame probability aggregation",
            "audio extraction when FFmpeg is available",
            "trained audio anti-spoof probability",
            "configurable visual/audio fusion",
        ],
        "additional_high_accuracy_signals": [
            "temporal face consistency",
            "identity consistency across frames",
            "optical-flow and motion artifacts",
            "flicker / texture instability",
            "lip-motion versus phoneme timing",
            "audio-video synchronization offset",
            "speaker-face identity consistency",
            "audio anti-spoof probability",
            "audio-visual embedding agreement",
            "generator-specific temporal residuals",
        ],
        "real_explanation": [
            "A video should be considered authentic-leaning only when temporal visual evidence and audio-visual consistency do not show significant contradictions.",
            "The system should report frame-level and audio-level evidence instead of hiding everything behind one number.",
        ],
        "fake_explanation": [
            "A manipulated-video finding should identify suspicious frames/time ranges and whether the audio, face motion, identity, or synchronization contributed.",
            "Audio and video evidence should be fused only after calibration; raw probabilities from different models are not automatically comparable.",
        ],
    },
}


def get_detection_parameters(modality: str | None = None) -> dict[str, Any]:
    if modality:
        if modality not in DETECTION_PARAMETERS:
            raise KeyError(modality)
        return DETECTION_PARAMETERS[modality]
    return DETECTION_PARAMETERS
