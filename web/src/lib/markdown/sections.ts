/**
 * Drop the lesson sections the screen already shows as its own UI.
 *
 * `GET /lessons/{id}` returns the whole Markdown in `body` *and* the pieces the
 * screen needs separately (`study_method`, the quiz, the resources). The lesson
 * screen renders the study method in its highlighted card and links to the quiz
 * screen, so leaving those sections in the body showed the study method twice
 * and printed the quiz's YAML source as a code block.
 *
 * `rc site build` does the same thing differently: one page shows everything, so
 * it turns the quiz fence into a readable question list instead of removing it.
 */
const HEADING = /^##\s+\S/
const FENCE = /^\s{0,3}(`{3,}|~{3,})/
const QUIZ_FENCE = /^\s{0,3}(`{3,}|~{3,})\s*quiz\s*$/

interface Section {
  /** The `## …` line, or `undefined` for the text before the first heading. */
  heading?: string
  lines: string[]
}

/** Split into `## ` sections; headings inside fenced code are not headings. */
function split(markdown: string): Section[] {
  const sections: Section[] = [{ lines: [] }]
  let fence: string | null = null

  for (const line of markdown.split('\n')) {
    const fenceMatch = FENCE.exec(line)
    if (fenceMatch) {
      const marker = (fenceMatch[1] ?? '')[0] ?? null
      if (fence === null) fence = marker
      else if (marker === fence) fence = null
    } else if (fence === null && HEADING.test(line)) {
      sections.push({ heading: line, lines: [line] })
      continue
    }
    sections[sections.length - 1]?.lines.push(line)
  }
  return sections
}

/** The section's text with every ```` ```quiz ```` fence taken out. */
function withoutQuizFences(lines: readonly string[]): { kept: string[]; removed: boolean } {
  const kept: string[] = []
  let fence: string | null = null
  let removed = false

  for (const line of lines) {
    if (fence !== null) {
      if (FENCE.exec(line)?.[1]?.[0] === fence) fence = null
      continue
    }
    const quiz = QUIZ_FENCE.exec(line)
    if (quiz) {
      fence = (quiz[1] ?? '')[0] ?? null
      removed = true
      continue
    }
    kept.push(line)
  }
  return { kept, removed }
}

export interface StripOptions {
  /** `study_method` from the API; the section holding exactly this text is dropped. */
  studyMethod?: string | null
}

export function stripLessonSections(
  body: string | null | undefined,
  { studyMethod }: StripOptions = {},
): string {
  if (!body) return ''
  const study = studyMethod?.trim()
  const out: string[] = []

  for (const section of split(body)) {
    const { kept, removed } = withoutQuizFences(section.lines)
    const text = kept.slice(section.heading ? 1 : 0).join('\n')

    // The quiz section is nothing but its fence once the fence is gone.
    if (removed && text.trim() === '') continue
    // The study method is already in the card above; compare the text, not the
    // heading, so a translated lesson needs no heading table.
    if (study && study !== '' && text.trim() === study) continue

    out.push(...kept)
  }
  return out
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}
