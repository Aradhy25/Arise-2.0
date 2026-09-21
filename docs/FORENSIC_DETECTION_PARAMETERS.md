# DeepGuard AI — Forensic Detection Parameters

## Purpose

DeepGuard should answer two separate questions:

1. **Classification:** Does the trained detector consider the media Real/Bona Fide or Fake/Spoofed?
2. **Evidence:** What measurable properties support or contradict that classification?

A confidence score is **not proof of originality**. A "REAL" result means the available detector evidence is real-leaning within the model's training and operating conditions.

This separation is deliberate because current deepfake research shows that strong benchmark results can degrade substantially on newer, in-the-wild content and unseen generators. DeepGuard should therefore expose evidence, calibration, and model/version information rather than presenting one percentage as certainty.

## 1. Image detection

### Primary decision signal

- Fine-tuned Real/Fake Vision Transformer probability.
- Input normalization and fixed-size preprocessing.
- Face detection/crop confidence when a face is present.

### Supporting forensic parameters

| Parameter | What it measures | Why it matters |
|---|---|---|
| ELA / recompression inconsistency | Local error after controlled JPEG recompression | Can expose regions with different compression histories |
| Frequency anomaly | Unusual mid/high-frequency energy patterns | Generated/manipulated imagery can leave frequency-domain traces |
| Noise inconsistency | Variation of local sensor/compression noise | Different regions may have incompatible noise statistics |
| RGB channel correlation | Relationship between color channels | Blending or synthesis can disturb local/global channel statistics |
| Face confidence/bounding box | Whether a face was found and where | Tells the detector what region was actually analyzed |
| Grad-CAM/heatmap | Regions influencing the visual model | Provides explainability, not independent proof |
| Model fake probability | Learned Real/Fake classification | Main trained-model decision signal |

### What makes an image "REAL" in DeepGuard?

A Real-leaning result means:

- the trained classifier assigns a Real-leaning probability;
- the supporting forensic signals do not show strong contradictory anomalies;
- the analyzed face/frame is within the detector's usable input conditions.

**Originality is a stronger claim than "REAL".** An image may be a genuine photograph that has been resized, compressed, cropped, filtered, or edited without being a deepfake. Conversely, a sophisticated synthetic image can look clean to older forensic heuristics.

### What makes an image "FAKE"?

A Fake-leaning result should be supported by:

- the trained classifier probability;
- spatial/texture/frequency anomalies where available;
- face-region evidence when the manipulation is facial;
- agreement between multiple calibrated signals.

The UI should show *which signals contributed* rather than inventing a human-readable reason that the model did not actually establish.

---

## 2. Document forgery detection

Document analysis is different from image deepfake detection. A PDF or office document has a **digital structure** in addition to pixels.

### Planned evidence layers

**Structural**
- PDF object/xref consistency
- incremental updates and revision history
- embedded object anomalies
- page/object ordering
- font embedding and substitution
- document producer/creator metadata

**Metadata**
- creation/modification timestamps
- author/application fields
- inconsistent timezone/timestamp relationships
- metadata versus visible document content

**Visual**
- page-level ELA
- local noise inconsistency
- duplicated regions
- pasted signatures/stamps
- font rendering differences
- alignment, spacing, baseline and kerning anomalies

**Semantic/OCR**
- OCR text versus rendered text
- altered numbers/dates/names
- layout changes around edited text
- duplicated or missing text regions

**Authenticity/provenance**
- cryptographic digital-signature validation
- certificate chain and signing time
- QR/barcode payload consistency
- source hash/provenance matching

### Important interpretation

A missing digital signature **does not automatically mean a document is forged**. Likewise, PDF metadata alone is not proof because documents are routinely exported, printed, scanned, and re-saved.

A high-confidence forgery report should identify the page/region and the concrete inconsistency.

---

## 3. Audio / voice-clone detection

### Current DeepGuard forensic path

The existing audio path measures:

- spectral flatness
- high-frequency energy ratio
- zero-crossing-rate mean
- zero-crossing-rate variability
- sample rate
- duration

These are **forensic heuristics**, not a state-of-the-art anti-spoof model.

### Higher-accuracy production path

A stronger audio system should combine a trained anti-spoof classifier with:

- mel-spectrogram embeddings
- F0/pitch trajectory
- formant trajectories
- prosody/rhythm
- phase/group-delay features
- codec/resampling traces
- speaker-embedding consistency
- calibrated ASVspoof-style bona-fide/spoof probability

The final result should expose both the model probability and the supporting signal evidence.

---

## 4. Video + audio detection

Video must not simply be treated as one still image.

### Visual/temporal parameters

- frame-level deepfake probability
- suspicious-frame ratio
- face identity consistency
- facial landmark/motion consistency
- optical-flow anomalies
- temporal flicker
- texture instability
- frame-to-frame frequency residuals
- generator-specific temporal traces

### Audio parameters

- voice anti-spoof probability
- spectral/prosodic evidence
- speaker consistency
- codec/resampling traces

### Audio-visual parameters

- lip motion versus phoneme timing
- audio/video synchronization offset
- face identity versus speaker identity consistency
- audio-visual embedding agreement

### Final video decision

The target architecture is:

**visual temporal detector + audio anti-spoof detector + calibrated audio-visual fusion**

Do not average raw probabilities from unrelated models. Each model needs validation/calibration before its score is combined with another modality.

The report should identify:

- suspicious timestamps;
- suspicious frames;
- audio evidence;
- lip-sync/synchronization evidence;
- model versions;
- calibration/confidence;
- conflicting signals.

---

## 5. "Highest accuracy" policy

DeepGuard should not claim a single detector is universally the "highest accuracy" model.

Recent in-the-wild evaluations demonstrate that open-source deepfake detectors can lose substantial performance on newer content and unseen generators. Therefore the production strategy should be:

1. use a trained detector per modality;
2. evaluate on current, representative data;
3. test cross-generator/generalization performance;
4. calibrate probabilities;
5. use multimodal fusion for video+audio;
6. retain forensic evidence and uncertainty;
7. benchmark before changing the model or claiming an accuracy figure.

The benchmark suite should include both established academic datasets and newer in-the-wild material.

## Runtime status

The parameter registry is now available in:

backend/app/ml/forensic_parameters.py

Current implementation status:

- **Image:** trained ViT + forensic auxiliary signals
- **Audio:** heuristic spectral forensic path
- **Video:** sampled-frame visual detection
- **Video + audio fusion:** architecture specified; full calibrated multimodal fusion is not yet implemented
- **Document forgery:** parameter specification added; detector implementation is not yet enabled

This is intentional: the repository should not claim a detector is implemented merely because its planned parameters have been documented.
