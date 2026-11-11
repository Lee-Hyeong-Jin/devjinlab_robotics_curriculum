import type { LockState } from '@/lib/api/types'

import { Card } from './Card'
import { ProgressBar } from './ProgressBar'
import { StatusDot } from './StatusDot'

export interface StageProgressModule {
  id?: string
  title?: string
  progress?: number
  state?: LockState
}

export interface StageProgressStage {
  level?: string
  progress?: number
  modules?: StageProgressModule[]
}

export interface StageProgressProps {
  title: string
  stages: StageProgressStage[]
  stateLabel: (state: LockState) => string
  progressLabel: string
}

/** Per-stage progress list for the dashboard (AC-WEB.3). */
export function StageProgress({ title, stages, stateLabel, progressLabel }: StageProgressProps) {
  return (
    <Card as="section" aria-labelledby="stage-progress-heading">
      <h2 id="stage-progress-heading" className="text-primary mb-4 font-semibold">
        {title}
      </h2>
      <ul className="flex flex-col gap-5">
        {stages.map((stage, index) => (
          <li key={stage.level ?? index}>
            <div className="mb-2 flex items-center justify-between gap-3">
              <h3 className="text-primary text-sm font-semibold">{stage.level}</h3>
            </div>
            <ProgressBar
              value={stage.progress}
              label={`${stage.level ?? ''} ${progressLabel}`}
              showValue
            />
            <ul className="mt-3 flex flex-col gap-2">
              {(stage.modules ?? []).map((module, moduleIndex) => (
                <li
                  key={module.id ?? moduleIndex}
                  className="flex flex-wrap items-center gap-x-3 gap-y-1"
                >
                  <StatusDot
                    state={module.state ?? 'available'}
                    label={stateLabel(module.state ?? 'available')}
                    labelHidden
                  />
                  <span className="text-primary min-w-0 flex-1 truncate text-sm">
                    {module.title ?? module.id}
                  </span>
                  <span className="text-muted text-xs">{stateLabel(module.state ?? 'available')}</span>
                  <ProgressBar
                    className="w-28 shrink-0"
                    value={module.progress}
                    label={`${module.title ?? module.id ?? ''} ${progressLabel}`}
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
