# ⭐ 1. Do all backends have a `tagset`?

**Every backend will have a `tagset`**, but *not in the same way* and *not for the same purpose*.  

### ✔ **CRF backend**  
Yes — CRF *must* have a tagset because it predicts **BIO tags**:

```
["B", "I"]
```

This is part of the model definition.

### ✔ **Rule backend**  
No — rule backend does **not** use tags.  
But it *does* have a “feature set” (onsets, nuclei, codas, rules).

### ✔ **FST backend**  
No tagset — but it has states, transitions, etc.

### ✔ **Transformer backend**  
No tagset — but it has layers, heads, hidden size.

### ✔ **BiLSTM backend**  
If it predicts BIO tags, then yes — it will have a tagset.

---

# ⭐ 2. So how do we unify metadata across all backends?

We do **NOT** force every backend to have a `tagset`.  
Instead:

- CRF backend → `features.tagset`
- Rule backend → `features.ruleset_summary`
- FST backend → `features.fst_states`
- Transformer backend → `features.num_layers`, etc.

This is exactly why UMS has:

```
"features": { ... backend-specific ... }
```

Each backend fills in **only what applies**.

---

# ⭐ 3. CRF backend implementation (UMS‑compliant)

Here is the **correct** UMS implementation for CRF backend, using existing interface.

### ✔ Add backend identity  
### ✔ Add feature metadata  
### ✔ Add UMS wrapper  
### ✔ Keep existing `capabilities` block  

```python
class CRFBackend(BaseSyllabifier):
    backend_name = "crf"
    backend_type = "statistical"
    backend_version = "1.0.0"

    def _feature_metadata(self):
        return {
            "tagset": ["B", "I"],
            "num_features": len(self.feature_templates),
            "feature_templates": self.feature_templates,
            "model_path": str(self.model_path),
        }

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "backend_type": "crf",
            "version": self.backend_version,
            "capabilities": {
                "supports_confidence": True,
                "supports_batch": True,
                "supports_gpu": False,
                "supports_cpu": True,
            },
            "ums": self._base_ums(),
        }
```

This is **fully correct** and matches backend interface.

---

# ⭐ 4. Why this is the correct design

### ✔ CRF backend has a tagset  
Because it predicts BIO tags.

### ✔ Rule backend does NOT have a tagset  
Because it does not predict tags.

### ✔ UMS allows backend‑specific features  
Without forcing irrelevant fields.

### ✔ `include_metadata=True` now matters  
Because metadata is only attached when requested.

---

# ⭐ 5. What the CRF metadata will look like

When a user calls:

```python
zs.syllabify("itna", model="crf", return_metadata=True)
```

They will see:

```
raw["metadata"] = {
    "backend_type": "crf",
    "version": "1.0.0",
    "capabilities": {...},
    "ums": {
        "backend": {...},
        "model": {...},
        "features": {
            "tagset": ["B", "I"],
            "num_features": 128,
            "feature_templates": [...],
            "model_path": ".../crf_syllabifier.joblib"
        },
        "runtime": {...}
    }
}
```
