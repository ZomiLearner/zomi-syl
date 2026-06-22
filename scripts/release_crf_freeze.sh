#!/usr/bin/env bash
set -euo pipefail

# ================================================================
#  ZOMI‑SYL — CRF RELEASE FREEZE PIPELINE
# ================================================================
# This script performs the FULL release workflow:
#
#   1. Download zomi_syllabified_human.tsv from Google Sheets
#   2. Clean dataset → zomi_only.tsv, non_zomi.tsv, mixed_unsure.tsv
#   3. Train CRF model → training/model/crf/
#   4. Freeze model into package folder (TEMPORARY)
#   5. Build wheel (wheel includes frozen model)
#   6. Remove model from repo (repo stays clean)
#
# Usage:
#   ./scripts/release_crf_freeze.sh \
#       --url "https://docs.google.com/spreadsheets/d/XXXX/edit#gid=0" \
#       --sheet "Sheet1"
#
# ================================================================

URL=""
SHEET="zomi_syllabified_human"

# ------------------------------------------------
# Parse arguments
# ------------------------------------------------
while [[ $# -gt 0 ]]; do
  case $1 in
    --url)
      URL="$2"
      shift 2
      ;;
    --sheet)
      SHEET="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$URL" ]]; then
  echo "❌ ERROR: --url is required"
  exit 1
fi

echo "🚀 Starting CRF release freeze…"
echo "URL: $URL"
echo "Sheet: $SHEET"
echo ""

# ------------------------------------------------
# 1. Fetch Google Sheet → get_zomi_syllabified_human.tsv
# ------------------------------------------------
echo "📥 Fetching zomi_syllabified_human.tsv from Google Sheets…"
make get-zomi-syllabified-human URL="$URL" SHEET="$SHEET"
echo ""

# ------------------------------------------------
# 2. Clean dataset
# ------------------------------------------------
echo "🧹 Cleaning dataset…"
make clean-dataset
echo ""

# ------------------------------------------------
# 3. Train CRF
# ------------------------------------------------
echo "🔄 Training CRF model…"
make train-crf
echo ""

# ------------------------------------------------
# 4. Freeze model into package folder
# ------------------------------------------------
FREEZE_DIR="training/model/crf"
PKG_DIR="src/zomi_syl/models/crf"

echo "📦 Freezing CRF model into package directory…"
mkdir -p "$PKG_DIR"
cp "$FREEZE_DIR"/* "$PKG_DIR"/
echo "✓ Model copied to $PKG_DIR"
echo ""

# ------------------------------------------------
# 5. Build wheel
# ------------------------------------------------
echo "🏗️ Building wheel…"
rm -rf dist/
make build
echo ""

# ------------------------------------------------
# 6. Remove model from repo (keep repo clean)
# ------------------------------------------------
echo "🧹 Removing temporary model from repo…"
rm -rf "$PKG_DIR"
echo "✓ Repo cleaned"
echo ""

# ------------------------------------------------
# Done
# ------------------------------------------------
echo "🎉 CRF release freeze complete!"
echo "📦 Wheel available in: dist/"
echo ""
echo "Next steps:"
echo "  1. pip install --force-reinstall dist/zomi_syl-*.whl"
echo "  2. make test"
echo "  3. git commit -am 'Release vX.Y.Z'"
echo "  4. git tag vX.Y.Z && git push --tags"
echo ""
echo "✨ Your wheel now contains the frozen CRF model."
