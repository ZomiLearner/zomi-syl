**v0.1.0** - **Unified Metadata Schema (UMS)**

- a **single, stable structure**  
- consistent across **rule**, **CRF**, **FST**, **BiLSTM**, **Transformer**  
- minimal overhead  
- optional (only included when `include_metadata=True`)  
- future‑proof for v0.2.x and v0.3.x  

Below is the **full implementation plan**, with concrete backend code patterns.

---

# ⭐ Unified Metadata Schema (UMS) v1.0 — Final Structure

Every backend must return metadata in this shape:

```python
{
    "backend": {
        "name": "rule" | "crf" | "fst" | "transformer" | ...,
        "version": "1.0.0",
        "type": "rule-based" | "statistical" | "neural" | "hybrid"
    },

    "model": {
        "id": "rule-tedim-v6",
        "language": "zomi",
        "dialect": "tedim",
        "trained_on": [],
        "created_at": None,
        "updated_at": None
    },

    "features": {
        # backend-specific
    },

    "runtime": {
        "latency_ms": None,
        "confidence_method": None,
        "device": "cpu"
    }
}
```

This schema is compact, predictable, and works for every backend.

---

# ⭐ 1. Base class: `Backend.get_metadata()`

Every backend inherits this:

```python
class Backend:
    backend_name = None
    backend_version = "1.0.0"
    backend_type = None  # "rule-based", "statistical", "neural", "hybrid"

    def get_metadata(self):
        return {
            "backend": {
                "name": self.backend_name,
                "version": self.backend_version,
                "type": self.backend_type,
            },
            "model": {
                "id": getattr(self, "model_id", None),
                "language": "zomi",
                "dialect": getattr(self, "dialect", None),
                "trained_on": getattr(self, "trained_on", []),
                "created_at": getattr(self, "created_at", None),
                "updated_at": getattr(self, "updated_at", None),
            },
            "features": self.get_feature_metadata(),
            "runtime": {
                "latency_ms": None,
                "confidence_method": getattr(self, "confidence_method", None),
                "device": "cpu",
            },
        }

    def get_feature_metadata(self):
        return {}
```

Backends override **only** `get_feature_metadata()`.

---

# ⭐ 2. Rule backend implementation

```python
class RuleBackend(Backend):
    backend_name = "rule"
    backend_type = "rule-based"

    def get_feature_metadata(self):
        return {
            "num_onsets": len(self.ruleset["onsets"]),
            "num_nuclei": len(self.ruleset["nuclei"]),
            "num_codas": len(self.ruleset["codas"]),
            "num_rules": len(self.ruleset["rules"]),
            "ruleset_version": self.ruleset["version"],
        }
```

If `include_metadata=True`, may optionally add:

```python
metadata["features"]["ruleset_full"] = self.ruleset
```

---

# ⭐ 3. CRF backend implementation

```python
class CRFBackend(Backend):
    backend_name = "crf"
    backend_type = "statistical"

    def get_feature_metadata(self):
        return {
            "tagset": self.tagset,
            "num_features": len(self.feature_templates),
            "feature_templates": self.feature_templates,
            "model_file": self.model_path,
        }
```

This finally makes CRF metadata meaningful.

---

# ⭐ 4. FST backend implementation

```python
class FSTBackend(Backend):
    backend_name = "fst"
    backend_type = "rule-based"

    def get_feature_metadata(self):
        return {
            "fst_states": self.fst.num_states(),
            "fst_transitions": self.fst.num_transitions(),
            "deterministic": self.fst.is_deterministic(),
        }
```

---

# ⭐ 5. Transformer backend implementation

```python
class TransformerBackend(Backend):
    backend_name = "transformer"
    backend_type = "neural"

    def get_feature_metadata(self):
        return {
            "num_layers": self.model.config.num_hidden_layers,
            "hidden_size": self.model.config.hidden_size,
            "attention_heads": self.model.config.num_attention_heads,
            "parameters": self.model.num_parameters(),
        }
```

---

# ⭐ 6. Engine: attach metadata only when requested

Modify `predict()`:

```python
if include_metadata:
    result.raw["metadata"] = backend.get_metadata()
```

Now the flag **finally matters**.

---

# ⭐ 7. API behavior after UMS

### Without metadata:

```python
zs.syllabify("itna", model="crf")
```

→ clean output:

```
raw = {
    "backend": "crf",
    "tags": [...]
}
```

### With metadata:

```python
zs.syllabify("itna", model="crf", return_metadata=True)
```

→ includes:

```
raw["metadata"] = {
    "backend": {...},
    "model": {...},
    "features": {...},
    "runtime": {...}
}
```

---

# ⭐ 8. Why this is perfect for v0.1.0

- No breaking changes  
- Backends become consistent  
- `include_metadata` becomes meaningful  
- Rule backend stops dumping huge rulesets by default  
- CRF backend finally exposes useful metadata  
- Future backends (BiLSTM, Transformer) fit naturally  
- You can freeze UMS v1.0 in the release notes  

This is the right moment to do it.

