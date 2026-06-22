# **CONTRIBUTING.md**

## **👋 Welcome**

Thank you for your interest in contributing to **Zomi‑Syl** — a rule‑based + CRF‑based Zomi syllabifier and NLP toolkit.  
This project aims to provide a reproducible, linguistically‑accurate foundation for Zomi language processing.

Contributions of all kinds are welcome: code, documentation, tests, datasets, and linguistic corrections.

---

## **📦 Project Structure**

```bash
src/zomi_syl/        → library code
training/            → CRF training pipeline
scripts/             → release + golden regression tools
tests/               → unit tests + golden regression
data/                → small metadata files
```

Packaged inference models live in:

```bash
src/zomi_syl/models/
```

Training models **must never** be committed.

---

## **🧱 Development Setup**

### 1. Clone the repository

```bash
git clone https://github.com/vubao2303/zomi-syl.git
cd zomi-syl
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 3. Install pre‑commit hooks

```bash
pre-commit install
```

This enforces formatting, linting, and prevents accidental model commits.

---

## **🧪 Running Tests**

The project uses `pytest` with golden regression.

```bash
make test
```

All tests must pass before submitting a PR.

If you modify the CRF model or training data, regenerate golden outputs:

```bash
python scripts/get_golden_crf_frozen_data.py
```

---

## **🧠 CRF Model Contributions**

If you contribute to the CRF training pipeline:

- Training models **must not** be committed  
- Only the **frozen inference model** inside `src/zomi_syl/models/` is packaged  
- Golden regression must be updated after retraining  
- Ambiguous words **must not** appear in the golden set  

See:

- CRF golden rules  
- Ambiguous word detection

---

## **📄 Coding Standards**

- Python 3.11+
- Black formatting
- Ruff linting
- Type hints encouraged
- Tests required for new features
- No large files in Git (datasets, models)

---

## **📝 Submitting a Pull Request**

1. Create a feature branch  
2. Ensure tests pass  
3. Ensure pre‑commit passes  
4. Update documentation if needed  
5. Submit PR with a clear description of the change  

PRs that modify the CRF model must include:

- updated golden regression  
- explanation of training data changes  
- evaluation summary (`training/model/crf/eval.txt`)

---

## **🚫 What Not to Commit**

The following must **never** be committed:

- training models (`*.joblib`, `*.bin`, `*.pt`, etc.)  
- large datasets  
- temporary files  
- local notebooks with sensitive data  

The pre‑commit hook will block these automatically.

---

## **📢 Reporting Issues**

Please include:

- example word(s)
- expected vs actual syllabification
- environment details
- whether the issue is CRF, rule‑based, or tokenization

---

## **🤝 Thank You**

Your contributions help build the first high‑quality, reproducible NLP toolkit for the Zomi language.  
Every improvement — small or large — strengthens the ecosystem.

---
