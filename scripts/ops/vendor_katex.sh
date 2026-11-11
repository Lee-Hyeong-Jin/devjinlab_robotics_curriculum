#!/usr/bin/env bash
# Re-vendor the KaTeX copy that `rc site build` ships (server review SRV-17).
#
#   bash scripts/ops/vendor_katex.sh 0.19.1
#
# Downloads the npm tarball into a scratch directory, copies only the files we ship
# (minified js/css, the auto-render contrib script, woff2 fonts, LICENSE), then rewrites
# VERSION and MANIFEST.sha256. tests/test_katex_assets.py checks the result.
set -euo pipefail

version="${1:?usage: scripts/ops/vendor_katex.sh <version>   e.g. 0.19.1}"
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
dest="$root/src/robotics_curriculum/site/assets/katex"
[ -d "$dest" ] || { echo "no vendored KaTeX at $dest" >&2; exit 1; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cd "$work"

url="https://registry.npmjs.org/katex/-/katex-$version.tgz"
echo "--- downloading $url"
curl -fsSL -o katex.tgz "$url"
sha="$(sha512sum katex.tgz | cut -d' ' -f1)"
integrity="sha512-$(openssl dgst -sha512 -binary katex.tgz | base64 -w0)"
tar -xzf katex.tgz

echo "--- replacing the shipped files"
rm -f "$dest"/katex.min.css "$dest"/katex.min.js "$dest"/contrib/auto-render.min.js
rm -f "$dest"/fonts/*.woff2
cp package/dist/katex.min.css package/dist/katex.min.js "$dest"/
cp package/dist/contrib/auto-render.min.js "$dest"/contrib/
cp package/dist/fonts/*.woff2 "$dest"/fonts/
cp package/LICENSE "$dest"/LICENSE

cat >"$dest/VERSION" <<EOF
KaTeX $version (MIT), vendored from $url
(sha512 $sha,
 npm integrity $integrity).
Only woff2 fonts are kept.
Used by \`rc site build\` so math renders without network access.
Re-vendor with scripts/ops/vendor_katex.sh <version>; MANIFEST.sha256 pins every file.
EOF

cd "$dest"
find . -type f ! -name MANIFEST.sha256 -printf '%P\n' | sort | xargs sha256sum >MANIFEST.sha256

echo "--- KaTeX $version vendored ($(wc -l <MANIFEST.sha256) files pinned)"
echo "    run: uv run pytest -q tests/test_katex_assets.py"
