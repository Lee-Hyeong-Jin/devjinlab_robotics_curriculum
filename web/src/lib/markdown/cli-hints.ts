/**
 * Lesson bodies and reports are written once and read in three places: the terminal, the
 * static site and this app. They tell the reader to run `rc quiz <lesson>`, `rc start <lesson>`
 * or `rc review` — the right advice in a terminal and a dead end on a web page that has those
 * screens one click away (QA B-19, B-23). Here the commands become links to the screens; the
 * command stays beside the link, because it still works.
 */

export interface CliHintLabels {
  /** Link text for a lesson's quiz. */
  quiz: string
  /** Link text for opening a lesson. */
  start: string
  /** Link text for the review screen. */
  review: string
  /** `(CLI: …)`-style prefix placed before the command that is kept. */
  cli: string
}

export interface CliHintOptions {
  labels: CliHintLabels
  /** Where a lesson's quiz lives, or `null` when the lesson is unknown. */
  quizHref: (lessonId: string) => string | null
  /** Where a lesson lives, or `null` when the lesson is unknown. */
  lessonHref: (lessonId: string) => string | null
}

const LESSON_ID = '[a-z0-9][a-z0-9-]*'
// `rc quiz m1-vectors` in backticks; flags after the id (`--lang en`) are left in the command.
const COMMAND = new RegExp('`rc (quiz|start) (' + LESSON_ID + ')((?: --?[a-z][^`]*)?)`', 'g')
const REVIEW = /`rc review`/g
const FENCE = /^(```|~~~)/

/** Replace CLI commands in running text with links to the matching screens. */
export function linkCliHints(markdown: string, options: CliHintOptions): string {
  const { labels } = options
  let fenced = false
  return markdown
    .split('\n')
    .map((line) => {
      // A code block shows a terminal session: leave it exactly as written.
      if (FENCE.test(line.trimStart())) {
        fenced = !fenced
        return line
      }
      if (fenced) return line
      return line
        .replace(COMMAND, (whole: string, verb: string, lessonId: string) => {
          const href = verb === 'quiz' ? options.quizHref(lessonId) : options.lessonHref(lessonId)
          if (!href) return whole
          const label = verb === 'quiz' ? labels.quiz : labels.start
          return `[${label}](${href}) (${labels.cli} ${whole})`
        })
        .replace(REVIEW, (whole: string) => `[${labels.review}](/review) (${labels.cli} ${whole})`)
    })
    .join('\n')
}
