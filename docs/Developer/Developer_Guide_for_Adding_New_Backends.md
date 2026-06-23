# Developer Guide: Adding New Backends to Zomi‑Syl

The **clean, authoritative, production‑ready Developer Guide for Adding New Backends** to Zomi‑Syl.  

This guide explains how to implement, register, and expose a new syllabification backend in the Zomi‑Syl engine.  
A *backend* is a pluggable module that implements the `BaseSyllabifier` interface and can be loaded via:

```python
be = zs.load_backend("rule")
```

or used indirectly through:

```python
zs.syllabify("itna", model="rule")
```

---

## 1. Backend Requirements

Every backend **must**:

- implement the `BaseSyllabifier` abstract class  
- provide `predict()` and `predict_batch()`  
- provide `get_metadata()` returning UMS‑compatible metadata  
- live under `zomi_syl/backends/`  
- be loadable via `core.engine._load_backend(name)`  
- be registered in the backend registry  

---

## 2. Directory Structure

Place backend here:

```
zomi_syl/
  backends/
    my_backend.py
```

Example:

```
zomi_syl/backends/fst_backend.py
```

---

## 3. Implementing a Backend Class

Every backend must subclass `BaseSyllabifier`:

```python
from zomi_syl.core.interfaces import BaseSyllabifier, Prediction, Boundary, ConfidenceScore

class MyBackend(BaseSyllabifier):

    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        # load model files, rules, weights, etc.

    def predict(self, word: str) -> Prediction:
        # run model
        sylls = ...
        boundaries = ...
        confidence = ...

        return Prediction(
            syllables=sylls,
            boundaries=boundaries,
            confidence=confidence,
            raw={"backend": "my-backend"},
        )

    def predict_batch(self, words):
        return [self.predict(w) for w in words]

    def get_metadata(self, include_ruleset=False):
        return {
            "backend_type": "my-backend",
            "version": "1.0.0",
            "capabilities": {
                "supports_confidence": True,
                "supports_batch": True,
                "supports_gpu": False,
            },
            "ums": self._base_ums(),
        }
```

### Required fields in `Prediction`:

- `syllables`: list of strings  
- `boundaries`: list of `Boundary(index, is_boundary=True)`  
- `confidence`: list of `ConfidenceScore(index, score)`  
- `raw`: backend‑specific debug info  

---

## 4. Add a Loader in `models/loader.py`

Each backend must be loadable by name.

In:

```
zomi_syl/models/loader.py
```

Add:

```python
from zomi_syl.backends.my_backend import MyBackend
import importlib.resources

def load_backend(name: str):
    if name == "my-backend":
        model_dir = importlib.resources.files("zomi_syl.models.my_backend")
        return MyBackend(str(model_dir))

    # existing:
    if name == "rule":
        ...
    if name == "crf":
        ...

    raise ValueError(f"Unknown backend: {name}")
```

---

## 5. Register the Backend in `core.engine`

In:

```
zomi_syl/core/engine.py
```

Add backend to the registry:

```python
_BACKEND_LOADERS = {
    "rule": _load_rule_backend,
    "crf": _load_crf_backend,
    "my-backend": _load_my_backend,
}
```

And implement:

```python
def _load_my_backend():
    return load_backend("my-backend")
```

---

## 6. Expose It in the Public API

In:

```
zomi_syl/__init__.py
```

```python
from .core.engine import _load_backend

def load_backend(name: str):
    return _load_backend(name)
```

This automatically exposes new backend:

```python
be = zs.load_backend("my-backend")
```

---

## 7. Test the Backend

### Load it:

```python
be = zs.load_backend("my-backend")
```

### Run prediction:

```python
be.predict("itna")
```

### Check metadata:

```python
be.get_metadata()
```

### Check UMS:

```python
be.get_metadata()["ums"]
```

---

## 8. Optional: Add a Model Folder

If backend needs model files:

```
zomi_syl/models/my_backend/
    config.json
    weights.bin
    vocab.txt
```

Access them via:

```python
import importlib.resources
model_dir = importlib.resources.files("zomi_syl.models.my_backend")
```

---

## 9. Optional: Add CLI Support

In:

```
zomi_syl/cli.py
```

Add:

```python
@click.option("--backend", type=click.Choice(["rule", "crf", "my-backend"]))
```

---

## 10. Optional: Add to Model Registry

If backend supports multiple trained models:

```
zomi_syl/registry/models.py
```

Add entries like:

```python
{
    "name": "my-backend-default",
    "backend_type": "my-backend",
    "metadata": {...}
}
```

---

# Summary

To add a new backend:

1. **Create backend class** in `backends/`  
2. **Implement BaseSyllabifier**  
3. **Add loader** in `models/loader.py`  
4. **Register backend** in `core.engine`  
5. **Expose via public API** (`load_backend`)  
6. **Add model files** (optional)  
7. **Add CLI + registry entries** (optional)  

The architecture is now fully extensible — adding CRF, FST, Transformer, or hybrid backends is straightforward.
