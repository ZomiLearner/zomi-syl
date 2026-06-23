# **CONTRIBUTING.md — Linguistic Contributors Guide**

## **🌱 Welcome**

Thank you for contributing to **Zomi‑Syl**, a community‑driven project to build the first high‑quality, reproducible NLP tools for the Zomi language.

This guide is for **linguistic contributors** — speakers, annotators, and linguists who help with:

- syllabification  
- tone classification  
- morphological segmentation  
- lexicon entries  
- example sentences  
- variant checking  
- dataset corrections  

You do **not** need programming experience to contribute.

---

## **🧭 What You Can Contribute**

Linguistic contributors can help with:

- **Correcting syllabification**  
- **Providing tone‑accurate examples**  
- **Identifying ambiguous or irregular words**  
- **Adding lexicon entries**  
- **Providing example sentences**  
- **Correcting morphological segmentation**  
- **Reporting inconsistencies**  
- **Validating golden regression outputs**  

If you want to explore specific areas:

- syllable variants  
- tone classes  
- derivational suffixes  
- lexicon entry structure

---

## **📦 Project Structure (Linguist‑Relevant)**

```bash
data/                     → small linguistic metadata files
training/data/            → cleaned syllabification datasets
tests/golden/             → golden syllabification outputs
src/zomi_syl/lexicon/     → lexicon entries (future)
```

You will mostly interact with:

- **Google Sheets** (syllabification dataset)  
- **TSV files** (syllable variants, tone lists)  
- **golden regression outputs** (for validation)  

---

## **📝 How to Contribute Linguistic Data**

### **1. Syllabification Corrections**

If you find a word that is syllabified incorrectly:

- provide the correct syllabification  
- include tone if known  
- include a short example sentence (optional)

Example:

```bash
Word: themthum
Correct: them-thum
Tone: H-L
Example: A themthum a om.
```

---

### **2. Tone Corrections**

Tone is essential for:

- rule‑based syllabification  
- CRF training  
- lexicon entries  
- morphological analysis  

If you correct tone:

- specify the tone class (H, L, F, R, etc.)  
- provide minimal pairs if possible  
- note dialect differences if relevant  

---

### **3. Morphological Segmentation**

If you contribute segmentation:

- segment using hyphens  
- identify derivational suffixes  
- note tone changes  
- provide glosses if possible  

Example:

```bash
khaang-vui
khaang = dry
-vui   = become (inchoative)
```

---

### **4. Lexicon Entries**

When adding or correcting lexicon entries:

- provide lemma  
- provide definition  
- provide example sentence  
- provide tone  
- provide morphological notes if relevant  

If you want to see the full contributor template:

- lexicon entry template

---

### **5. Identifying Ambiguous Words**

Ambiguous words are words with **multiple valid syllabifications**.  
These must **not** appear in the golden regression set.

If you find one:

- list all valid variants  
- provide examples for each  
- note dialect differences  

Example:

```bash
Word: suahin
Variants:
  1. sua-hin
  2. suah-in
```

---

## **🧪 Validating Golden Regression**

Linguistic contributors help ensure the golden set is:

- correct  
- consistent  
- tone‑accurate  
- free of ambiguous words  

To validate:

1. Look at `tests/golden/crf_golden.tsv`  
2. Check each word’s syllabification  
3. Report any incorrect or ambiguous entries  

You can also request a CRF prediction check:

- check CRF output

---

## **📣 Reporting Issues**

When reporting a linguistic issue, include:

- the word  
- expected syllabification  
- tone  
- dialect (if relevant)  
- example sentence  
- explanation of the issue  

Example:

```text
Issue: Incorrect syllabification
Word: upa
Expected: u-pa
Actual: up-a
Dialect: Tedim
Notes: The vowel boundary is misidentified.
```

---

## **🤝 Collaboration Principles**

- Respect dialect diversity  
- 
- Provide examples when possible  
- Explain reasoning clearly  
- Avoid prescriptive judgments  
- Focus on linguistic evidence  
- Be patient with model limitations  

---

## **❤️ Thank You**

Your contributions help build the first comprehensive, community‑driven NLP toolkit for the Zomi language.  
Every correction, example, and insight strengthens the linguistic foundation of the project.

---
