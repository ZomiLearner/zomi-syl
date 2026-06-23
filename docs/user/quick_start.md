# **Quick Start**

This guide introduces the essential features of **zomi‑syl** so you can begin syllabifying Zomi words within minutes.  
You’ll learn how to use the CLI, the Python API, and how to work with dialect profiles and backends.

---

## **🚀 Syllabify Your First Word**

Once installed, try syllabifying a word:

```bash
zomi-syl syllabify itna
```

Expected output:

```
kam-sang
```

To see more detail:

```bash
zomi-syl analyze itna
```

Or JSON output:

```bash
zomi-syl analyze itna --json
```

---

## **🧰 Python API**

You can also use `zomi-syl` directly from Python.

```python
import zomi_syl as zs

zs.syllabify("itna")
zs.analyze("itna")
```

The `analyze()` function returns:

- syllables  
- boundaries  
- backend used  
- confidence (CRF)  

---

## **📦 Batch Syllabification**

To syllabify many words at once:

```bash
zomi-syl batch words.txt --output out.txt
```

Supported output formats:

- text  
- jsonl  
- csv  

Example:

```bash
zomi-syl batch words.txt --format jsonl --output results.jsonl
```

---

## **🧩 Choosing a Backend**

Zomi‑Syl supports multiple backends:

- **rule** — deterministic rule‑based  
- **crf** — statistical CRF model  
- **transformer** — placeholder for future models  

List available backends:

```bash
zomi-syl models list
```

Use a specific backend:

```bash
zomi-syl syllabify itna --backend crf
```

See backend metadata:

```bash
zomi-syl models info rule
```

Learn more: **Backends Overview**

---

## **🌏 Choosing a Dialect Profile**

Profiles define onsets, nuclei, codas, and rules for each dialect.

List profiles:

```bash
zomi-syl profiles list
```

Use a specific profile:

```bash
zomi-syl syllabify itna --profile tedim
```

Show profile details:

```bash
zomi-syl profiles info paite
```

Learn more: **Dialect Profiles**

---

## **📊 Benchmarking Backends**

Benchmark a single backend:

```bash
zomi-syl models benchmark crf
```

Compare multiple backends:

```bash
zomi-syl models compare rule crf
```

Compare all:

```bash
zomi-syl models compare --all
```

Learn more: **Benchmarking Guide**

---

## **🩺 Diagnostics**

Check that all backends load correctly:

```bash
zomi-syl models doctor
```

This runs:

- registry validation  
- metadata checks  
- backend load tests  
- prediction tests  

---

## **Next Steps**

- Install the library: **Installation**  
- Explore dialect profiles: **Dialect Profiles**  
- Learn the CLI: **Top‑Level Commands**  
- Add your own backend: **Adding New Backends**  

---
