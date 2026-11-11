export const meta = {
  name: 'review-loop',
  description: 'Standalone loop node L2: review the working-tree diff, adversarially verify each blocking finding with two skeptics, fix the confirmed ones, repeat until clean or max rounds',
  whenToUse: 'Code changes are ready and should be reviewed and hardened before commit. Invoked by /review-loop.',
  phases: [
    { title: 'Review', detail: 'reviewer lists findings with severity and failure scenarios' },
    { title: 'Verify', detail: 'two skeptics try to refute each blocking finding' },
    { title: 'Fix', detail: 'implementer fixes confirmed findings and adds regression tests' },
  ],
}

const cfg = Object.assign({ maxRounds: 2, target: 'the current working tree (git status, git diff, plus untracked files)' },
  typeof args === 'string' ? { target: args } : (args || {}))
const REVIEW = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' }, line: { type: 'integer' }, summary: { type: 'string' },
          severity: { type: 'string', enum: ['blocking', 'minor'] }, failure_scenario: { type: 'string' },
        },
        required: ['file', 'summary', 'severity'],
      },
    },
  },
  required: ['findings'],
}
const VERDICT = { type: 'object', properties: { refuted: { type: 'boolean' }, reason: { type: 'string' } }, required: ['refuted', 'reason'] }
const IMPL = { type: 'object', properties: { done: { type: 'boolean' }, summary: { type: 'string' } }, required: ['done', 'summary'] }

const history = []
for (let round = 1; round <= cfg.maxRounds; round++) {
  phase('Review')
  const review = await agent(
    `당신은 개발 그래프의 N5(review) 노드다. 리뷰 대상: ${cfg.target}.
정확성 버그, 명세 위반, 누락된 테스트, 보안 문제를 찾아라. 스타일만의 문제는 minor. 각 finding 에 구체적인 실패 시나리오(입력/상태 → 잘못된 출력)를 적어라. 코드는 수정하지 말 것.`,
    { agentType: 'reviewer', schema: REVIEW, phase: 'Review', label: `review#${round}` },
  )
  const blocking = review && review.findings ? review.findings.filter((f) => f.severity === 'blocking') : []
  const minor = review && review.findings ? review.findings.filter((f) => f.severity !== 'blocking') : []
  if (!blocking.length) { history.push({ round, blocking: 0, confirmed: 0, minor }); log(`round ${round}: clean (minor: ${minor.length})`); break }

  phase('Verify')
  const judged = await parallel(
    blocking.map((f) => () =>
      parallel([0, 1].map((k) => () =>
        agent(
          `당신은 N6(adversarial verify) 게이트의 회의론자 #${k + 1}이다. 다음 finding 을 반박하라.
파일: ${f.file}${f.line ? ':' + f.line : ''}
주장: ${f.summary}
실패 시나리오: ${f.failure_scenario || '(없음)'}
코드를 직접 읽고, 가능하면 재현해 보라. 실제 결함이 아니거나 재현되지 않으면 refuted=true. 확신이 없으면 refuted=true.`,
          { agentType: 'reviewer', schema: VERDICT, phase: 'Verify', label: `skeptic${k + 1}:${f.file}` },
        ),
      )).then((vs) => ({ f, real: vs.filter(Boolean).filter((v) => !v.refuted).length >= 1 })),
    ),
  )
  const confirmed = judged.filter(Boolean).filter((j) => j.real).map((j) => j.f)
  history.push({ round, blocking: blocking.length, confirmed: confirmed.length, minor })
  log(`round ${round}: ${blocking.length} blocking, ${confirmed.length} confirmed`)
  if (!confirmed.length) break

  phase('Fix')
  await agent(
    `당신은 N7(fix) 노드다. 확정된 findings 를 모두 고치고 각각 회귀 테스트를 추가하라. \`bash scripts/harness/check.sh\` 를 통과시킨다. 커밋은 하지 않는다.
${confirmed.map((f) => `- ${f.file}${f.line ? ':' + f.line : ''}: ${f.summary}`).join('\n')}`,
    { agentType: 'implementer', schema: IMPL, phase: 'Fix', label: `fix#${round}` },
  )
}
const last = history[history.length - 1]
return { clean: !!last && last.confirmed === 0, rounds: history, minor_findings: last ? last.minor : [] }
