// Render pymdownx.arithmatex (generic mode) output with the vendored KaTeX.
// document$ is mkdocs-material's page-load observable (works with instant navigation).
function rcRenderMath(root) {
  if (typeof renderMathInElement !== "function") return;
  renderMathInElement(root, {
    delimiters: [
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true },
    ],
    throwOnError: false,
  });
}
if (typeof document$ !== "undefined") {
  document$.subscribe(function (doc) { rcRenderMath(doc.body); });
} else {
  document.addEventListener("DOMContentLoaded", function () { rcRenderMath(document.body); });
}
