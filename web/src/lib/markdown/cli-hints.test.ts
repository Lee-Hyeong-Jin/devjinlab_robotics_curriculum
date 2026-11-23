import { describe, expect, it } from 'vitest'

import { linkCliHints, type CliHintOptions } from './cli-hints'

const options: CliHintOptions = {
  labels: { quiz: '이 레슨의 퀴즈', start: '레슨 열기', review: '복습 화면', cli: 'CLI:' },
  quizHref: (id) => (id === 'm1-vectors' ? '/modules/m1/m1-vectors/quiz' : null),
  lessonHref: (id) => (id.startsWith('m1-') ? `/lessons/${id}` : null),
}

describe('linkCliHints', () => {
  it('links a quiz command to the web quiz and keeps the command', () => {
    expect(linkCliHints('`rc quiz m1-vectors` 로 풀 수 있다.', options)).toBe(
      '[이 레슨의 퀴즈](/modules/m1/m1-vectors/quiz) (CLI: `rc quiz m1-vectors`) 로 풀 수 있다.',
    )
    expect(linkCliHints('Run `rc quiz m1-vectors --lang en`.', options)).toContain(
      '](/modules/m1/m1-vectors/quiz) (CLI: `rc quiz m1-vectors --lang en`)',
    )
  })

  it('links start and review commands', () => {
    expect(linkCliHints('시작: `rc start m1-rotation`', options)).toBe(
      '시작: [레슨 열기](/lessons/m1-rotation) (CLI: `rc start m1-rotation`)',
    )
    expect(linkCliHints('새 카드 3장 → `rc review` 로 복습', options)).toBe(
      '새 카드 3장 → [복습 화면](/review) (CLI: `rc review`) 로 복습',
    )
  })

  it('leaves unknown lessons, placeholders and code blocks alone', () => {
    expect(linkCliHints('`rc quiz zz-unknown`', options)).toBe('`rc quiz zz-unknown`')
    expect(linkCliHints('`rc start <레슨>` 으로 시작하세요.', options)).toBe(
      '`rc start <레슨>` 으로 시작하세요.',
    )
    const block = '```bash\nrc quiz m1-vectors\n`rc quiz m1-vectors`\n```'
    expect(linkCliHints(block, options)).toBe(block)
    expect(linkCliHints('rc quiz m1-vectors', options)).toBe('rc quiz m1-vectors')
  })
})
