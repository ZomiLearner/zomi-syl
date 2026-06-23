# **Benchmarking Backends**

Zomi‑Syl includes a built‑in benchmarking framework for evaluating syllabification backends.  
You can benchmark a single backend, compare multiple backends, or run diagnostics to ensure models load correctly.

Benchmarking is essential for:

- evaluating rule‑based vs CRF performance  
- validating new backends  
- regression testing  
- dialect‑specific evaluation  
- release readiness  

---

## **📊 Benchmark a Single Backend**

To benchmark one backend:

```bash
zomi-syl models benchmark crf
```

This runs:

- syllable accuracy  
- boundary F1  
- confidence scoring (if supported)  
- dataset‑level summary  

Benchmark a specific dialect:

```bash
zomi-syl models benchmark crf --dialect tedim
```

Output as JSON:

```bash
zomi-syl models benchmark crf --json
```

---

## **⚖️ Compare Multiple Backends**

Compare two or more backends:

```bash
zomi-syl models compare rule crf
```

This produces a side‑by‑side comparison of:

- accuracy  
- boundary F1  
- speed (if available)  
- metadata summary  

Example:

```bash
zomi-syl models compare rule crf transformer
```

---

## **🌐 Compare All Backends**

To benchmark every registered backend:

```bash
zomi-syl models compare --all
```

Useful for:

- release validation  
- regression testing  
- backend development  
- model selection  

---

## **🧪 Benchmark Datasets**

Benchmarking uses datasets defined in:

```
src/zomi_syl/evaluation/
```

Default dataset:

- `crf_golden.tsv` — gold standard regression set

Specify a dataset:

```bash
zomi-syl models benchmark crf --dataset crf_golden
```

Specify a dataset version:

```bash
zomi-syl models benchmark crf --dataset-version latest
```

---

## **🩺 Backend Diagnostics**

Before benchmarking, run a full backend health check:

```bash
zomi-syl models doctor
```

This validates:

- registry entries  
- metadata schema  
- model file presence  
- backend loadability  
- single prediction  
- batch prediction  

This is especially important when:

- adding new backends  
- modifying metadata  
- updating model files  

See: **Adding New Backends**

---

## **📁 Benchmark Reports**

Export JSON:

```bash
zomi-syl models benchmark crf --json > report.json
```

Advanced users can generate Markdown/HTML reports using the evaluation module.

---

## **🧠 Benchmarking in Python**

You can also run benchmarks programmatically:

```python
from zomi_syl.evaluation.benchmark import run_benchmark

result = run_benchmark(backend="crf", dialect="tedim")
print(result)
```

This returns:

- accuracy  
- boundary F1  
- dataset version  
- backend metadata  

---

## **🛠 Tips for Backend Developers**

When developing a new backend:

1. Run diagnostics:

```bash
zomi-syl models doctor
```

2. Benchmark your backend:

```bash
zomi-syl models benchmark my_backend
```

3. Compare against existing backends:

```bash
zomi-syl models compare rule crf my_backend
```

4. Add regression tests using:

```
tests/backends/template_test_my_backend.py
```

See: **Developer Documentation**

---

## **Next Steps**

- Install the library: **Installation**  
- Learn the CLI: **Top‑Level Commands**  
- Explore dialect profiles: **Dialect Profiles**  
- Add your own backend: **Adding New Backends**  

---
