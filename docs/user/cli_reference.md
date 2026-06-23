# **CLI Reference**

The `zomi-syl` command‑line interface provides tools for syllabification, analysis, batch processing, benchmarking, backend management, diagnostics, configuration, and dataset handling.

This page documents every top‑level command and subcommand available in **v0.1.0**.

---

# **📌 Command Overview**

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

---

# **🧠 Core Commands**

## **syllabify**  
Syllabify a single word.

```
zomi-syl syllabify WORD [--backend BACKEND] [--profile PROFILE] [--json] [--compact]
```

Examples:

```
zomi-syl syllabify kamsang
zomi-syl syllabify kamsang --backend crf
zomi-syl syllabify kamsang --profile tedim --json
```

---

## **analyze**  
Return a detailed analysis of a word, including:

- syllables  
- boundaries  
- backend used  
- confidence (CRF)  

```
zomi-syl analyze WORD [--backend BACKEND] [--profile PROFILE] [--json]
```

---

## **batch**  
Batch syllabify a file of words.

```
zomi-syl batch FILE [--output PATH] [--format text|jsonl|csv] [--workers N] [--progress]
```

Examples:

```
zomi-syl batch words.txt --output out.txt
zomi-syl batch words.txt --format jsonl --output out.jsonl
```

---

# **📊 Benchmarking & Evaluation**

## **benchmark**  
Legacy top‑level benchmark command (still supported).

```
zomi-syl benchmark [--backend BACKEND] [--dialect DIALECT] [--dataset DATASET]
```

---

# **🧩 Backend Management (`models` group)**

## **models list**  
List all available backends.

```
zomi-syl models list
```

---

## **models info**  
Show metadata for a backend.

```
zomi-syl models info BACKEND
```

---

## **models benchmark**  
Benchmark a single backend.

```
zomi-syl models benchmark BACKEND [--dialect DIALECT] [--json]
```

---

## **models compare**  
Compare multiple backends or all backends.

```
zomi-syl models compare BACKEND BACKEND...
zomi-syl models compare --all
```

---

## **models doctor**  
Run a full backend diagnostic:

- registry validation  
- metadata schema check  
- model file presence  
- load test  
- prediction test  

```
zomi-syl models doctor [--verbose]
```

---

# **🌏 Dialect Profiles (`profiles` group)**

## **profiles list**  
List all available dialect profiles.

```
zomi-syl profiles list
```

---

## **profiles info**  
Show profile metadata.

```
zomi-syl profiles info PROFILE
```

---

## **profiles validate**  
Validate a profile’s structure and phonotactic files.

```
zomi-syl profiles validate PROFILE
```

---

# **📁 Dataset Management (`datasets` group)**

## **datasets list**  
List available datasets.

```
zomi-syl datasets list
```

---

## **datasets download**  
Download a dataset (if remote sources are configured).

```
zomi-syl datasets download NAME
```

---

## **datasets validate**  
Validate dataset format and schema.

```
zomi-syl datasets validate NAME
```

---

# **⚙️ Configuration (`config` group)**

## **config show**  
Show the active configuration.

```
zomi-syl config show
```

---

## **config path**  
Show the path to the config file.

```
zomi-syl config path
```

---

## **config validate**  
Validate the configuration file.

```
zomi-syl config validate
```

---

## **config set**  
Set a configuration key.

```
zomi-syl config set KEY VALUE
```

---

# **🧹 Cache Management (`cache` group)**

## **cache info**  
Show cache status.

```
zomi-syl cache info
```

---

## **cache clear**  
Clear all cache entries.

```
zomi-syl cache clear
```

---

## **cache remove**  
Remove a specific cached model.

```
zomi-syl cache remove NAME
```

---

# **🔧 Utility Commands**

## **validate**  
Validate resources (placeholder for future expansion).

```
zomi-syl validate [TARGET]
```

---

## **download**  
Download a model (if remote sources are configured).

```
zomi-syl download NAME
```

---

## **version**  
Show the installed version.

```
zomi-syl version
```

---

# **Next Steps**

- Install the library: **Installation**  
- Try the API: **Quick Start**  
- Explore dialect profiles: **Dialect Profiles**  
- Benchmark backends: **Benchmarking Guide**  
- Add your own backend: **Adding New Backends**  

---
