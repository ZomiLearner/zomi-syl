<p align="center">📦 <b>zomi‑syl</b></p>
<p align="center">
<a href="https://pypi.org/project/zomi-syl/">
<img src="https://img.shields.io/pypi/v/zomi-syl.svg" alt="PyPI Version">
</a>
<a href="https://pypi.org/project/zomi-syl/">
<img src="https://img.shields.io/pypi/dm/zomi-syl.svg" alt="Downloads">
</a>
<a href="https://github.com/ZomiLearner/zomi-syl/blob/main/LICENSE">
<img src="https://img.shields.io/github/license/ZomiLearner/zomi-syl.svg" alt="License">
</a>
<a href="https://github.com/ZomiLearner/zomi-syl/actions">
<img src="https://img.shields.io/github/actions/workflow/status/ZomiLearner/zomi-syl/tests.yml?branch=main" alt="CI Status">
</a>
<a href="https://ZomiLearner.github.io/zomi-syl">
<img src="https://img.shields.io/badge/docs-online-blue.svg" alt="Documentation">
</a>
</p>

# **zomi‑syl**

**A modular, dialect‑aware Zomi syllabification library with rule‑based and CRF backends.**

`zomi-syl` provides a **production‑ready syllabifier** for Zomi, supporting multiple dialects, multiple backends, and a clean, extensible architecture. It includes:

- A fast **rule‑based** syllabifier  
- A statistical **CRF** syllabifier  
- A unified API  
- A full CLI  
- A backend registry  
- Benchmarking tools  
- Dialect profiles  
- A clean, documented developer workflow  

---

## 🚀 **Features**

- **Multiple backends**: rule‑based, CRF, transformer‑ready  
- **Dialect‑aware** syllabification (csy [Siyin], ctd [Tedim] , gnb [Gangte], kmm [Kom Rem], pck [Paite], vap [Vaiphei], smt [Simte], tcz [Thado/Thadou], zom [Zo/Zou], [Mate], [Thangkhal], Zolai Standard, Myanmar Zomi, India Zomi)  
- **Unified API** (`zs.syllabify()`, `zs.analyze()`)  
- **Full CLI** (`zomi-syl syllabify`, `zomi-syl models benchmark`, `zomi-syl models compare`)
- **Benchmarking & evaluation tools**  
- **Extensible backend architecture**  
- **Clean developer documentation**  

---

## 📦 **Installation**

```bash
pip install zomi-syl
```

---

## 🧠 **Quick Start**

### **Syllabify a word**

```bash
zomi-syl syllabify itna
```

### **Analyze a word**

```bash
zomi-syl analyze itna --json
```

### **Batch syllabify**

```bash
zomi-syl batch words.txt --output out.txt
```

---

## 🧰 **Python API**

```python
import zomi_syl as zs

zs.syllabify("itna")
zs.analyze("itna")
```

---

## 🧩 **Backends**

`zomi-syl` supports multiple backends through a unified registry:

- **rule** — deterministic rule‑based syllabifier  
- **crf** — statistical CRF syllabifier  
- **transformer** — placeholder for future transformer models  

List available backends:

```bash
zomi-syl models list
```

Show backend metadata:

```bash
zomi-syl models info crf
```

---

## 📊 **Benchmarking**

### **Single backend**

```bash
zomi-syl models benchmark crf
```

### **Compare multiple backends**

```bash
zomi-syl models compare rule crf
```

### **Compare all backends**

```bash
zomi-syl models compare --all
```

---

## 🩺 **Diagnostics**

Run a full backend self‑test:

```bash
zomi-syl models doctor
```

This checks:

- registry integrity  
- model metadata  
- backend loadability  
- single prediction  
- batch prediction  

---

## 🌏 **Dialect Profiles**

Profiles live under:

```bash
src/zomi_syl/profiles/
```

Supported dialects:

- Gangte | Not Yet
- Kom | Not Yet
- Mate | Not Yet
- `Paite  | Yes`
- Simte | Not Yet
- Siyin | Not Yet
- `Tedim  | Yes`
- Thangkhaal | Not Yet
- Thado/Thadou | Not Yet
- Vaiphei | Not Yet
- Zo/Zou | Not Yet
- India Zomi | Not Yet
- Myanmar Zomi | Not Yet
- Zolai Standard | Not Yet

Eventhough some dialects are not yet supportted, `zomi-syl` will give higher 90% accurarcy for all the dialects.

List profiles:

```bash
zomi-syl profiles list
```

Show profile info:

```bash
zomi-syl profiles info tedim
```

---

## 🧪 **Testing**

Run all tests:

```bash
pytest
```

Golden CRF regression data:

```bash
tests/golden/crf_golden.tsv
```

---

## 🗂 **Project Structure**

```bash
src/zomi_syl/
    api.py
    cli.py
    backends/
    profiles/
    models/
    evaluation/
    rule_based/
    utils/
    ...
scripts/
docs/
tests/
training/
```

---

## 🛠 **Development**

Developer documentation lives in:

```bash
docs/Developer/
```

Key guides:

- Adding new backends  
- Unified Metadata Schema (UMS)  
- CRF training  
- Backend loader  
- Test templates  

---

## 📄 **Changelog**

The changelog is generated automatically:

```bash
make changelog
```

Template:

```bash
docs/Developer/CHANGELOG_template.md
```

---

## 📦 **Release Checklist**

See:

```bash
docs/RELEASE_CHECKLIST_v0.1.0.md
```

---

## 📜 **License**

MIT License — see `LICENSE`.

---

## 🙌 **Contributing**

See:

```bash
CONTRIBUTING.md
```

---

## 🔗 **Command Reference**

Full CLI command tree:

```bash
zomi-syl
│
├── syllabify
├── analyze
├── batch
├── benchmark
│
├── profiles list|info|validate
├── datasets list|download|validate
│
├── config show|path|validate|set
├── cache info|clear|remove
│
├── validate
├── download
├── version
│
└── models
    ├── list
    ├── info
    ├── benchmark
    ├── compare
    └── doctor
```
