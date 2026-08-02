#!/usr/bin/env bash
# Build a single PDF from the extension documentation.
#
# Read-only: this script never modifies the markdown. It renders a copy in a
# temporary directory and writes the PDF to the path given (default ./junk-store-extensions.pdf).
#
# Requires: python3, and either chromium or google-chrome for the PDF step.
# Usage: ./build-pdf.sh [output.pdf]

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Docs are organised into top-level sections; this builds the extensions one.
DOCS="${HERE}/extensions"
OUT="${1:-${HERE}/junk-store-extensions.pdf}"
WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

BROWSER=""
for c in chromium google-chrome-stable google-chrome chrome; do
    if command -v "$c" >/dev/null 2>&1; then BROWSER="$c"; break; fi
done
if [ -z "${BROWSER}" ]; then
    echo "No chromium or chrome found; cannot render the PDF." >&2
    exit 1
fi

# Reading order. Mirrors README, which is the only place the order is recorded.
PAGES=(
    "introduction.md"
    "workflows.md"
    "guides/quickstart.md"
    "guides/overriding-actions.md"
    "guides/authoring-by-hand.md"
    "guides/emulators-and-roms.md"
    "guides/when-a-game-will-not-run.md"
    "concepts/how-extensions-are-found.md"
    "concepts/how-launching-works.md"
    "concepts/config-schema.md"
    "concepts/config-layering.md"
    "concepts/the-generator.md"
    "reference/custom-scripts.md"
    "reference/script-output.md"
    "reference/static-json.md"
    "reference/downloader-protocol.md"
    "reference/settings.md"
    "reference/actions-and-types.md"
    "reference/download-methods.md"
    "reference/dosbox-import.md"
    "reference/sharing-and-licensing.md"
    "troubleshooting.md"
    # Lives at the docs root: it serves every section, not just this one.
    "../glossary.md"
)

python3 "${HERE}/tools/md2html.py" "${DOCS}" "${WORK}/doc.html" "${PAGES[@]}"

"${BROWSER}" --headless --disable-gpu --no-sandbox \
    --no-pdf-header-footer \
    --print-to-pdf="${OUT}" \
    "file://${WORK}/doc.html" >/dev/null 2>&1

echo "Wrote ${OUT}"
