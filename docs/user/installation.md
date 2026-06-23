# **Installation**

This page explains how to install **zomi‑syl**, the modular, dialect‑aware Zomi syllabification library.  
You can install it from PyPI for normal use or from source if you are developing new backends.

---

## **📦 Requirements**

- Python **3.9+**  
- pip **23+**  
- macOS, Linux, or Windows  
- A virtual environment (recommended)

---

## **🧰 Install from PyPI**

Install the latest stable release:

```bash
pip install zomi-syl
```

This installs:

- the core engine  
- rule‑based backend  
- CRF backend  
- dialect profiles  
- CLI (`zomi-syl`)  
- evaluation tools  

---

## **📁 Verify Installation**

Check the installed version:

```bash
zomi-syl version
```

Test a simple syllabification:

```bash
zomi-syl syllabify itna
```

---

## **🧪 Using a Virtual Environment (Recommended)**

### **venv**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install zomi-syl
```

### **conda**

```bash
conda create -n zomi-syl python=3.10
conda activate zomi-syl
pip install zomi-syl
```

---

## **🔧 Install from Source (Development Mode)**

If you are contributing or adding new backends:

```bash
git clone https://github.com/ZomiLearner/zomi-syl.git
cd zomi-syl
pip install -e .
```

Editable mode allows live code changes without reinstalling.

See **Developer Documentation** for backend development, metadata schema, and testing.

---

## **🧩 Optional Developer Tools**

Some advanced tools live in `scripts/`:

- dataset cleaning  
- CRF training  
- evaluation scripts  
- golden data extraction  

If you maintain a `requirements-dev.txt`, install them with:

```bash
pip install -r requirements-dev.txt
```

---

## **🛠 Troubleshooting**

### **Command not found: `zomi-syl`**

Try:

```bash
python -m zomi_syl version
```

If this works, your PATH is missing the Python scripts directory.

---

### **ImportError: cannot import name `zomi_syl`**

Ensure the package is installed:

```bash
pip install zomi-syl
```

Or activate your virtual environment.

---

## **Next Steps**

- Learn the CLI: **Top‑Level Commands**  
- Try the API: **Quick Start**  
- Explore dialect profiles: **Dialect Profiles**  
- Benchmark backends: **Benchmarking Guide**  

---