---
---

Vu — perfect, this is exactly the moment to **lock UMS into v0.1.0**, because nothing is released yet and you can still reshape the backend interface without breaking anyone.

Below is a **complete, drop‑in UMS implementation** that:

- **respects existing interface** (`get_metadata()` must return backend_type, version, capabilities)
- **adds a unified metadata schema** *inside* that structure
- **keeps backends lightweight**
- **makes `include_metadata` meaningful**
- **does NOT break current API or Prediction class**

This is the cleanest possible design for v0.1.0.

---

# ⭐ Unified Metadata Schema (UMS) v1.0  
UMS is a **nested structure** returned by each backend’s `get_metadata()`:

```
{
    "backend_type": "...",
    "version": "...",
    "capabilities": {...},

    "ums": {
        "backend": {...},
        "model": {...},
        "features": {...},
        "runtime": {...}
    }
}
```

This keeps **public interface stable**, while giving you a **powerful internal schema**.

---

# ⭐ 1. Base class implementation (recommended)

Add a mixin or base implementation that all backends inherit.

```python
class BaseSyllabifier(ABC):
    backend_name: str = None
    backend_version: str = "1.0.0"
    backend_type: str = None  # "rule", "crf", "fst", "transformer", etc.

    # ------------------------------
    # Unified Metadata Schema (UMS)
    # ------------------------------
    def _base_ums(self) -> Dict[str, Any]:
        return {
            "backend": {
                "name": self.backend_name,
                "version": self.backend_version,
                "type": self.backend_type,
            },
            "model": {
                "id": getattr(self, "model_id", None),
                "language": "zomi",
                "dialect": getattr(self, "dialect", None),
                "trained_on": getattr(self, "trained_on", []),
                "created_at": getattr(self, "created_at", None),
                "updated_at": getattr(self, "updated_at", None),
            },
            "features": self._feature_metadata(),
            "runtime": {
                "latency_ms": None,
                "confidence_method": getattr(self, "confidence_method", None),
                "device": "cpu",
            },
        }

    def _feature_metadata(self) -> Dict[str, Any]:
        """Backends override this."""
        return {}

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        raise NotImplementedError
```

This gives every backend a **shared UMS core**.

---

# ⭐ 2. CRF backend implementation (UMS‑compliant)

```python
class CRFBackend(BaseSyllabifier):
    backend_name = "crf"
    backend_type = "statistical"

    def _feature_metadata(self):
        return {
            "tagset": self.tagset,
            "num_features": len(self.feature_templates),
            "feature_templates": self.feature_templates,
            "model_path": str(self.model_path),
        }

    def get_metadata(self):
        return {
            "backend_type": "crf",
            "version": "1.0.0",
            "capabilities": {
                "supports_confidence": True,
                "supports_batch": True,
                "supports_gpu": False,
                "supports_cpu": True,
            },
            "ums": self._base_ums(),
        }
```

Now CRF finally has meaningful metadata.

---

# ⭐ 3. Rule backend implementation (UMS‑compliant)

```python
class RuleBackend(BaseSyllabifier):
    backend_name = "rule"
    backend_type = "rule-based"

    def _feature_metadata(self):
        return {
            "num_onsets": len(self.ruleset["onsets"]),
            "num_nuclei": len(self.ruleset["nuclei"]),
            "num_codas": len(self.ruleset["codas"]),
            "num_rules": len(self.ruleset["rules"]),
            "ruleset_version": self.ruleset["version"],
        }

    def get_metadata(self):
        return {
            "backend_type": "rule-reverse" if self.use_reverse else "rule",
            "version": "1.0.0",
            "capabilities": {
                "supports_confidence": True,
                "supports_batch": True,
                "supports_gpu": False,
            },
            "ums": self._base_ums(),
        }
```

This replaces the giant ruleset dump with a **compact summary**.

If you want the full ruleset only when requested:

```python
if include_metadata:
    metadata["ums"]["features"]["ruleset_full"] = self.ruleset
```

---

# ⭐ 4. Engine: attach metadata only when requested

Modify engine’s `predict()`:

```python
if include_metadata:
    prediction.raw["metadata"] = backend.get_metadata()
```

Now the flag **finally matters**.

---

# ⭐ 5. What users will see

### Without metadata:

```
Prediction(
    syllables=['it','na'],
    raw={'backend': 'crf', 'tags': [...]}
)
```

### With metadata:

```
Prediction(
    syllables=['it','na'],
    raw={
        'backend': 'crf',
        'tags': [...],
        'metadata': {
            'backend_type': 'crf',
            'version': '1.0.0',
            'capabilities': {...},
            'ums': {...}
        }
    }
)
```

This is clean, structured, and future‑proof.

---

# ⭐ 6. Why this is perfect for v0.1.0

- No breaking changes  
- Backends become consistent  
- CRF finally exposes metadata  
- Rule backend stops dumping huge rulesets  
- `include_metadata` becomes meaningful  
- UMS v1.0 becomes part of **first public release**  

This is the right moment to do it.

---
