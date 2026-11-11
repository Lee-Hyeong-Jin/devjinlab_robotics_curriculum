/**
 * Normalise `$$…$$` written on a single line into a math block.
 *
 * The curriculum writes display formulas as one line (`$$x = y$$`), which is what
 * KaTeX auto-render on the static site treats as display math. `remark-math`
 * only treats a `$$` fence spanning several lines as display math, so without
 * this the same formula would render inline on the web and the two renderings
 * would not match (AC-WEB.2: "정적 사이트와 같은 의미로 보인다").
 *
 * Lines inside a fenced code block are left alone.
 */
const SINGLE_LINE_DISPLAY = /^\$\$(.+)\$\$$/
const FENCE = /^\s{0,3}(`{3,}|~{3,})/

export function normalizeDisplayMath(markdown: string): string {
  const lines = markdown.split('\n')
  const out: string[] = []
  let fence: string | null = null

  for (const line of lines) {
    const fenceMatch = FENCE.exec(line)
    if (fenceMatch) {
      const marker = fenceMatch[1] ?? ''
      if (fence === null) fence = marker[0] ?? null
      else if (marker[0] === fence) fence = null
      out.push(line)
      continue
    }
    if (fence !== null) {
      out.push(line)
      continue
    }
    const match = SINGLE_LINE_DISPLAY.exec(line.trim())
    const body = match?.[1]?.trim()
    if (body && !body.includes('$$')) {
      out.push('$$', body, '$$')
      continue
    }
    out.push(line)
  }

  return out.join('\n')
}
