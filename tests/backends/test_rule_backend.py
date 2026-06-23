# tests/backends/test_rule_backend.py

import pytest
import zomi_syl as zs
from zomi_syl.core.interfaces import Prediction, Boundary, ConfidenceScore


@pytest.fixture(scope="module")
def backend():
    """Load the Rule backend once for all tests."""
    return zs.load_backend("rule")


# --------------------------------------------------------------
# Backend identity + metadata
# --------------------------------------------------------------

def test_rule_backend_identity(backend):
    assert backend.backend_name == "rule"
    assert backend.backend_type == "rule"
    assert backend.backend_version is not None


def test_rule_metadata_structure(backend):
    meta = backend.get_metadata()
    assert "backend_type" in meta
    assert "version" in meta
    assert "capabilities" in meta
    assert "ums" in meta

    ums = meta["ums"]
    assert "backend" in ums
    assert "model" in ums
    assert "features" in ums
    assert "runtime" in ums


def test_rule_metadata_features(backend):
    feats = backend.get_metadata()["ums"]["features"]

    assert "num_onsets" in feats
    assert "num_nuclei" in feats
    assert "num_codas" in feats
    assert "num_rules" in feats
    assert "ruleset_version" in feats

    # All counts must be integers
    assert isinstance(feats["num_onsets"], int)
    assert isinstance(feats["num_nuclei"], int)
    assert isinstance(feats["num_codas"], int)
    assert isinstance(feats["num_rules"], int)


# --------------------------------------------------------------
# Prediction tests
# --------------------------------------------------------------

def test_rule_predict_returns_prediction(backend):
    pred = backend.predict("itna")
    assert isinstance(pred, Prediction)
    assert isinstance(pred.syllables, list)
    assert isinstance(pred.boundaries, list)
    assert isinstance(pred.confidence, list)


def test_rule_boundaries_valid(backend):
    pred = backend.predict("itna")

    for b in pred.boundaries:
        assert isinstance(b, Boundary)
        assert b.is_boundary is True
        assert isinstance(b.index, int)
        assert 0 < b.index < len("itna")


def test_rule_confidence_valid(backend):
    pred = backend.predict("itna")

    for c in pred.confidence:
        assert isinstance(c, ConfidenceScore)
        assert c.score == 1.0


def test_rule_raw_backend_name(backend):
    pred = backend.predict("itna")
    assert pred.raw["backend"] == "rule-v6"


# --------------------------------------------------------------
# Batch prediction
# --------------------------------------------------------------

def test_rule_predict_batch(backend):
    words = ["itna", "khuapi", "nao"]
    preds = backend.predict_batch(words)

    assert len(preds) == len(words)
    for p in preds:
        assert isinstance(p, Prediction)


# --------------------------------------------------------------
# Ruleset access
# --------------------------------------------------------------

def test_rule_ruleset_loaded(backend):
    assert hasattr(backend, "ruleset")
    assert isinstance(backend.ruleset, dict)
    assert "all_syllables" in backend.ruleset
    assert isinstance(backend.ruleset["all_syllables"], list)


def test_rule_metadata_include_ruleset(backend):
    meta = backend.get_metadata(include_ruleset=True)
    feats = meta["ums"]["features"]

    assert "ruleset_full" in feats
    assert isinstance(feats["ruleset_full"], dict)
    assert "all_syllables" in feats["ruleset_full"]


# --------------------------------------------------------------
# Integration with zs.syllabify
# --------------------------------------------------------------

def test_rule_syllabify_integration():
    pred = zs.syllabify("itna", model="rule", return_metadata=True)
    assert pred.raw["backend"] == "rule-v6"
