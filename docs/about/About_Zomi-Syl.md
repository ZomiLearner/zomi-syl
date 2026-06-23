# **About Zomi‑Syl**

Zomi‑Syl is a **modular, dialect‑aware syllabification engine** designed for the Zomi language and its closely related varieties.  
It provides a unified, linguistically grounded framework for syllable segmentation across dialects, orthographies, and backend architectures.

Zomi‑Syl is built for:

- linguists  
- NLP researchers  
- educators  
- community contributors  
- developers integrating Zomi processing into applications  

It is open‑source, reproducible, and designed for long‑term maintainability.

---

## **🎯 Core Goals**

Zomi‑Syl was created to solve several long‑standing challenges in Zomi language technology:

- inconsistent syllabification across dialects  
- lack of standardized tooling  
- absence of reproducible, testable backends  
- difficulty integrating rule‑based and ML‑based approaches  
- need for a single, authoritative pipeline for research and production  

The project aims to provide:

- **dialect‑aware syllabification**  
- **multiple interchangeable backends**  
- **transparent evaluation and benchmarking**  
- **clean API + CLI**  
- **a unified metadata schema**  
- **a single source of truth for profiles and rules**  

---

## **🧩 Architecture Overview**

Zomi‑Syl is built on a **modular pipeline**:

- **Profiles** — dialect‑specific phonotactic inventories  
- **Backends** — rule‑based, CRF, transformer, and future models  
- **Registry** — unified backend and profile discovery  
- **Evaluation** — benchmarking, metrics, reports  
- **CLI** — user‑friendly command‑line interface  
- **Python API** — programmatic access  

This design ensures:

- reproducibility  
- extensibility  
- dialect flexibility  
- backend neutrality  
- clean separation of concerns  

---

## **🌏 Dialect‑Aware by Design**

Zomi‑Syl supports multiple Zomi varieties, including:

| Language / Group      | ISO‑639‑3 Link | Glottolog Link |
|-----------------------|----------------|-----------------|
| Gangte                | [gnb](https://iso639-3.sil.org/code/gnb) | [gang1266](https://glottolog.org/resource/languoid/id/gang1266) |
| Kom Rem               | [kmm](https://iso639-3.sil.org/code/kmm) | [komr1235](https://glottolog.org/resource/languoid/id/komr1235) |
| Mate                  |                |                 |
| Paite                 | [pck](https://iso639-3.sil.org/code/pck) | [pait1246](https://glottolog.org/resource/languoid/id/pait1246) |
| Simte                 | [smt](https://iso639-3.sil.org/code/smt) | [simt1235](https://glottolog.org/resource/languoid/id/simt1235) |
| Siyin                 | [csy](https://iso639-3.sil.org/code/csy) | [siyi1235](https://glottolog.org/resource/languoid/id/siyi1235) |
| Tedim                 | [ctd](https://iso639-3.sil.org/code/ctd) | [tedi1235](https://glottolog.org/resource/languoid/id/tedi1235) |
| Thado / Thadou        | [tcz](https://iso639-3.sil.org/code/tcz) | [thad1235](https://glottolog.org/resource/languoid/id/thad1235) |
| Thangkhal             |                |                 |
| Vaiphei               | [vap](https://iso639-3.sil.org/code/vap) | [vaip1236](https://glottolog.org/resource/languoid/id/vaip1236) |
| Zo / Zou              | [zom](https://iso639-3.sil.org/code/zom) | [zouu1234](https://glottolog.org/resource/languoid/id/zouu1234) |
| India Zomi            |                |                 |
| Myanmar Zomi          |                |                 |
| Zolai Standard        |                |                 |

---

Each dialect has its own:

- onset inventory  
- nucleus inventory  
- coda inventory  
- tone behavior (if applicable)  
- orthographic conventions  
- rule set  

See **Dialect Profiles** for details.

---

## **🛠 Backends**

Zomi‑Syl supports multiple interchangeable backends:

- **Rule‑based**  
- **CRF (Conditional Random Field)**  
- **Transformer‑based** (experimental)  
- **Reverse rule‑based** (diagnostic)  

Each backend is:

- versioned  
- benchmarked  
- validated  
- documented  

See **Backends** for implementation details.

---

## **📊 Evaluation & Benchmarking**

Zomi‑Syl includes a full evaluation suite:

- accuracy  
- boundary F1  
- confusion matrices  
- confidence scoring  
- regression testing  
- dataset validation  

See **Benchmarking Guide**.

---

## **📦 Installation & Usage**

- Install: **Installation**  
- Try the CLI: **CLI Reference**  
- Try the API: **Quick Start**  

---

## **🤝 Community & Contributions**

Zomi‑Syl is a community‑driven project.  
Contributions are welcome from:

- linguists  
- developers  
- educators  
- native speakers  
- researchers  

See:

- **Linguistic Contributors Guide**  
- **Developer Guide**  
- **Infra Maintainers Guide**  

---

## **📜 License**

Zomi‑Syl is released under the **MIT License**, allowing:

- academic use  
- commercial use  
- modification  
- redistribution  

---

## **Next Steps**

- Explore dialects: **Dialect Profiles**  
- Learn the CLI: **CLI Reference**  
- Add a backend: **Adding New Backends**  
- Benchmark models: **Benchmarking Guide**  

---
