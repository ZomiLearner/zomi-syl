# **CONTRIBUTING.md — Infra Maintainers Guide**

## **🔧 Purpose**

This document defines the responsibilities, workflows, and rules for **infra maintainers** of the Zomi‑Syl project.  
Infra maintainers are responsible for:

- reproducible CRF training  
- golden regression stability  
- model freeze + packaging  
- Makefile orchestration  
- dataset ingestion + cleaning  
- release engineering  
- CI stability  
- preventing model drift  

This guide ensures the entire pipeline remains deterministic and auditable.

---

## **📁 Infra‑Relevant Repository Structure**

```bash
training/                    → CRF training pipeline
training/data/               → cleaned datasets
training/model/crf/          → temporary training outputs

scripts/                     → golden, freeze, validation scripts
scripts/release_crf_freeze.sh
scripts/get_golden_crf_frozen_data.py

src/zomi_syl/models/         → packaged inference models (only these go to PyPI)

tests/golden/                → golden regression snapshots
tests/                       → regression + backend tests

Makefile                     → orchestration for training, testing, release
MANIFEST.in                  → PyPI exclusion rules
.pre-commit-config.yaml      → formatting + safety hooks
```

---

## **🧱 Core Responsibilities**

### **1. Maintain Reproducibility**

Infra maintainers must ensure:

- deterministic CRF training  
- stable feature extraction  
- stable golden regression  
- no accidental model drift  
- no stale artifacts in Git  
- no training models committed  

Reproducibility is the highest priority.

---

### **2. Maintain Golden Regression**

Golden regression is the contract between:

- the packaged inference model  
- the test suite  
- the release pipeline  

Infra maintainers must:

- ensure golden files reflect the **frozen** model  
- ensure **no ambiguous words** appear in golden  
- regenerate golden after any model change  
- validate golden diffs before merging  

Golden regeneration:

```bash
python scripts/get_golden_crf_frozen_data.py
```

Golden inspection:

```bash
make check-crf WORDS="amah upa zawlai"
```

---

### **3. Maintain the CRF Training Pipeline**

Infra maintainers own:

- dataset ingestion  
- dataset cleaning  
- feature extraction  
- training configuration  
- evaluation metrics  
- training reproducibility  

Key commands:

```bash
make get-zomi-syllabified-human
make clean-dataset
make train-crf
```

Training outputs must **never** be committed.

---

### **4. Maintain the Release Freeze Workflow**

The release freeze script:

```bash
scripts/release_crf_freeze.sh
```

Must always:

- fetch dataset  
- clean dataset  
- train CRF  
- freeze model  
- package model into wheel  
- regenerate golden  
- validate tests  
- remove temporary artifacts  

Infra maintainers must ensure:

- freeze script works on clean machines  
- wheel contains correct model  
- no training artifacts leak into Git  
- versioning is correct  

---

### **5. Maintain Makefile Orchestration**

The Makefile is the single source of truth for:

- training  
- testing  
- golden regeneration  
- release freeze  
- linting  
- dataset ingestion  

Infra maintainers must:

- keep targets deterministic  
- avoid side effects  
- ensure targets work on Linux + macOS  
- ensure targets do not require secrets  

---

### **6. Maintain Pre‑Commit Hooks**

Infra maintainers must ensure:

- Black formatting  
- Ruff linting  
- YAML/JSON/TOML validation  
- model‑file blocking  
- golden‑ambiguity blocking  

Run:

```bash
pre-commit install
pre-commit run --all-files
```

---

### **7. Maintain CI Stability**

Infra maintainers must ensure:

- CI runs `make test`  
- CI enforces pre‑commit  
- CI validates wheel build  
- CI validates golden regression  

CI must never allow:

- model drift  
- golden drift  
- missing packaged model  
- stale artifacts  

---

## **🧪 Testing Requirements**

Infra maintainers must ensure:

- all tests pass before merging  
- golden regression is stable  
- CRFBackend loads packaged model  
- no test depends on local state  

Run:

```bash
make test
```

---

## **🚫 What Infra Maintainers Must Never Do**

- never commit training models  
- never commit large datasets  
- never modify golden without explanation  
- never change CRF features without retraining  
- never bypass pre‑commit  
- never merge without full test pass  
- never break reproducibility  

---

## **📦 Release Responsibilities**

Infra maintainers own the release pipeline:

- version bump  
- golden regeneration  
- freeze script execution  
- wheel validation  
- PyPI upload  
- post‑release verification  

Release dry‑run:

```bash
make test
pip install dist/zomi_syl-*.whl --force-reinstall
python -m zomi_syl syllabify "themthum"
```

---

## **🧭 How to Propose Infra Changes**

1. Open an issue describing:
   - motivation  
   - reproducibility impact  
   - golden impact  
   - release impact  

2. Create a feature branch  
3. Update Makefile + scripts  
4. Update tests  
5. Run full release dry‑run  
6. Submit PR with:
   - evaluation summary  
   - golden diff  
   - wheel validation  

---

## **🤝 Thank You**

Infra maintainers are the backbone of Zomi‑Syl.  
Your work ensures the project remains:

- reproducible  
- stable  
- linguistically correct  
- future‑proof  

This is the foundation for the entire Zomi NLP ecosystem.

---
