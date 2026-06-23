A clean, polished, **official‑style documentation page** for public API function **`load_backend()`**.  
It matches the tone and structure of professional NLP library docs (spaCy, Stanza, HF Transformers), and it integrates naturally into Zomi‑Syl documentation set.

---

# `load_backend()` — Public Backend Loader

The `load_backend()` function provides direct access to the underlying syllabification backends used by the Zomi‑Syl engine.  
It allows advanced users to inspect backend internals, access rulesets, examine CRF metadata, or run predictions manually without going through the high‑level `zs.syllabify()` interface.

---

## Overview

`load_backend()` loads a syllabification backend by name and returns an initialized backend object.  
This backend object implements the `BaseSyllabifier` interface and provides:

- direct access to backend‑specific metadata  
- batch prediction  
- confidence scoring  
- access to internal resources (e.g., ruleset, CRF model path)  
- optional full ruleset inspection (RuleBackend only)

This function is intended for **advanced users**, researchers, and developers building tools on top of Zomi‑Syl.

---

## Function Signature

```python
load_backend(name: str) -> BaseSyllabifier
```

---

## Parameters

### `name`  
A string identifying the backend to load.

Supported values:

- `"rule"` — Rule‑based syllabifier (v6 engine)
- `"crf"` — CRF‑based syllabifier
- (future) `"fst"`, `"transformer"`, etc.

---

## Returns

A backend instance implementing:

- `predict(word: str) -> Prediction`
- `predict_batch(words: List[str]) -> List[Prediction]`
- `get_metadata(include_ruleset: bool = False) -> Dict[str, Any]`

---

## Basic Usage

### Load a backend

```python
import zomi_syl as zs

backend = zs.load_backend("rule")
```

### Run a prediction

```python
backend.predict("itna")
```

### Batch prediction

```python
backend.predict_batch(["itna", "khuapi", "nao"])
```

---

## Accessing Backend Metadata

### Summary metadata (UMS)

```python
meta = backend.get_metadata()
meta["ums"]
```

### Full ruleset (RuleBackend only)

The full ruleset is **not included by default** because it can be large.  
To access it:

```python
meta = backend.get_metadata(include_ruleset=True)
ruleset = meta["ums"]["features"]["ruleset_full"]
```

Or access directly:

```python
backend.ruleset
```

---

## When to Use `load_backend()`

Use this function when:

- backend‑specific debugging  
- full ruleset inspection  
- CRF feature template access  
- custom evaluation pipelines  
- integration into external NLP workflows  
- reproducible research setups  

For normal syllabification, prefer:

```python
zs.syllabify("itna")
```

---

## Example: Inspecting CRF Feature Templates

```python
crf = zs.load_backend("crf")
meta = crf.get_metadata()
meta["ums"]["features"]["feature_templates"]
```

---

## Example: Exporting the RuleBackend Ruleset

```python
rule = zs.load_backend("rule")
ruleset = rule.get_metadata(include_ruleset=True)["ums"]["features"]["ruleset_full"]

# Save to JSON
import json
json.dump(ruleset, open("ruleset_export.json", "w"), indent=2)
```

---

## Notes

- `load_backend()` does **not** run predictions automatically.  
- Backends are loaded lazily and cached internally.  
- The function provides a stable public API for backend access.  
- Normal users do not need this function; it is intended for advanced workflows.

---
