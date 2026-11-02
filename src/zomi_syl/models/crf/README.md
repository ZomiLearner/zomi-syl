# CRF Model Conventions

- hashes = sha256 of smudged file (what ships), not the LFS pointer;

- `role: "model"` = a full loadable `sklearn_crfsuite.estimator.CRF`; `"wrapper"`/`"pointer"` reserved for future use;

- `format: "crfsuite+joblib"` = two independently loadable CRF artifacts, not model+wrapper (unless/until proven);

- append-only; one line per released tag; release tags are immutable (no force-push/rewrite/filter-repo);
