# **RELEASE_CHECKLIST_v0.1.0**

## **1. Preconditions**
- [ ] All ambiguous words removed from **CRF golden set**  
- [ ] All tests passing locally (`make test`)  
- [ ] Google Sheet URL + sheet name confirmed  
- [ ] No model files present in `src/zomi_syl/models/crf/`  
- [ ] Version bumped to `0.1.1` in code (will finalize in step 8)

---

## **2. Refresh Data**
- [ ] Fetch latest human syllabified dataset  
  ```
  make get-zomi-syllabified-human URL=<sheet-url> SHEET=<sheetname>
  ```
- [ ] Clean dataset  
  ```
  make clean-dataset
  ```
- [ ] Confirm `training/data/zomi_only.tsv` exists and is non‑empty

---

## **3. Train CRF Model**
- [ ] Train CRF  
  ```
  make train-crf
  ```
- [ ] Confirm output files in `training/model/crf/`:
  - `crf_syllabifier.joblib`
  - `config.json`
  - `stats.txt`
  - `eval.txt`

---

## **4. Regenerate Golden Regression**
- [ ] Regenerate golden CRF outputs  
  ```
  python scripts/get_golden_crf_frozen_data.py
  ```
- [ ] Confirm:
  - `tests/golden/crf_golden.tsv` updated  
  - No ambiguous words included  
  - No multi‑variant words included  
- [ ] Optional: inspect CRF predictions  
  ```
  make check-crf WORDS="ama upa zawlai"
  ```

---

## **5. Freeze + Package Model**
- [ ] Run release freeze script  
  ```
  ./scripts/release_crf_freeze.sh --url <sheet-url> --sheet <sheetname>
  ```
- [ ] Confirm:
  - Wheel built in `dist/`  
  - Temporary model removed from repo  
  - No model files left in `src/zomi_syl/models/crf/`

---

## **6. Validate Wheel**
- [ ] Install wheel  
  ```
  pip install --force-reinstall dist/zomi_syl-*.whl
  ```
- [ ] Run full test suite  
  ```
  make test
  ```
- [ ] Confirm:
  - All tests pass  
  - Golden regression matches  
  - CRFBackend loads packaged model  

---

## **7. Documentation Updates**
- [ ] Update `CHANGELOG.md` for v0.1.0  
- [ ] Update README if needed:
  - Installation  
  - Example usage  
  - Backend notes  
  - Release notes  

---

## **8. Versioning**
- [ ] Update version in:
  - `src/zomi_syl/version.py`
  - `pyproject.toml`
- [ ] Commit changes  
  ```
  git commit -am "Release v0.1.0"
  ```

---

## **9. Tag + Push**
- [ ] Tag release  
  ```
  git tag v0.1.0
  git push --tags
  ```

---

## **10. Publish to PyPI**
- [ ] Upload  
  ```
  twine upload dist/*
  ```

---

## **11. Post‑Release Validation**
- [ ] Install from PyPI in a clean environment  
- [ ] Run:
  ```
  python -m zomi_syl syllabify "themthum"
  ```
- [ ] Confirm correct output  
- [ ] Confirm CRFBackend loads packaged model  

---

## **12. Optional Enhancements**
- [ ] Add **ambiguous‑word detector**  
- [ ] Add **golden‑set enforcement**  
- [ ] Add **CRF vs rule‑based diff tool**  
- [ ] Add **transformer backend regression tests**  

---
