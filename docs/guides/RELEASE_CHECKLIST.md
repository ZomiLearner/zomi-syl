# **RELEASE_CHECKLIST.md**  

### _zomi‑syl v0.1.0 — Release Preparation Checklist_

A polished, production‑ready **`RELEASE_CHECKLIST.md`** for **zomi‑syl v0.1.0**, written as a standalone document.

This document lists all required steps before publishing **zomi‑syl v0.1.0** to PyPI.  
Version 0.1.0 includes **rule** and **crf** backends only.

---

## **1. Versioning**
- [ ] Update `src/zomi_syl/version.py`:

  ```
  __version__ = "0.1.0"
  ```

- [ ] Ensure `pyproject.toml` version matches.
- [ ] Add a v0.1.0 entry to `CHANGELOG.md`.

---

## **2. Model Directory Structure**
Models must follow the required layout:

```
src/zomi_syl/models/
  crf/
    config.json
    crf_syllabifier.joblib
    eval.txt
    stats.txt

  rule/
    ruleset.json
    metadata.json
```

Checklist:
- [ ] No models under `models/bundled/`
- [ ] Loader does **not** reference `bundled/`
- [ ] Registry resolves `models/<model-name>/` correctly
- [ ] `storage.local_path` in metadata is `""` (empty)

---

## **3. Packaging: Include All Required Files**
Ensure `pyproject.toml` includes:

```
[tool.setuptools.package-data]
zomi_syl = ["models/**/*", "profiles/**/*", "config/*.toml"]
```

Verify:
- [ ] CRF model files included in wheel  
- [ ] Rule model files included in wheel  
- [ ] Profiles included  
- [ ] Config files included  

Test:

```
python -m build
pip install dist/zomi_syl-0.1.0-py3-none-any.whl
python -m zomi_syl syllabify "themthum"
```

---

## **4. CLI Validation**
Test all CLI entry points:

- [ ] `python -m zomi_syl syllabify "themthum"`
- [ ] `python -m zomi_syl syllabify --backend rule "kiginna"`
- [ ] `python -m zomi_syl syllabify --backend crf "kiginna"`

Confirm:
- [ ] No stack traces  
- [ ] No missing model errors  
- [ ] No fallback to bundled paths  
- [ ] No transformer backend errors  

---

## **5. Tests**
Run:

```
pytest -q
```

Verify:
- [ ] `test_crf_consistency.py` passes  
- [ ] `test_crf_regression.py` passes  
- [ ] No unexpected failures  

---

## **6. Profiles Validation**
Run:

```
python -m zomi_syl validate-profile tedim
python -m zomi_syl validate-profile zolai_standard
python -m zomi_syl validate-profile myanmar_zomi
```

Confirm:
- [ ] All profiles load  
- [ ] No missing keys  
- [ ] Validators pass  

---

## **7. Documentation**
- [ ] README.md includes:
  - installation instructions  
  - quickstart  
  - backend usage (rule + crf)  
  - example commands  
  - supported profiles  
  - link to HF models  

- [ ] Validate PyPI rendering:

  ```
  twine check dist/*
  ```

---

## **8. Code Cleanup**
Remove development artifacts:

- [ ] `src/zomi_syl/models/loader_before_using_crf.py`
- [ ] `src/zomi_syl/temp.py`
- [ ] Unused scripts in `scripts/`
- [ ] Debug prints in loader/engine

---

## **9. Makefile Developer Help Targets**
Ensure the following exist and work:

- [ ] help-devs
- [ ] help-backends
- [ ] help-models
- [ ] help-cli

---

## **10. Licensing**
- [ ] LICENSE file present  
- [ ] Model licenses compatible  
- [ ] HF repos referenced in README  

---

## **11. Remove Old Build Artifacts**
Before final build:

```
rm -rf dist/ build/ src/zomi_syl.egg-info/
```

Checklist:
- [ ] egg-info removed  
- [ ] old wheels removed  

---

## **12. Final Sanity Check**
Install from wheel:

```
pip uninstall -y zomi_syl
pip install dist/zomi_syl-0.1.0-py3-none-any.whl
python -m zomi_syl syllabify "themthum"
```

Verify:
- [ ] CLI works  
- [ ] CRF backend loads  
- [ ] Rule backend loads  
- [ ] No missing files  
- [ ] No warnings  

---

## **13. Publish**
When everything passes:

```
twine upload dist/*
```
