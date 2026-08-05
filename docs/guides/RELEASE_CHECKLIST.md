# **RELEASE_CHECKLIST.md**  
## _<project> v<version> — Hybrid Release Checklist (Manual → CI)_

A strict, reusable release checklist for preparing and publishing a new version of **<project>**.  
All **manual steps must be completed before CI** is allowed to run.

---

# **A. Manual Steps (must be done *before* CI)**

## **A1. Versioning**
- [ ] Update version in `pyproject.toml`  
- [ ] Add entry to `CHANGELOG.md`  
- [ ] Confirm CLI reports correct version:

```bash
python -m <package> version
```

---

## **A2. Model Directory Structure**
Required layout:

```text
src/<package>/models/
  <backend-1>/
    <required-files>
  <backend-2>/
    <required-files>
```

Checklist:
- [ ] No deprecated model directories  
- [ ] Loader does not reference deprecated paths  
- [ ] Registry resolves `models/<model-name>/` correctly  
- [ ] Metadata fields (e.g., `storage.local_path`) correct  

---

## **A3. Packaging: Include All Required Files**
Ensure `pyproject.toml` includes:

```toml
[tool.setuptools.package-data]
<package> = ["models/**/*", "profiles/**/*", "config/*.toml"]
```

Verify:
- [ ] Model files included  
- [ ] Profiles included  
- [ ] Config files included  

Local test:

```bash
python -m build
pip install dist/<package>-<version>-py3-none-any.whl
python -m <package> <command> <args>
```

---

## **A4. CLI Validation**
Run:

```bash
python -m <package> version
python -m <package> <command> <args>
python -m <package> <command> --backend <backend-1> <args>
python -m <package> <command> --backend <backend-2> <args>
```

Confirm:
- [ ] No stack traces  
- [ ] No missing model errors  
- [ ] No fallback to deprecated paths  
- [ ] All backends load correctly  

---

## **A5. Profiles Validation**
Run:

```bash
python -m <package> profiles validate <profile-name>
```

Confirm:
- [ ] Profiles load  
- [ ] No missing keys  
- [ ] Validators pass  

---

## **A6. Documentation**
- [ ] README includes installation, quickstart, backend usage, examples, supported profiles  
- [ ] External resource links valid  

Optional:

```bash
twine check dist/*
```

---

## **A7. Code Cleanup**
- [ ] Remove development artifacts  
- [ ] Remove unused files  
- [ ] Ensure no temporary or experimental code remains  

---

## **A8. Makefile Developer Help Targets**
Check:

```bash
make help-devs
make help-cli
# Todo:
# make help-backends
# make help-models
```

---

## **A9. Licensing**
- [ ] LICENSE file present  
- [ ] Model/data licenses compatible  
- [ ] External repos referenced properly  

---

## **A10. Final Manual Sanity Check**
Install from wheel:

```bash
pip uninstall -y <package>
pip install dist/<package>-<version>-py3-none-any.whl
python -m <package> <command> <args>
```

Verify:
- [ ] CLI works  
- [ ] All backends load  
- [ ] No missing files  
- [ ] No warnings  

---

# **B. CI‑Driven Steps (automated)**

## **B1. CI Build Pipeline**
- [ ] CI builds wheel + sdist in a clean environment  
- [ ] No leftover artifacts (`dist/`, `build/`, `.egg-info/`)  
- [ ] Package‑data rules include all required assets  
- [ ] Version in `pyproject.toml` matches the release tag  

---

## **B2. CI Test Pipeline**
- [ ] All tests pass  
- [ ] Regression tests pass  
- [ ] No unexpected failures  
- [ ] No warnings or deprecations flagged  

---

## **B3. CI Lint & Type‑Check Pipeline**
- [ ] Linting passes  
- [ ] Formatting passes  
- [ ] Type checks pass  

---

## **B4. CI Documentation Pipeline**
- [ ] README renders correctly  
- [ ] Documentation builds (if applicable)  
- [ ] No broken links or missing assets  

---

## **B5. CI Publish Pipeline**
Triggered only on tagged releases.

- [ ] PyPI credentials stored in CI secrets  
- [ ] CI uploads artifacts to PyPI  
- [ ] Upload succeeds  
- [ ] PyPI page updates with new version  

---
