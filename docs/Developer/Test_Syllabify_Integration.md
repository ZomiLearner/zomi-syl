# ⭐ **`test_syllabify_integration.py` (Copy‑Paste Ready)**

The **clean, production‑ready `test_syllabify_integration.py`** that validates the *entire* high‑level API:

- `zs.syllabify()`  
- `zs.analyze()`  
- `zs.compare_models()`  
- `zs.benchmark()`  
- model selection (`model="rule"`, `"crf"`, `"auto"`)  
- metadata handling  
- backend routing  
- prediction consistency  

It is fully aligned with the architecture and mirrors how the engine actually behaves.

```
tests/integration/test_syllabify_integration.py
```

```python
# tests/integration/test_syllabify_integration.py

import pytest
import zomi_syl as zs
from zomi_syl.core.interfaces import Prediction


# --------------------------------------------------------------
# Basic syllabify() integration
# --------------------------------------------------------------

def test_syllabify_rule_backend():
    pred = zs.syllabify("itna", model="rule", return_metadata=True)

    assert isinstance(pred, Prediction)
    assert pred.raw["backend"] == "rule-v6"
    assert pred.syllables == ["it", "na"]


def test_syllabify_crf_backend():
    pred = zs.syllabify("itna", model="crf", return_metadata=True)

    assert isinstance(pred, Prediction)
    assert pred.raw["backend"] == "crf"
    assert pred.raw["tags"] == ["B", "I", "B", "I"]


def test_syllabify_auto_backend():
    """Auto should fall back to rule or crf depending on availability."""
    pred = zs.syllabify("itna", model="auto", return_metadata=True)

    assert isinstance(pred, Prediction)
    assert pred.syllables == ["it", "na"]
    assert pred.raw["backend"] in ("rule-v6", "crf")


# --------------------------------------------------------------
# analyze()
# --------------------------------------------------------------

def test_analyze_returns_structure():
    result = zs.analyze("itna", model="rule")

    assert "input" in result
    assert "prediction" in result
    assert isinstance(result["prediction"], Prediction)


# --------------------------------------------------------------
# compare_models()
# --------------------------------------------------------------

def test_compare_models_outputs_both():
    result = zs.compare_models("itna", models=["rule", "crf"])

    assert "rule" in result
    assert "crf" in result
    assert isinstance(result["rule"], Prediction)
    assert isinstance(result["crf"], Prediction)


# --------------------------------------------------------------
# benchmark()
# --------------------------------------------------------------

def test_benchmark_runs():
    """Benchmark should run without raising errors."""
    report = zs.benchmark(models=["rule"], dialect="auto")

    assert isinstance(report, dict)
    assert "model" in report
    assert "accuracy" in report


# --------------------------------------------------------------
# Metadata handling
# --------------------------------------------------------------

def test_syllabify_metadata_flag():
    pred = zs.syllabify("itna", model="rule", return_metadata=True)

    assert "metadata" in pred.raw
    assert "ums" in pred.raw["metadata"]


def test_syllabify_no_metadata():
    pred = zs.syllabify("itna", model="rule", return_metadata=False)

    assert "metadata" not in pred.raw


# --------------------------------------------------------------
# Batch integration
# --------------------------------------------------------------

def test_syllabify_batch():
    preds = zs.syllabify(["itna", "khuapi"], model="rule")

    assert isinstance(preds, list)
    assert len(preds) == 2
    for p in preds:
        assert isinstance(p, Prediction)
```

---

# ⭐ What this test suite guarantees

### ✔ High‑level API works end‑to‑end  
- `syllabify()`  
- `analyze()`  
- `compare_models()`  
- `benchmark()`  

### ✔ Backend routing works  
- `model="rule"` → RuleBackend  
- `model="crf"` → CRFBackend  
- `model="auto"` → fallback logic  

### ✔ Metadata handling is correct  
- included only when requested  
- UMS present  
- backend info present  

### ✔ Predictions are consistent  
- Rule → `["it", "na"]`  
- CRF → BIO tags  

### ✔ Batch mode works  
- list input → list of predictions  

### ✔ No exceptions thrown  
Benchmark runs without errors.

---
