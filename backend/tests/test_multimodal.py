from app.ml.document import DOCUMENT_EXTS
from app.ml.forensic_parameters import get_detection_parameters


def test_document_extensions_include_pdf():
    assert ".pdf" in DOCUMENT_EXTS


def test_forensic_parameter_registry_covers_modalities():
    params = get_detection_parameters()
    assert {"image", "document", "audio", "video_audio"} <= set(params)


def test_image_parameters_expose_provenance():
    image = get_detection_parameters("image")
    assert "EXIF/provenance signals" in image["implemented_now"]


def test_video_parameters_expose_audio_fusion():
    video = get_detection_parameters("video_audio")
    assert "configurable visual/audio fusion" in video["implemented_now"]
