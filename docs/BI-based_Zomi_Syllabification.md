# O is NOT needed for Zomi syllabification

## 1. What “O” means in BIO tagging

In standard BIO tagging:

- **B** = Begin a labeled span  
- **I** = Inside a labeled span  
- **O** = Outside any labeled span  

The **O** tag is only meaningful when some tokens are *not part of any unit* the subject of interest (e.g., non-entity words in NER).

---

## 2. Why “O” does not make sense for Zomi syllabification

In Zomi syllabification:

- Every **character** in a word belongs to **some syllable**.
- There are **no characters** that are “outside” syllables.
- Syllables are **contiguous sequences** of characters.

Therefore:

- There is **no valid position** where a character should be tagged as **O**.
- Introducing **O** would create linguistically impossible patterns (e.g., a character “outside” any syllable).

---

## 3. Correct tagset for Zomi syllabification

For Zomi syllable segmentation, the correct tagset is:

- **B** = Begin a new syllable  
- **I** = Inside the current syllable  

Example: `itna` → `["i","t","n","a"]` with tags:

- `B I B I` → `it-na`

No **O** is needed or meaningful here.

---

## 4. How hyphens are handled (e.g., `ki-itna`)

Hyphens in Zomi orthography (e.g., `ki-itna`) are:

- **pre-existing syllable boundaries**, not characters to be tagged
- stripped out **before** CRF tagging
- recorded via flags and reinserted later

So the CRF sees only real characters, not hyphens.  
There is still **no position** where an **O** tag would be appropriate.

---

## 5. When “O” *is* needed (for contrast)

The **O** tag is essential in tasks where some tokens are outside labeled units, such as:

- Named Entity Recognition (NER)
- Chunking / shallow parsing
- Slot filling (e.g., virtual assistants)
- Event or relation extraction
- Sparse token classification (e.g., toxic spans, keyphrases)

In these tasks, many tokens are **not** part of any labeled span, so **O** is required.

In Zomi syllabification, this situation never arises.

---

## 6. Conclusion

- **O is NOT needed for Zomi syllabification.**
- The correct CRF tagset is **only**: `["B", "I"]`.
- Every character belongs to a syllable; there is no “outside”.
- Hyphens are handled structurally (pre-split), not via tagging.

BIO with **B** and **I** is the linguistically and technically correct choice for Zomi syllable segmentation.
