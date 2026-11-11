import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import type { ResourceRef } from '@/lib/api/types'
import { resource } from '@/test/factories'
import { renderWithIntl } from '@/test/render'

import { Chip } from './Chip'
import { DataTable, type Column } from './DataTable'
import { EmptyState } from './EmptyState'
import { LessonRow } from './LessonRow'
import { ModuleCard } from './ModuleCard'
import { ProgressBar } from './ProgressBar'
import { ResourceExplorer } from './ResourceExplorer'
import { ResourceRow } from './ResourceRow'
import { StageProgress } from './StageProgress'
import { StatTile } from './StatTile'
import { StatusDot } from './StatusDot'
import { StudyStep } from './StudyStep'

describe('StatusDot', () => {
  it('always carries a text label, never colour alone (AC-A11Y.2)', () => {
    render(<StatusDot state="done" label="완료" />)
    expect(screen.getByText('완료')).toBeInTheDocument()
  })

  it('adds a lock glyph for the locked state', () => {
    render(<StatusDot state="locked" label="잠김" />)
    expect(screen.getByText('🔒 잠김')).toBeInTheDocument()
  })

  it('keeps the label available to assistive tech when visually hidden', () => {
    const { container } = render(<StatusDot state="in_progress" label="진행 중" labelHidden />)
    expect(container.querySelector('.sr-only')?.textContent).toBe('진행 중')
  })
})

describe('ProgressBar', () => {
  it('exposes the value through the progressbar role (AC-A11Y.3)', () => {
    render(<ProgressBar value={0.42} label="코스 진행률" showValue />)
    const bar = screen.getByRole('progressbar', { name: '코스 진행률' })
    expect(bar).toHaveAttribute('aria-valuenow', '42')
    expect(bar).toHaveAttribute('aria-valuemin', '0')
    expect(bar).toHaveAttribute('aria-valuemax', '100')
    expect(screen.getByText('42%')).toBeInTheDocument()
  })

  it('reports 0 for a missing value instead of NaN', () => {
    render(<ProgressBar value={undefined} label="진행률" />)
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '0')
  })
})

describe('Chip', () => {
  it('renders its tone as a class, not as the only signal', () => {
    render(<Chip tone="warning">진행 중</Chip>)
    expect(screen.getByText('진행 중')).toBeInTheDocument()
  })
})

describe('ModuleCard', () => {
  const base = {
    id: 'm1-math-physics',
    title: '수학·물리 기초',
    progress: 0.5,
    lessonsTotal: 4,
    lessonsDone: 2,
    level: '기초',
    stateLabel: '진행 중',
    lessonsLabel: '레슨 4개',
    progressLabel: '진행률',
  }

  it('links to the module when it is not locked', () => {
    render(<ModuleCard {...base} state="in_progress" />)
    expect(screen.getByRole('link')).toHaveAttribute('href', '/modules/m1-math-physics')
  })

  it('does not link a locked module (AC-WEB.3)', () => {
    render(<ModuleCard {...base} state="locked" stateLabel="잠김" />)
    expect(screen.queryByRole('link')).toBeNull()
    expect(screen.getByText('🔒 잠김')).toBeInTheDocument()
  })
})

describe('LessonRow', () => {
  it('links an available lesson and marks the current one', () => {
    render(
      <ul>
        <LessonRow
          moduleId="m1-math-physics"
          lessonId="vectors-matrices"
          title="벡터와 행렬"
          state="in_progress"
          stateLabel="진행 중"
          current
        />
      </ul>,
    )
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/modules/m1-math-physics/vectors-matrices')
    expect(link).toHaveAttribute('aria-current', 'page')
  })

  it('does not link a locked lesson', () => {
    render(
      <ul>
        <LessonRow
          moduleId="m1-math-physics"
          lessonId="locked-lesson"
          title="잠긴 레슨"
          state="locked"
          stateLabel="잠김"
        />
      </ul>,
    )
    expect(screen.queryByRole('link')).toBeNull()
  })
})

describe('StudyStep', () => {
  it('renders the step number and action', () => {
    render(
      <ul>
        <StudyStep n={2} action="직접 풀어 보기">
          연습문제 3개
        </StudyStep>
      </ul>,
    )
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('직접 풀어 보기')).toBeInTheDocument()
    expect(screen.getByText('연습문제 3개')).toBeInTheDocument()
  })
})

describe('ResourceRow', () => {
  it('shows title, kind, scope note and an external link (AC-WEB.2)', () => {
    render(
      <ul>
        <ResourceRow
          title="Modern Robotics"
          url="https://example.com/mr"
          kind="book"
          kindLabel="도서"
          note="3장만"
          externalLabel="새 탭에서 열기"
        />
      </ul>,
    )
    const link = screen.getByRole('link', { name: /Modern Robotics/ })
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    expect(screen.getByText('도서')).toBeInTheDocument()
    expect(screen.getByText('3장만')).toBeInTheDocument()
    expect(screen.getByText('example.com')).toBeInTheDocument()
  })

  it('renders a resource without a URL as plain text', () => {
    render(
      <ul>
        <ResourceRow title="사내 자료" externalLabel="새 탭" />
      </ul>,
    )
    expect(screen.queryByRole('link')).toBeNull()
    expect(screen.getByText('사내 자료')).toBeInTheDocument()
  })
})

