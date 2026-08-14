#!/usr/bin/env bash
# Build a single PDF from one section of the documentation.
#
# Read-only: this script never modifies the markdown. It renders a copy in a
# temporary directory and writes the PDF to the path given.
#
# Requires: python3, and either chromium or google-chrome for the PDF step.
# Uses ghostscript to shrink the result if it is installed; works without it.
#
# Usage: ./build-pdf.sh [section] [output.pdf]
#   ./build-pdf.sh                     -> extensions, junk-store-extensions.pdf
#   ./build-pdf.sh user                -> user, junk-store-user.pdf
#   ./build-pdf.sh user /tmp/out.pdf

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECTION="${1:-extensions}"
DOCS="${HERE}/${SECTION}"
OUT="${2:-${HERE}/junk-store-${SECTION}.pdf}"

if [ ! -d "${DOCS}" ]; then
    echo "No such section: ${SECTION}" >&2
    echo "Sections: $(cd "${HERE}" && find . -maxdepth 1 -mindepth 1 -type d \
        -not -name '.*' -not -name tools -printf '%f ')" >&2
    exit 1
fi
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

# Reading order per section. Mirrors each section's README, which is the only
# other place the order is recorded. The glossary lives at the docs root and is
# appended to every section, since it serves all of them.
if [ "${SECTION}" = "user" ]; then
TITLE="Junk Store Pro"
SUBTITLE="User manual"
NOTE="This is a printable copy of the Junk Store Pro user manual. It documents \
Junk Store Pro, not the free Decky plugin. It was written by working through \
the source, and is a first pass at material that had not been documented \
before. It is accurate where it makes a claim, but it is not complete. Cross \
references between pages appear as plain text here; the online version links \
them."
PAGES=(
    "introduction.md"
    "main-menu.md"
    "games.md"
    "game-page.md"
    "download-queue.md"
    "game-settings.md"
    "proton-settings.md"
    "store-settings.md"
    "store-settings-reference.md"
    "setting-up-by-hand.md"
    "file-manager.md"
    "file-manager-driving.md"
    "file-manager-steam.md"
    "file-manager-tools.md"
    "networking.md"
    "file-manager-reference.md"
    "settings.md"
    "diagnostics.md"
    "../glossary.md"
)
else
TITLE="Junk Store Pro"
SUBTITLE="Extension developer guide"
NOTE="This is a printable copy of the extension documentation. It documents \
Junk Store Pro, not the free Decky plugin. It was written by working through \
the source, and is a first pass at material that had not been documented \
before. It is accurate where it makes a claim, but it is not complete. Cross \
references between pages appear as plain text here; the online version links \
them."
PAGES=(
    "introduction.md"
    "workflows.md"
    "guides/quickstart.md"
    "guides/overriding-actions.md"
    "guides/authoring-by-hand.md"
    "guides/emulators-and-roms.md"
    "guides/non-launchable-items.md"
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
    "../glossary.md"
)
fi

python3 "${HERE}/tools/md2html.py" \
    --title "${TITLE}" --subtitle "${SUBTITLE}" --note "${NOTE}" \
    "${DOCS}" "${WORK}/doc.html" "${PAGES[@]}"

"${BROWSER}" --headless --disable-gpu --no-sandbox \
    --no-pdf-header-footer \
    --print-to-pdf="${OUT}" \
    "file://${WORK}/doc.html" >/dev/null 2>&1

# Chromium writes each screenshot into the PDF far larger than it needs to be:
# 4 MB of source images comes out around 30 MB. Ghostscript recompresses them
# without changing their size on the page or their pixel dimensions. Optional,
# so the build still works without it.
if command -v gs >/dev/null 2>&1; then
    if gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.5 -dPDFSETTINGS=/printer \
          -dNOPAUSE -dQUIET -dBATCH -sOutputFile="${WORK}/small.pdf" "${OUT}"; then
        mv "${WORK}/small.pdf" "${OUT}"
    fi
fi

echo "Wrote ${OUT}"
