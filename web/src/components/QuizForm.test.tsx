import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { QuizState } from '@/lib/actions/quiz'
import { renderWithIntl } from '@/test/render'

import { QuizForm, type RenderedQuestion } from './QuizForm'

const submitQuiz = vi.hoisted(() => vi.fn())

vi.mock('@/lib/actions/quiz', () => ({ submitQuiz }))

const QUESTION: RenderedQuestion = {
  id: 'q1',
  type: 'single',
  prompt: <span>관성 모멘트는?</span>,
  choices: [<span key="a">Ia</span>, <span key="b">Ib</span>],
}

function state(over: Partial<QuizState> = {}): QuizState {
  return {
    run: {
      lesson_id: 'l1',
      correct: 0,
      total: 1,
      percent: 0,
      seconds: 12,
      new_card_ids: [],
      answers: [
        {
          question_id: 'q1',
          given: '1',
          correct: false,
          correct_answer: '2',
          explanation: '관성 모멘트는 $I = mr^2$ 입니다.',
        },
      ],
    },
    ...over,
  }
}

async function submit() {
  await userEvent.click(screen.getByRole('button', { name: '제출' }))
}

describe('QuizForm explanations', () => {
  beforeEach(() => submitQuiz.mockReset())

  it('renders the explanation the action rendered on the server, not its Markdown source', async () => {
    // The Server Action runs the lesson Markdown pipeline and returns a React
    // tree, so KaTeX and emphasis reach the screen instead of raw `$…$`.
    submitQuiz.mockResolvedValue(
      state({
        explanations: {
          q1: (
            <p>
              관성 모멘트는 <span data-testid="katex">I = mr²</span> 입니다.
            </p>
          ),
        },
      }),
    )
    renderWithIntl(<QuizForm moduleId="m1" lessonId="l1" questions={[QUESTION]} />)
    await userEvent.click(screen.getByRole('radio', { name: /Ia/ }))
    await submit()

    await waitFor(() => expect(screen.getByTestId('katex')).toBeInTheDocument())
    expect(screen.queryByText(/\$I = mr\^2\$/)).not.toBeInTheDocument()
  })

  it('falls back to the plain explanation when the action rendered none', async () => {
    submitQuiz.mockResolvedValue(state())
    renderWithIntl(<QuizForm moduleId="m1" lessonId="l1" questions={[QUESTION]} />)
    await userEvent.click(screen.getByRole('radio', { name: /Ia/ }))
    await submit()

    await waitFor(() =>
      expect(screen.getByText('관성 모멘트는 $I = mr^2$ 입니다.')).toBeInTheDocument(),
    )
  })

  it('shows no explanation row when there is nothing to explain', async () => {
    const empty = state()
    empty.run!.answers[0]!.explanation = ''
    submitQuiz.mockResolvedValue({ ...empty, explanations: {} })
    renderWithIntl(<QuizForm moduleId="m1" lessonId="l1" questions={[QUESTION]} />)
    await userEvent.click(screen.getByRole('radio', { name: /Ia/ }))
    await submit()

    await waitFor(() => expect(screen.getByText('오답')).toBeInTheDocument())
    expect(screen.queryByText('해설')).not.toBeInTheDocument()
  })
})
