# ⭐ **`test_crf_backend.py` (Copy‑Paste Ready)**

The **clean, production‑ready `test_crf_backend.py`** that matches the architecture, UMS schema, CRFBackend interface, and existing test style.

It is fully aligned with how CRF backend behaves:

- `tagset = ['B', 'I']`
- `predict()` returns `Prediction`
- `raw['tags']` exists
- confidence scores are floats
- boundaries come from BIO decoding
- metadata includes UMS with CRF‑specific fields (`tagset`, `feature_templates`, `model_path`)

```dir
tests/backends/test_crf_backend.py
```

```python
# tests/backends/test_crf_backend.py

import pytest
import zomi_syl as zs
from zomi_syl.core.interfaces import Prediction, Boundary, ConfidenceScore


@pytest.fixture(scope="module")
def backend():
    """Load the CRF backend once for all tests."""
    return zs.load_backend("crf")


# --------------------------------------------------------------
# Backend identity + metadata
# --------------------------------------------------------------

def test_crf_backend_identity(backend):
    assert backend.backend_name == "crf"
    assert backend.backend_type == "crf"
    assert backend.backend_version is not None


def test_crf_metadata_structure(backend):
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


def test_crf_metadata_features(backend):
    meta = backend.get_metadata()
    feats = meta["ums"]["features"]

    assert "tagset" in feats
    assert feats["tagset"] == ["B", "I"]

    assert "feature_templates" in feats
    assert isinstance(feats["feature_templates"], list)

    assert "model_path" in feats
    assert isinstance(feats["model_path"], str)


# --------------------------------------------------------------
# Prediction tests
# --------------------------------------------------------------

def test_crf_predict_returns_prediction(backend):
    pred = backend.predict("itna")
    assert isinstance(pred, Prediction)
    assert isinstance(pred.syllables, list)
    assert isinstance(pred.boundaries, list)
    assert isinstance(pred.confidence, list)


def test_crf_predict_tags_present(backend):
    pred = backend.predict("itna")
    assert "tags" in pred.raw
    assert pred.raw["tags"] == ["B", "I", "B", "I"]


def test_crf_boundaries_valid(backend):
    pred = backend.predict("itna")

    for b in pred.boundaries:
        assert isinstance(b, Boundary)
        assert b.is_boundary is True
        assert isinstance(b.index, int)
        assert 0 < b.index < len("itna")


def test_crf_confidence_valid(backend):
    pred = backend.predict("itna")

    for c in pred.confidence:
        assert isinstance(c, ConfidenceScore)
        assert isinstance(c.score, float)


# --------------------------------------------------------------
# Batch prediction
# --------------------------------------------------------------

def test_crf_predict_batch(backend):
    words = ["itna", "khuapi", "nao"]
    preds = backend.predict_batch(words)

    assert len(preds) == len(words)
    for p in preds:
        assert isinstance(p, Prediction)


# --------------------------------------------------------------
# Metadata expansion
# --------------------------------------------------------------

def test_crf_metadata_include_ruleset(backend):
    """CRF backend does not have a ruleset, but include_ruleset=True should not break."""
    meta = backend.get_metadata(include_ruleset=True)
    assert "ums" in meta
    # CRF should NOT add ruleset_full
    assert "ruleset_full" not in meta["ums"]["features"]


# --------------------------------------------------------------
# Integration with zs.syllabify
# --------------------------------------------------------------

def test_crf_syllabify_integration():
    pred = zs.syllabify("itna", model="crf", return_metadata=True)
    assert pred.raw["backend"] == "crf"
    assert pred.raw["tags"] == ["B", "I", "B", "I"]
```

---

# ⭐ What this test suite guarantees

### ✔ CRF backend loads correctly  
`zs.load_backend("crf")` returns the actual CRFBackend instance.

### ✔ UMS metadata is valid  
Checks:

- backend  
- model  
- features  
- runtime  

### ✔ CRF‑specific metadata is correct  
- tagset = `["B", "I"]`  
- feature templates list  
- model path string  

### ✔ Prediction object is correct  
- syllables list  
- boundaries list  
- confidence list  
- raw tags  

### ✔ BIO decoding is correct  
Ensures `["B", "I", "B", "I"]` for `"itna"`.

### ✔ Batch prediction works  
Ensures list of Prediction objects.

### ✔ Integration with `zs.syllabify()`  
Ensures CRF backend is correctly wired into the high‑level API.

---
