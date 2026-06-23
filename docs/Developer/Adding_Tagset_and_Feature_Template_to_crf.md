It *should* save `feature_templates` directly into the CRF model**, and the training script is the right place to do it. Right now, the CRF model contains only:

- weights  
- transitions  
- hyperparameters  

But **not**:

- `tagset`  
- `feature_templates`  

This is why the backend crashed with:

```
AttributeError: 'CRFBackend' object has no attribute 'feature_templates'
```

Let’s fix this properly and cleanly.

---

# ⭐ What must be saved inside the CRF model

Every CRF model must store:

- **tagset** → `["B", "I"]`  
- **feature_templates** → the templates used by `sent2features()`  

These two things define the model’s identity.

If they are not saved:

- metadata is incomplete  
- inference cannot be reproduced  
- UMS cannot be correct  
- backend must hard‑code templates (bad)

---

# ⭐ Step 1 — Extract feature templates from feature extractor

`sent2features()` function uses a fixed set of templates.  
It should define them in `features.py` like this:

```python
FEATURE_TEMPLATES = [
    "bias",
    "ch",
    "is_vowel",
    "is_consonant",
    "prev_ch",
    "next_ch",
    "prev_is_vowel",
    "next_is_vowel",
    "digraph_here",
    "digraph_prev",
    "at_start",
    "at_end",
]
```

This becomes the **single source of truth**.

---

# ⭐ Step 2 — Save templates into the CRF model during training

Modify training script:

### Before saving:

```python
crf = train_crf(X_train, y_train)

# Attach metadata to the model object
crf.tagset = ["B", "I"]
crf.feature_templates = FEATURE_TEMPLATES
```

### Then save:

```python
save_model(crf, args.output)
```

This ensures the model file contains:

- weights  
- tagset  
- feature templates  

---

# ⭐ Step 3 — Load them in the backend

Modify CRFBackend `__init__`:

```python
self.model = joblib.load(self.model_path)

self.tagset = getattr(self.model, "tagset", ["B", "I"])
self.feature_templates = getattr(self.model, "feature_templates", [])
```

Now the backend always loads the correct templates.

---

# ⭐ Step 4 — UMS metadata becomes correct

CRF metadata will now show:

```
"features": {
    "tagset": ["B", "I"],
    "num_features": 12,
    "feature_templates": [...],
    "model_path": ".../crf_syllabifier.joblib"
}
```

---
---

# ⭐ 1. The CRF does *not* use a simple list of template names  
The CRF uses **dictionary‑valued feature templates**, generated dynamically by:

- `char_features()`  
- `sent2features()`  

These functions produce **feature dictionaries**, not a list of template names.

Example output for one character:

```python
{
    "bias": 1.0,
    "char": "i",
    "char.lower": "i",
    "is_digit": False,
    "is_alpha": True,
    "is_upper": False,
    "is_lower": True,
    "pos": 0,
    "pos_from_end": 3,
    "prev_hyphen": False,
    "BOS": True,
    "is_onset_bigram": False,
    "is_onset_trigram": False,
    "is_coda": False,
    "is_vowel": True,
    "is_long_vowel": False,
    "vowel_class": "i",
    "suffix_2": "it",
    "suffix_3": "itn",
    "suffix_4": "itna",
    "prefix_2": "it",
    "prefix_3": "itn",
    "is_prefix": False,
    "prefix_class": "none",
    "char_type": "V",
    "next_char_type": "C",
    "cvc_pattern_window": "VC",
}
```

This means:

### ✔ CRF feature templates are **implicit**  
They are defined by the *code*, not by a list.

### ✔ It cannot extract them automatically from the CRF model  
Because sklearn‑crfsuite does not store them.

### ✔ It *can* store a list of **feature names**  
This is the correct approach.

---

# ⭐ 2. The correct `feature_templates` for CRF model  
Based on `char_features()` function, the **complete feature name set** is:

```
bias
char
char.lower
is_digit
is_alpha
is_upper
is_lower
pos
pos_from_end
prev_hyphen
prev.char
prev.char.lower
prev.prev_hyphen
BOS
next.char
next.char.lower
next_prev_hyphen
EOS
is_onset_bigram
is_onset_trigram
prev_is_onset
next_is_onset
is_coda
prev_is_coda
next_is_coda
is_vowel
is_long_vowel
vowel_class
suffix_2
suffix_3
suffix_4
prefix_2
prefix_3
is_prefix
prefix_class
char_type
prev_char_type
next_char_type
cvc_pattern_window
```

This is the **canonical feature template list** for CRF syllabifier.

---

# ⭐ 3. How to save these templates into the CRF model

Modify training script:

### Add this at the top of the file:

```python
FEATURE_TEMPLATES = [
    "bias",
    "char",
    "char.lower",
    "is_digit",
    "is_alpha",
    "is_upper",
    "is_lower",
    "pos",
    "pos_from_end",
    "prev_hyphen",
    "prev.char",
    "prev.char.lower",
    "prev.prev_hyphen",
    "BOS",
    "next.char",
    "next.char.lower",
    "next_prev_hyphen",
    "EOS",
    "is_onset_bigram",
    "is_onset_trigram",
    "prev_is_onset",
    "next_is_onset",
    "is_coda",
    "prev_is_coda",
    "next_is_coda",
    "is_vowel",
    "is_long_vowel",
    "vowel_class",
    "suffix_2",
    "suffix_3",
    "suffix_4",
    "prefix_2",
    "prefix_3",
    "is_prefix",
    "prefix_class",
    "char_type",
    "prev_char_type",
    "next_char_type",
    "cvc_pattern_window",
]
```

### Then modify `train_crf()`:

```python
crf = train_crf(X_train, y_train)
crf.tagset = ["B", "I"]
crf.feature_templates = FEATURE_TEMPLATES
```

### Then save:

```python
save_model(crf, args.output)
```

---

# ⭐ 4. How the backend loads them

In `CRFBackend.__init__`:

```python
self.model = joblib.load(self.model_path)

self.tagset = getattr(self.model, "tagset", ["B", "I"])
self.feature_templates = getattr(self.model, "feature_templates", [])
```

Now backend has:

- correct tagset  
- correct feature templates  
- correct metadata  

---

# ⭐ 5. Why this is the correct design

- CRF feature templates are **code‑defined**, not model‑defined  
- They must be saved manually  
- They must match training exactly  
- They belong in UMS under `features`  
- This makes model fully reproducible  
- This makes metadata correct and meaningful  

This is the cleanest, safest, and most future‑proof approach.

---
