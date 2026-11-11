export const meta = {
  name: 'platform-loop',
  description: 'Outer loop node L0: pick the next runnable milestone from harness/roadmap.yaml, run the milestone graph, repeat until none remain, one is blocked, or the cap/budget is hit',
  whenToUse: 'Drive the platform forward across several milestones without human intervention between them. Invoked by /platform-loop.',
  phases: [
    { title: 'Select', detail: 'read roadmap state, choose the next runnable milestone, mark it in_progress' },
    { title: 'Milestone', detail: 'run the milestone sub-workflow (spec -> implement/verify -> review -> acceptance -> integrate)' },
  ],
}

const cfg = Object.assign(
  { maxMilestones: 2, stopOnBlocked: true, milestoneArgs: {} },
  typeof args === 'number' ? { maxMilestones: args } : (args || {}),
)
const SELECT = {
  type: 'object',
  properties: {
    milestone: { type: ['string', 'null'] },
    title: { type: 'string' },
    remaining_todo: { type: 'integer' },
  },
  required: ['milestone', 'remaining_todo'],
}

const results = []
for (let i = 0; i < cfg.maxMilestones; i++) {
  if (budget.total && budget.remaining() < 150000) {
    log(`token budget nearly exhausted (${Math.round(budget.remaining() / 1000)}k left); stopping the outer loop`)
    break
  }
  phase('Select')
  const sel = await agent(
    `당신은 개발 그래프의 N0(select) 노드다.
1. \`python3 -I scripts/harness/roadmap.py next\` 를 실행해 다음 실행 가능한 마일스톤(JSON 또는 null)을 얻는다.
2. null 이 아니면 \`python3 -I scripts/harness/roadmap.py set <id> in_progress\` 로 표시한다.
3. \`python3 -I scripts/harness/roadmap.py summary\` 로 남은 todo 수를 센다.
milestone(id 또는 null), title, remaining_todo 를 반환하라. 다른 파일은 수정하지 말 것.`,
    { schema: SELECT, phase: 'Select', label: `select#${i + 1}`, effort: 'low' },
  )
  if (!sel || !sel.milestone) {
    log('no runnable milestone left (all done, or remaining ones are blocked / have unmet dependencies)')
    break
  }
  log(`milestone ${i + 1}/${cfg.maxMilestones}: ${sel.milestone} ${sel.title || ''}`)

  phase('Milestone')
  let r = null
  try {
    r = await workflow('milestone', Object.assign({}, cfg.milestoneArgs, { milestone: sel.milestone }))
  } catch (e) {
    r = { milestone: sel.milestone, status: 'error', error: String(e && e.message ? e.message : e) }
    log(`milestone ${sel.milestone} threw: ${r.error}`)
  }
  results.push(r)
  if (r && r.status !== 'done' && cfg.stopOnBlocked) {
    log(`milestone ${sel.milestone} ended as "${r.status}"; stopping for human review (see reports/milestones/)`)
    break
  }
}
return { ran: results.length, results }
