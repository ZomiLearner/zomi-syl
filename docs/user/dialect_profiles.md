# **Dialect Profiles**

Zomi‑Syl supports multiple dialect profiles representing the major mutually intelligible varieties of the Zomi language.  
Each profile defines:

- **onsets**  
- **nuclei**  
- **codas**  
- **syllable rules**  
- **tone behavior (if applicable)**  
- **normalization rules**  

Profiles live in:

```bash
src/zomi_syl/profiles/
```

Each profile contains:

```bash
onsets.json
nuclei.json
codas.json
vowels.json
rules.json
profile.json
```

These files collectively define the phonotactic constraints for that dialect.

---

## **📜 Supported Dialects**

Zomi‑Syl v0.1.0 includes profiles for the following dialects and varieties:

### **ISO‑coded varieties**

These correspond to historically fragmented ISO 639‑3 codes but are **mutually intelligible Zomi varieties**:

- **csy — Siyin**  
- **ctd — Tedim**  
- **gnb — Gangte**  
- **kmm — Kom Rem**  
- **pck — Paite**  
- **vap — Vaiphei**  
- **smt — Simte**  
- **tcz — Thado / Thadou**  
- **zom — Zo / Zou**

### **Other Zomi varieties**

These are widely recognized Zomi groups not represented by ISO codes:

- **Mate**  
- **Thangkhal**

### **Composite / practical profiles**

These represent broader usage patterns:

- **India Zomi**  
- **Myanmar Zomi**  
- **Zolai Standard** (orthographic standard)

---

## **📁 Profile Directory Structure**

Example: Tedim profile

```bash
src/zomi_syl/profiles/tedim/
    onsets.json
    nuclei.json
    codas.json
    vowels.json
    rules.json
    profile.json
```

---

## **🔍 Listing Available Profiles**

Use the CLI:

```bash
zomi-syl profiles list
```

Example output:

```bash
tedim
paite
myanmar_zomi
india_zomi
zolai_standard
...
```

---

## **ℹ️ Viewing Profile Details**

```bash
zomi-syl profiles info tedim
```

This shows:

- dialect name  
- description  
- phonotactic inventory  
- rule count  
- version  
- backend compatibility  

---

## **🧩 Using a Specific Profile**

You can specify a profile for any syllabification command.

### CLI

```bash
zomi-syl syllabify itna --profile paite
```

### Python API

```python
import zomi_syl as zs

zs.syllabify("itna", profile="paite")
```

---

## **🧠 Why Profiles Matter**

Different Zomi varieties have small but meaningful differences:

- vowel length  
- diphthong inventory  
- coda restrictions  
- tone behavior  
- orthographic conventions  
- cluster permissibility  

Profiles allow Zomi‑Syl to:

- adapt syllabification to dialect norms  
- maintain consistency across corpora  
- support linguistic research  
- enable dialect‑specific evaluation  

---

## **🛠 Creating or Extending Profiles**

To create a new profile:

1. Copy an existing profile folder  
2. Edit `profile.json` (metadata)  
3. Update phonotactic files (`onsets.json`, `nuclei.json`, etc.)  
4. Add or modify rules in `rules.json`  
5. Validate:

```bash
zomi-syl profiles validate my_new_profile
```

See: **Adding New Backends**  
See: **Developer Documentation**

---

## **Next Steps**

- Install the library: **Installation**  
- Try the CLI: **Top‑Level Commands**  
- Benchmark backends: **Benchmarking Guide**  
- Add your own backend: **Adding New Backends**  

---
