# ⭐ **Top‑Level Commands (`zomi-syl …`)**

These are all commands registered directly under `@main.command()`.

### **Syllabification & Analysis**
- **syllabify** — Syllabify a single word  
- **analyze** — Detailed analysis of a word  
- **batch** — Batch syllabification from a file  

### **Benchmarking**
- **benchmark** — Run the *old* top‑level benchmark (still present in file)

### **Profiles & Datasets**
- **profiles** — List / info / validate profiles  
- **datasets** — Dataset management (stub)

### **Configuration & Cache**
- **config** — Show / set / validate config  
- **cache** — Cache info / clear / remove model  

### **Validation & Downloads**
- **validate** — Validate resources (stub)  
- **download** — Download a model  

### **Version**
- **version** — Show version  

---

# ⭐ **Model Registry Commands (`zomi-syl models …`)**

These come from `@main.group()` → `models`.

### **Model Info & Management**
- **models list** — List all available backends  
- **models info** — Show metadata for a backend  

### **Benchmarking**
- **models benchmark** — Benchmark a single backend  
- **models compare** — Compare multiple backends (new feature)

### **Diagnostics**
- **models doctor** — Full backend self‑test (load, metadata, prediction, batch)

---

# ⭐ **Full Command Tree (README‑ready)**

```
zomi-syl
│
├── syllabify WORD [--backend auto] [--profile auto] [--json] [--compact]
├── analyze WORD [--backend auto] [--profile auto] [--json]
├── batch FILE [--output PATH] [--format text|jsonl|csv] [--workers N] [--progress]
│
├── benchmark [--backend auto] [--dialect auto] [--dataset auto] [--dataset-version latest] [--report PATH]
│
├── profiles (list | info NAME | validate NAME)
├── datasets (list | download NAME | validate NAME)
│
├── config (show | path | validate | set KEY VALUE)
├── cache (info | clear | remove NAME)
│
├── validate [TARGET]
├── download NAME
├── version
│
└── models
    ├── list
    ├── info BACKEND
    ├── benchmark BACKEND [--dialect auto] [--json]
    ├── compare BACKEND... | --all [--dialect auto] [--json]
    └── doctor [--verbose]
```
