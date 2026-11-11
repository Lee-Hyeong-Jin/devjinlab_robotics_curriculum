/**
 * Put every `$$` display-math marker on a line of its own.
 *
 * The curriculum writes display formulas with content on the marker line, either
 * on one line (`$$x = y$$`) or across several:
 *
 * ```text
 * $$T_{ac} = T_{ab}T_{bc}, \qquad
 * T_{ab}^{-1} = T_{ba}$$
 * ```
 *
 * KaTeX auto-render on the static site reads both as display math. `remark-math`
 * does not: it parses math-flow like a fenced code block, so text after the
 * opening `$$` is *meta* (silently dropped) and a line that merely ends with `$$`
 * is not a closing fence. The block then never closes and swallows the rest of
 * the lesson, which reaches the reader as raw TeX — the formulas "look broken".
 *
 * Splitting the markers onto their own lines makes `remark-math` see a real math
 * fence, so the web and the static site render the same thing (AC-WEB.2).
 *
 * Fenced code blocks are left untouched, and a `$$` inside an inline-code span
 * is not a marker.
 */
const FENCE = /^\s{0,3}(`{3,}|~{3,})/

/** Offsets of `$$` markers in a line, skipping inline-code spans. */
function markerOffsets(line: string): number[] {
  const out: number[] = []
  let index = 0
  while (index < line.length) {
    const char = line[index]
    if (char === '`') {
      // Skip to the end of the code span (or the line, when it is unterminated).
      let run = 0
      while (line[index + run] === '`') run += 1
      const ticks = line.slice(index, index + run)
      const close = line.indexOf(ticks, index + run)
      index = close === -1 ? line.length : close + run
      continue
    }
    if (char === '$' && line[index + 1] === '$') {
      out.push(index)
      index += 2
      continue
    }
    index += 1
  }
  return out
}

/** Push `text` as its own line when it holds anything but whitespace. */
function pushContent(out: string[], text: string): void {
  const trimmed = text.trim()
  if (trimmed !== '') out.push(trimmed)
}

export function normalizeDisplayMath(markdown: string): string {
  const lines = markdown.split('\n')
  const out: string[] = []
  let codeFence: string | null = null
  let inMath = false

  for (const line of lines) {
    const fenceMatch = FENCE.exec(line)
    if (fenceMatch && !inMath) {
      const marker = fenceMatch[1] ?? ''
      if (codeFence === null) codeFence = marker[0] ?? null
      else if (marker[0] === codeFence) codeFence = null
      out.push(line)
      continue
    }
    if (codeFence !== null) {
      out.push(line)
      continue
    }

    const markers = markerOffsets(line)
    if (markers.length === 0) {
      out.push(line)
      continue
    }

    let cursor = 0
    for (const at of markers) {
      const segment = line.slice(cursor, at)
      if (inMath) pushContent(out, segment)
      else if (segment.trim() !== '') out.push(segment.trimEnd())
      out.push('$$')
      inMath = !inMath
      cursor = at + 2
    }
    const tail = line.slice(cursor)
    if (inMath) pushContent(out, tail)
    else if (tail.trim() !== '') out.push(tail.trimStart())
  }

  return out.join('\n')
}
