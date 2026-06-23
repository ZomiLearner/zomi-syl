# Welcome to the Zomi‑Syl Documentation

`zomi-syl` is a modular, dialect‑aware Zomi syllabification library with support for
multiple backends, dialect profiles, benchmarking tools, and a clean developer
workflow. This documentation provides an overview of the system, how to use it,
and how to extend it with new models.

---

## 🚀 What is Zomi‑Syl?

Zomi‑Syl provides:

- A unified syllabification API  
- Multiple backends (rule‑based, CRF, transformer‑ready)  
- Dialect‑aware syllabification  
- A full CLI for analysis, benchmarking, and diagnostics  
- Developer tooling for adding new backends  
- Training and evaluation scripts  

It is designed for linguists, developers, and researchers working with Zomi
language processing.

---

## 📦 Installation

```bash
pip install zomi-syl
```

---

## 🧠 Quick Start

### Syllabify a word

```bash
zomi-syl syllabify itna
```

### Analyze a word

```bash
zomi-syl analyze itna --json
```

### Python API

```python
import zomi_syl as zs

zs.syllabify("itna")
zs.analyze("itna")
```

---

## 🧩 Key Components

### **Backends**

Zomi‑Syl supports multiple syllabification backends:

- Rule‑based  
- CRF  
- Transformer‑ready  

See: **Backend Overview**

### **Dialect Profiles**

Profiles define onsets, nuclei, codas, and rules for each dialect.

See: **Dialect Profiles**

### **CLI Tools**

The CLI provides:

- Syllabification  
- Analysis  
- Batch processing  
- Benchmarking  
- Backend comparison  
- Diagnostics  

See: **Top‑Level Commands**

### **Developer Guides**

Zomi‑Syl includes extensive developer documentation:

- Adding new backends  
- Unified Metadata Schema (UMS)  
- CRF training  
- Test templates  
- Recommended folder structure  

See: **Developer Documentation**

---

## 📊 Benchmarking

Benchmark a backend:

```bash
zomi-syl models benchmark crf
```

Compare multiple backends:

```bash
zomi-syl models compare rule crf
```

See: **Benchmarking Guide**

---

## 🛠 Adding New Models

Zomi‑Syl is designed for extensibility.  
New backends can be added without modifying the core engine.

See: **Adding New Backends**

---

## 📚 Documentation Structure

This documentation includes:

- **User Guide**  
  - Installation  
  - CLI usage  
  - Python API  
  - Dialect profiles  

- **Developer Guide**  
  - Backend architecture  
  - Unified Metadata Schema  
  - Adding new backends  
  - Testing  
  - Training CRF models  

- **Reference**  
  - CLI command reference  
  - Folder structure  
  - Release checklist  

---

## 🧪 Testing

Run all tests:

```bash
pytest
```

Golden CRF regression data:

```bash
tests/golden/crf_golden.tsv
```

---

## 📦 Release Notes

Changelog is generated automatically:

```bash
make changelog
```

See: **`[Looks like the result wasn't safe to show. Let's switch things up and try something else!]`**

---

## 📜 License

MIT License — see `LICENSE`.

---

## 🙌 Contributing

See: **`[Looks like the result wasn't safe to show. Let's switch things up and try something else!]`**

