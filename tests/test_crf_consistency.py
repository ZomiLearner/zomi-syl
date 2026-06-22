import pytest

from zomi_syl.backends.crf_backend import CRFBackend
from zomi_syl.utils.features import strip_and_flags, sent2features

# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------


@pytest.fixture(scope="session")
def crf_model():
    return CRFBackend()


# @pytest.fixture(scope="session")
# def crf_model():
#     """Load CRF backend once for all tests."""
#     model_dir = Path("src/zomi_syl/models/crf")
#     backend = CRFBackend(str(model_dir))
#     return backend


@pytest.fixture(scope="session")
def crf_backend():
    from zomi_syl.backends.crf_backend import CRFBackend

    return CRFBackend()


@pytest.fixture
def sample_words():
    """Representative Zomi words for consistency testing."""
    return [
        "ki-itna",
        "na-hun",
        "thu-khen",
        "papi-khat",
        "innsung",
        "lungzuang",
        "muhdahna",
    ]


# ---------------------------------------------------------
# 1. Feature extraction consistency
# ---------------------------------------------------------


def test_feature_shape_matches_training(crf_model, sample_words):
    """
    sent2features(chars, flags) must produce one feature dict per character.
    """
    for word in sample_words:
        chars, flags = strip_and_flags(word)
        feats = sent2features(chars, flags)

        assert len(chars) == len(
            feats
        ), f"Feature length mismatch for word={word}: chars={len(chars)}, feats={len(feats)}"

        assert isinstance(
            feats[0], dict
        ), "Each feature entry must be a dict (CRF expects dict features)."


# ---------------------------------------------------------
# 2. CRF model accepts inference features
# ---------------------------------------------------------


def test_crf_accepts_features(crf_model, sample_words):
    """
    Ensure CRF model can run predict_single() on sent2features output.
    """
    for word in sample_words:
        chars, flags = strip_and_flags(word)
        feats = sent2features(chars, flags)

        tags = crf_model.model.predict_single(feats)

        assert len(tags) == len(
            chars
        ), f"Tag length mismatch for word={word}: tags={len(tags)}, chars={len(chars)}"


# ---------------------------------------------------------
# 3. BIO tag validity
# ---------------------------------------------------------


def test_bio_tag_validity(crf_model, sample_words):
    """
    All predicted tags must be 'B' or 'I'.
    """
    for word in sample_words:
        pred = crf_model.predict(word)
        for t in pred.raw["tags"]:
            assert t in {"B", "I"}, f"Invalid BIO tag '{t}' in word={word}"


# ---------------------------------------------------------
# 4. Syllable reconstruction stability
# ---------------------------------------------------------


def test_syllable_reconstruction(crf_model, sample_words):
    """
    Ensure syllables reconstructed from BIO tags match expected segmentation length.
    """
    for word in sample_words:
        pred = crf_model.predict(word)

        # Reconstruct from boundaries
        reconstructed = "".join(pred.syllables)
        stripped = word.replace("-", "")

        assert (
            reconstructed == stripped
        ), f"Reconstructed syllables do not match original word={word}"


# ---------------------------------------------------------
# 5. Batch vs single prediction equivalence
# ---------------------------------------------------------


def test_batch_equals_single(crf_model, sample_words):
    """
    Batch prediction must produce identical results to single prediction.
    """
    batch_preds = crf_model.predict_batch(sample_words)

    for word, batch_pred in zip(sample_words, batch_preds):
        single_pred = crf_model.predict(word)

        assert (
            batch_pred.syllables == single_pred.syllables
        ), f"Batch vs single syllables mismatch for word={word}"

        assert [b.index for b in batch_pred.boundaries] == [
            b.index for b in single_pred.boundaries
        ], f"Batch vs single boundaries mismatch for word={word}"

        assert [c.score for c in batch_pred.confidence] == [
            c.score for c in single_pred.confidence
        ], f"Batch vs single confidence mismatch for word={word}"
