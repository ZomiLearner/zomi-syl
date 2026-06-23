# ⭐ Unified Metadata Schema (UMS) v1.0  

A **unified, backend‑agnostic metadata schema** so every backend (rule, CRF, FST, Transformer, BiLSTM, etc.) exposes metadata in a **consistent, predictable, machine‑readable** way.

A single, stable structure that every backend must follow.

Right now:

- **rule backend** dumps a huge ruleset directly into `raw`
- **CRF backend** exposes only `backend` + `tags`
- **FST / Transformer** will eventually need structured metadata
- `include_metadata` is effectively a no‑op because backends don’t follow a shared contract

```json
metadata: {
    "backend": {
        "name": "crf" | "rule" | "transformer" | "fst" | ...,
        "version": "1.0.0",
        "type": "statistical" | "rule-based" | "neural" | "hybrid"
    },

    "model": {
        "id": "crf-tedim-v1",
        "language": "zomi",
        "dialect": "tedim",
        "trained_on": ["dataset1", "dataset2"],
        "created_at": "2025-01-01",
        "updated_at": "2025-06-01"
    },

    "features": {
        "tagset": ["B", "I"],
        "num_features": 128,
        "feature_templates": [...],
        "ruleset_summary": {...},     # for rule backend
        "fst_states": 1234,           # for FST backend
        "transformer_layers": 6       # for transformer backend
    },

    "runtime": {
        "latency_ms": 0.42,
        "confidence_method": "marginals" | "rule-default" | "attention",
        "device": "cpu" | "gpu"
    }
}
```

This schema is:

- **backend‑agnostic**
- **extensible**
- **compact**
- **predictable**
- **safe to serialize**
- **easy to test**

---

# ⭐ How each backend would populate it

## ✔ Rule backend  

Instead of dumping the entire ruleset into `raw`, it would expose:

```json
metadata.features.ruleset_summary = {
    "num_onsets": 25,
    "num_nuclei": 30,
    "num_codas": 7,
    "num_rules": 12
}
```

The full ruleset can still be available under:

```text
metadata.features.ruleset_full
```

but **only when `include_metadata=True`**.

---

## ✔ CRF backend  

CRF finally gets meaningful metadata:

```
metadata.features = {
    "tagset": ["B", "I"],
    "num_features": 128,
    "feature_templates": ["prev_tag", "next_char", ...]
}
```

---

## ✔ Transformer backend  
Transformers can expose:

```
metadata.features = {
    "transformer_layers": 6,
    "hidden_size": 256,
    "attention_heads": 8
}
```

---

## ✔ FST backend  
Finite‑state models can expose:

```
metadata.features = {
    "fst_states": 1234,
    "fst_transitions": 5678
}
```

---

# ⭐ How `include_metadata` becomes meaningful

Right now, `include_metadata` does nothing because:

- rule backend always dumps metadata
- CRF backend has no metadata to dump

With UMS:

### `include_metadata=False`
Return only:

```
raw = {
    "backend": "crf",
    "tags": [...]
}
```

### `include_metadata=True`
Return:

```
raw = {
    "backend": "crf",
    "tags": [...],
    "metadata": {... UMS ...}
}
```

Now the flag **actually matters**.

---

# ⭐ Implementation plan (clean and incremental)

### Step 1 — Add a `get_metadata()` contract to all backends  
Each backend returns a dict matching UMS.

### Step 2 — Modify `predict()`  
Only attach metadata when `include_metadata=True`.

### Step 3 — Deprecate dumping full rule ruleset into `raw`  
Move it into:

```
metadata.features.ruleset_full
```

### Step 4 — Add unit tests  
- metadata present only when requested  
- metadata schema matches UMS  
- metadata keys consistent across backends  

---

# ⭐ Example final output (CRF, with metadata)

```
Prediction(
    syllables=['it', 'na'],
    boundaries=[...],
    confidence=[...],
    raw={
        "backend": "crf",
        "tags": ["B", "I", "B", "I"],
        "metadata": {
            "backend": {
                "name": "crf",
                "version": "1.0.0",
                "type": "statistical"
            },
            "model": {
                "id": "crf-tedim-v1",
                "language": "zomi",
                "dialect": "tedim"
            },
            "features": {
                "tagset": ["B", "I"],
                "num_features": 128
            },
            "runtime": {
                "latency_ms": 0.42,
                "confidence_method": "marginals",
                "device": "cpu"
            }
        }
    }
)
```

This is clean, structured, and future‑proof.
