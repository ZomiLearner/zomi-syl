# Project Versioning Rules (Semantic Versioning)

## Purpose
This document defines how version numbers must be assigned and incremented for this project using **Semantic Versioning (SemVer)**. It ensures consistent, predictable release behavior across all contributors.

## Semantic Versioning Format
Semantic Versioning follows the structure:

```
MAJOR.MINOR.PATCH
```

### MAJOR
Breaking changes that are incompatible with previous versions.

### MINOR
New functionality added in a backward‑compatible manner.

### PATCH
Backward‑compatible bug fixes.

## Versioning Principles

### MAJOR Version Changes
A MAJOR version increment occurs when:
- Public APIs change in a way that breaks existing usage.
- Functions, classes, or modules are removed or renamed.
- Behavior changes alter expected outputs.
- Architectural changes affect integration points.

**Examples:**
- Removing deprecated functions.
- Changing return types or parameter structures.
- Rewriting core logic that alters expected behavior.

### MINOR Version Changes
A MINOR version increment occurs when:
- New features are added without breaking existing functionality.
- Enhancements improve performance or usability while maintaining compatibility.
- New configuration options are introduced but remain optional.

**Examples:**
- Adding new API endpoints.
- Introducing optional parameters.
- Adding new modules that do not affect existing ones.

### PATCH Version Changes
A PATCH version increment occurs when:
- Bugs are fixed without altering existing behavior.
- Documentation updates accompany code changes.
- Internal refactoring does not affect external interfaces.

**Examples:**
- Fixing typos or incorrect logic.
- Updating dependency versions in a backward‑compatible way.
- Correcting documentation or comments.

## Pre‑Release Versions
Pre‑release versions use identifiers appended to the version number:

```
MAJOR.MINOR.PATCH-alpha
MAJOR.MINOR.PATCH-beta
MAJOR.MINOR.PATCH-rc
```

Use these for:
- Early testing.
- Experimental features.
- Release candidates.

## Build Metadata
Build metadata may be appended using a plus sign:

```
MAJOR.MINOR.PATCH+build.123
```

Metadata does not affect version precedence.

## Versioning Workflow
1. Identify the type of change (MAJOR, MINOR, PATCH).
2. Update the version number in `pyproject.toml`.
3. Document the change in `CHANGELOG.md`.
4. Tag the release using Git:

```
git tag vMAJOR.MINOR.PATCH
git push origin --tags
```

5. Publish release notes in `docs/releases/`.

## Decision Guide

| Change Type | Description | Version Bump |
|-------------|-------------|--------------|
| Breaking change | Incompatible API or behavior | MAJOR |
| New feature | Backward‑compatible addition | MINOR |
| Bug fix | Backward‑compatible correction | PATCH |
| Documentation | No code changes | PATCH |
| Dependency update | Backward‑compatible | PATCH |
| Dependency update | Breaking change | MAJOR |

## Best Practices
- Always update documentation alongside version changes.
- Avoid unnecessary MAJOR releases; group breaking changes when possible.
- Ensure MINOR releases remain backward‑compatible.
- Keep PATCH releases small and focused.
- Use pre‑release tags for unstable or experimental features.

## Conclusion
Following these rules ensures predictable versioning, clear communication with users, and stable release management across the project. Consistent application of Semantic Versioning helps maintain reliability and trust in the software lifecycle.
```
