# Zomi Syllabifier (zomi-syl)

**zomi-syl** is a modular, dialect‑aware syllabification library for the Zomi language family.  
It provides **rule‑based**, **CRF**, **FST**, **BiLSTM**, **BiLSTM‑CRF**, and **Transformer** backends, with automatic model selection, Hugging Face integration, and support for multiple dialect profiles.

The library is designed for:

- Linguistic research  
- NLP pipelines  
- Tokenization and morphology  
- Phonology and phonemization  
- Batch processing and dataset annotation  
- Benchmarking and model comparison  

It is the foundation of the broader **zomi‑nlp** ecosystem.

---

## ✨ Features

- **Dialect‑aware syllabification**
  - csy [Siyin], ctd [Tedim] , gnb [Gangte], kmm [Kom Rem], pck [Paite], vap [Vaiphei], smt [Simte], tcz [Thado/Thadou], zom [Zo/Zou], [Mate], [Thangkhal], Zolai Standard, Myanmar Zomi, India Zomi
  - Custom profiles supported

- **Multiple backends**
  - Rule‑based (fastest)
  - CRF
  - FST
  - BiLSTM
  - BiLSTM‑CRF (balanced default)
  - Transformer (highest accuracy)

- **Hugging Face Hub integration**
  - Auto‑download models
  - Auto‑download datasets
  - Local caching

- **Batch processing engine**
  - Streaming mode
  - CSV/JSON/JSONL writers

- **Evaluation suite**
  - Boundary F1
  - Syllable accuracy
  - Speed benchmarks
  - Confidence scoring
  - Confusion matrices

- **CLI interface**
  - `zomi-syl "itna"`
  - `zomi-syl --model transformer --dialect tedim`

- **Production‑ready**
  - Docker support
  - Pre‑commit hooks
  - GitHub Actions (tests, lint, release, docs, demo)

---

## 📦 Installation

```bash
pip install zomi-syl
```

Optional extras:

```bash
pip install zomi-syl[fst]
pip install zomi-syl[torch]
pip install zomi-syl[all]
```

---

## 🚀 Quickstart

```python
import zomi_syl as zs

zs.syllabify("itna")
# → ["it", "na"]
```

Specify a model:

```python
zs.syllabify("itna", model="rule")
zs.syllabify("itna", model="bilstm_crf")
zs.syllabify("itna", model="transformer")
```

Specify a dialect:

```python
zs.syllabify("itna", dialect="tedim")
zs.syllabify("itna", dialect="zo_zou")
```

Full analysis:

```python
zs.analyze("itna")
```

---

## 🌏 Dialect Profiles

Dialect profiles live in:

```bash
src/zomi_syl/profiles/
```

Each profile contains:

- `vowels.json`
- `onsets.json`
- `codas.json`
- `nuclei.json`
- `rules.json`
- `profile.json` (metadata)

Available profiles:

- `tedim`
- `paite`
- `zo_zou`
- `siyin`
- `zolai_standard`
- `myanmar_zomi`
- `india_zomi`

Use a profile:

```python
zs.syllabify("itna", dialect="tedim")
```

---

## 🧠 Model Selection

```python
zs.syllabify("itna", model="rule")
zs.syllabify("itna", model="crf")
zs.syllabify("itna", model="fst")
zs.syllabify("itna", model="bilstm")
zs.syllabify("itna", model="bilstm_crf")
zs.syllabify("itna", model="transformer")
```

Auto mode:

```python
zs.syllabify("itna")  
# → chooses best balanced model (bilstm_crf)
```

Dialect‑specific models (if available):

```python
zs.syllabify("itna", model="bilstm_crf", dialect="tedim")
```

---

## 📚 Batch Processing

```python
from zomi_syl.batch import processor

proc = processor.BatchProcessor(model="bilstm_crf")
proc.process_file("input.txt", output="output.jsonl")
```

Streaming mode:

```python
for result in proc.stream(["itna", "Zomite"]):
    print(result)
```

---

## 📊 Benchmarking

```python
import zomi_syl as zs

zs.benchmark(models=["rule", "bilstm_crf"], dialect="tedim")
```

Generate a full report:

```python
from zomi_syl.evaluation.reports import generate_report

report = generate_report(models="all", dialect="zolai_standard")
print(report)
```

---

## 🖥 CLI Usage

```bash
zomi-syl "itna"
```

Specify model:

```bash
zomi-syl "itna" --model transformer
```

Specify dialect:

```bash
zomi-syl "itna" --dialect tedim
```

Batch mode:

```bash
zomi-syl --input words.txt --output out.jsonl
```

---

## 🏗 Architecture Overview

```bash
zomi-syl
│
├── api.py                # Public API
├── cli.py                # Command-line interface
│
├── core/                 # Engine + pipeline
├── rule_based/           # Deterministic backend
├── models/               # Bundled models + registry
├── ml/                   # HF neural backends
├── fst/                  # Finite-state backend
├── datasets/             # HF dataset integration
├── evaluation/           # Benchmarking + metrics
├── profiles/             # Dialect profiles
└── resources/            # Shared phonology + patterns
```

---

## 📘 Documentation

Full documentation:

- Architecture  
- API reference  
- Dialect profiles  
- Benchmarking  
- Deployment  
- Migration guides  

👉 [https://github.com/ZomiCommunity/zomi-syl](https://github.com/ZomiCommunity/zomi-syl)

---

## 📓 Notebooks

- Quickstart  
- Compare models  
- Dialect profiles  
- Batch processing  
- Benchmarking  

Open in Colab/Kaggle:

👉 [notebooks/README.md](notebooks/README.md)

---

## 🧪 Tests

Run tests:

```bash
pytest
```

Run performance benchmarks:

```bash
pytest tests/performance
```

---

## 🤝 Contributing

See:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

Pull requests welcome!

---

## 📄 License

MIT License.  
See [LICENSE](LICENSE) for details.
