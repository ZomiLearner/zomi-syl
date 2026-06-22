# 📁 **zomi‑syl — Recommended Folder Structure**

It includes:

- clean PyPI packaging  
- clean separation of **inference vs training**  
- reproducible training pipelines  
- HuggingFace model publishing  
- long‑term maintainability  
- UD‑style, modular, auditable workflow preferences  

This structure is **battle‑tested** (spaCy, Stanza, Flair, HF Transformers) and tailored to Zomi NLP ecosystem.

```bash
zomi-syl/
├── pyproject.toml
├── README.md
├── LICENSE
├── MANIFEST.in
├── .gitignore
├── .github/
│   └── workflows/
│       ├── train_crf.yml
│       ├── test.yml
│       └── publish_pypi.yml
│
├── src/
│   └── zomi_syl/
│       ├── __init__.py
│       ├── __main__.py
│       ├── api.py                 ← public API (syllabify)
│       ├── cli.py                 ← zomi-syl CLI
│       ├── backends/
│       │   ├── crf_backend.py
│       │   ├── rule_backend.py
│       │   └── transformer_backend.py   (future)
│       ├── models/
│       │   ├── crf_syllabifier.joblib   ← frozen model
│       │   ├── config.json
│       │   └── ruleset.json
│       ├── config/
│       │   ├── default.toml
│       │   └── schema.json
│       ├── utils/
│       │   ├── features.py
│       │   └── loader.py
│       └── version.py
│
├── training/                     ← NOT included in PyPI
│   ├── data/                     ← downloaded dataset
│   │   └── zomi_syllabified_human.tsv
│   ├── scripts/
│   │   ├── clean_dataset.py
│   │   ├── train_crf.py
│   │   ├── evaluate_crf.py
│   │   ├── stats.py
│   │   └── freeze_model.py
│   ├── templates/
│   │   └── model_card_template.md
│   └── Makefile                  ← optional
│
├── tests/
│   ├── test_api.py
│   ├── test_crf_backend.py
│   ├── test_rule_backend.py
│   └── test_cli.py
│
└── docs/
    ├── architecture.md
    ├── backends.md
    ├── inference_api.md
    └── training_pipeline.md
```

---

# 🧠 **Why this structure is correct**

## ✔ 1. PyPI package stays clean  

Only `src/zomi_syl/` is included in the wheel.

Training code is **excluded** via:

```bash
MANIFEST.in
exclude training/
exclude tests/
exclude .github/
```

This keeps installation fast and lightweight.

---

## ✔ 2. Training pipeline stays in the repo, but outside the package  

This matches the goal:

- reproducible  
- auditable  
- modular  
- rule‑based + CRF + transformer backends  

And it keeps the PyPI package focused on **inference**.

---

## ✔ 3. GitHub Actions workflows are separated  

- `train_crf.yml` → model training + HF upload  
- `test.yml` → unit tests  
- `publish_pypi.yml` → PyPI release  

This avoids mixing dataset sync with model training.

---

## ✔ 4. Model artifacts live inside the package  

This allows:

```python
from zomi_syl import syllabify
```

to work **offline**, without downloading models.

---

## ✔ 5. Training uses the dataset repo or HF dataset

The training workflow will:

- download dataset from HF  
- clean  
- train  
- evaluate  
- freeze  
- upload model  

No dataset is stored in the PyPI package.
