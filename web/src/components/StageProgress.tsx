import type { RoadmapStageView } from '@/lib/roadmap'
import type { LockState } from '@/lib/progress'

import { Card } from './Card'
import { ProgressBar } from './ProgressBar'
import { StatusDot } from './StatusDot'

export interface StageProgressProps {
  title: string
  stages: readonly RoadmapStageView[]
  stateLabel: (state: LockState) => string
  progressLabel: string
  lessonsLabel: (done: number, total: number) => string
}

/** Per-stage, per-module progress list for the dashboard (AC-WEB.3). */
export function StageProgress({
  title,
  stages,
  stateLabel,
  progressLabel,
  lessonsLabel,
}: StageProgressProps) {
  return (
    <Card as="section" aria-labelledby="stage-progress-heading">
      <h2 id="stage-progress-heading" className="text-primary mb-4 font-semibold">
        {title}
      </h2>
      <ul className="flex flex-col gap-5">
        {stages.map((stage) => (
          <li key={stage.level}>
            <div className="mb-2 flex flex-wrap items-center justify-between gap-3">
              <h3 className="text-primary text-sm font-semibold">{stage.level}</h3>
              <span className="text-muted text-xs">
                {lessonsLabel(stage.lessonsDone, stage.lessonsTotal)}
              </span>
            </div>
            <ProgressBar
              value={stage.progress}
              label={`${stage.level} ${progressLabel}`}
              showValue
            />
            <ul className="mt-3 flex flex-col gap-2">
              {stage.modules.map((module) => (
                <li key={module.id} className="flex flex-wrap items-center gap-x-3 gap-y-1">
                  <StatusDot state={module.state} label={stateLabel(module.state)} labelHidden />
                  <span className="text-primary min-w-0 flex-1 truncate text-sm">
                    {module.title}
                  </span>
                  <span className="text-muted text-xs">{stateLabel(module.state)}</span>
                  <ProgressBar
                    className="w-28 shrink-0"
                    value={module.progress}
                    label={`${module.title} ${progressLabel}`}
                    showValue
                  />
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </Card>
  )
}