describe('StatTile', () => {
  it('shows a skeleton while the backend does not expose the field yet', () => {
    render(<StatTile label="연속 학습일" value="0일" pending pendingLabel="아직 제공되지 않음" />)
    expect(screen.getByTestId('stat-skeleton')).toBeInTheDocument()
    expect(screen.getByText('아직 제공되지 않음')).toBeInTheDocument()
    expect(screen.queryByText('0일')).toBeNull()
  })

  it('shows the value once it is available', () => {
    render(<StatTile label="연속 학습일" value="7일" />)
    expect(screen.getByText('7일')).toBeInTheDocument()
  })
})

describe('DataTable', () => {
  interface Row {
    id: string
    name: string
  }
  const columns: ReadonlyArray<Column<Row>> = [
    { key: 'name', header: '이름', cell: (row) => row.name },
  ]

  it('has a caption and scoped column headers (WCAG 2.1 AA)', () => {
    render(
      <DataTable
        caption="모듈 목록"
        captionVisible
        columns={columns}
        rows={[{ id: 'a', name: '모듈 A' }]}
        rowKey={(row) => row.id}
      />,
    )
    expect(screen.getByRole('table', { name: '모듈 목록' })).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: '이름' })).toHaveAttribute('scope', 'col')
  })

  it('renders the empty slot instead of an empty table body', () => {
    render(
      <DataTable
        caption="모듈 목록"
        columns={columns}
        rows={[]}
        rowKey={(row) => row.id}
        empty={<EmptyState title="없음" />}
      />,
    )
    expect(screen.queryByRole('table')).toBeNull()
    expect(screen.getByText('없음')).toBeInTheDocument()
  })
})

describe('StageProgress', () => {
  it('lists every stage and module with its state (AC-WEB.3)', () => {
    render(
      <StageProgress
        title="단계별 진행률"
        progressLabel="진행률"
        stateLabel={(state) => state}
        lessonsLabel={(done, total) => `${done}/${total}`}
        stages={[
          {
            level: '기초',
            progress: 0.5,
            lessonsDone: 1,
            lessonsTotal: 2,
            modules: [
              { id: 'm1', title: '모듈 1', progress: 1, state: 'done', lessons: [] },
              { id: 'm2', title: '모듈 2', progress: 0, state: 'locked', lessons: [] },
            ],
          },
        ]}
      />,
    )
    expect(screen.getByRole('heading', { name: '기초' })).toBeInTheDocument()
    expect(screen.getByText('모듈 1')).toBeInTheDocument()
    expect(screen.getByText('모듈 2')).toBeInTheDocument()
    expect(screen.getAllByRole('progressbar').length).toBe(3)
  })
})

describe('ResourceExplorer', () => {
  const resources: ResourceRef[] = [
    resource({
      title: 'Modern Robotics',
      url: 'https://example.com/mr',
      kind: 'book',
      note: '3장',
    }),
    resource({ title: 'ROS 2 Tutorials', url: 'https://example.com/ros', kind: 'course' }),
    resource({
      title: 'SLAM 강의',
      url: 'https://example.com/slam',
      kind: 'video',
      lesson_ids: ['l1'],
    }),
  ]

  it('lists every resource with an external link (AC-WEB.5)', () => {
    renderWithIntl(<ResourceExplorer resources={resources} />)
    expect(screen.getByText('자료 3개')).toBeInTheDocument()
    const link = screen.getByRole('link', { name: /Modern Robotics/ })
    expect(link).toHaveAttribute('target', '_blank')
  })

  it('filters by kind', async () => {
    const user = userEvent.setup()
    renderWithIntl(<ResourceExplorer resources={resources} />)
    await user.click(screen.getByRole('radio', { name: /영상/ }))
    expect(screen.getByText('자료 1개')).toBeInTheDocument()
    expect(screen.queryByText('Modern Robotics')).toBeNull()
    expect(screen.getByText('SLAM 강의')).toBeInTheDocument()
  })

  it('searches title and scope note', async () => {
    const user = userEvent.setup()
    renderWithIntl(<ResourceExplorer resources={resources} />)
    await user.type(screen.getByLabelText('자료 검색'), 'ros')
    expect(screen.getByText('자료 1개')).toBeInTheDocument()
    expect(screen.getByText('ROS 2 Tutorials')).toBeInTheDocument()
  })

  it('shows an empty state when nothing matches', async () => {
    const user = userEvent.setup()
    renderWithIntl(<ResourceExplorer resources={resources} />)
    await user.type(screen.getByLabelText('자료 검색'), 'zzzz')
    expect(screen.getByText('조건에 맞는 자료가 없습니다.')).toBeInTheDocument()
  })
})
