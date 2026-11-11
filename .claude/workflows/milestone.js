export const meta = {
  name: 'milestone',
  description: 'Drive one roadmap milestone through the dev graph: spec -> decompose -> implement/verify loop -> review loop -> acceptance gate -> integrate',
  whenToUse: 'Run a single milestone id from harness/roadmap.yaml to completion. Invoked by /milestone or by platform-loop.',
  phases: [
    { title: 'Spec', detail: 'planner writes docs/specs/<id>.md with acceptance criteria' },
    { title: 'Decompose', detail: 'planner splits the spec into tasks' },
    { title: 'Implement', detail: 'loop node L1: implement -> verify until green (max N)' },
    { title: 'Review', detail: 'loop node L2: review -> adversarial verify -> fix (max N)' },
    { title: 'Acceptance', detail: 'gate: acceptance criteria checked against the real tree' },
    { title: 'Integrate', detail: 'commit, update roadmap status, write report' },
  ],
}

// ---------- args ----------
const cfg = Object.assign(
  { milestone: null, maxFixIters: 3, maxReviewRounds: 2, maxAcceptanceRounds: 2, parallelTasks: false },
  typeof args === 'string' ? { milestone: args } : (args || {}),
)
if (!cfg.milestone) throw new Error('milestone workflow needs args.milestone (an id from harness/roadmap.yaml)')
const M = cfg.milestone

// ---------- schemas ----------
const SPEC = {
  type: 'object',
  properties: {
    spec_path: { type: 'string' },
    acceptance_criteria: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['spec_path', 'acceptance_criteria', 'summary'],
}
const TASKS = {
  type: 'object',
  properties: {
    tasks: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          title: { type: 'string' },
          description: { type: 'string' },
          files: { type: 'array', items: { type: 'string' } },
          independent: { type: 'boolean' },
        },
        required: ['id', 'title', 'description'],
      },
    },
  },
  required: ['tasks'],
}
const IMPL = {
  type: 'object',
  properties: {
    done: { type: 'boolean' },
    summary: { type: 'string' },
    files_changed: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['done', 'summary'],
}
const VERIFY = {
  type: 'object',
  properties: {
    ok: { type: 'boolean' },
    summary: { type: 'string' },
    failures: { type: 'array', items: { type: 'string' } },
  },
  required: ['ok', 'summary', 'failures'],
}
const REVIEW = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          line: { type: 'integer' },
          summary: { type: 'string' },
          severity: { type: 'string', enum: ['blocking', 'minor'] },
          failure_scenario: { type: 'string' },
        },
        required: ['file', 'summary', 'severity'],
      },
    },
  },
  required: ['findings'],
}
const VERDICT = {
  type: 'object',
  properties: { refuted: { type: 'boolean' }, reason: { type: 'string' } },
  required: ['refuted', 'reason'],
}
const ACCEPT = {
  type: 'object',
  properties: {
    passed: { type: 'boolean' },
    unmet: { type: 'array', items: { type: 'string' } },
    feedback: { type: 'string' },
  },
  required: ['passed', 'unmet', 'feedback'],
}
const INTEGRATE = {
  type: 'object',
  properties: { commit: { type: 'string' }, report_path: { type: 'string' }, status: { type: 'string' } },
  required: ['commit', 'report_path', 'status'],
}

const list = (xs) => (xs && xs.length ? xs.map((x) => `- ${x}`).join('\n') : '- (none)')

// ---------- N1 spec ----------
phase('Spec')
const spec = await agent(
  `당신은 개발 그래프의 N1(spec) 노드다. 마일스톤 "${M}" 의 명세를 작성하라.
1. \`python3 -I scripts/harness/roadmap.py get ${M}\` 로 goal/acceptance 를 읽는다.
2. research_notes/ 와 docs/adr/ 에 관련 자료가 있으면 읽고 반영한다.
3. docs/specs/${M}.md 를 작성한다: 배경, 범위(in/out), 설계 요점, 검증 가능한 수용조건(acceptance_criteria) 목록, 리스크.
   roadmap 의 acceptance 를 그대로 쓰되 모호한 항목은 검증 가능하게 구체화한다.
구조화된 결과로 spec_path, acceptance_criteria, summary 를 반환하라.`,
  { agentType: 'planner', schema: SPEC, phase: 'Spec', label: `spec:${M}` },
)
if (!spec) throw new Error('spec node returned nothing')
log(`spec: ${spec.spec_path} (${spec.acceptance_criteria.length} criteria)`)

let acceptance = null
let blockedTasks = []
let feedbackForDecompose = ''

// ---------- L3: acceptance retry loop ----------
for (let round = 1; round <= cfg.maxAcceptanceRounds; round++) {
  // ---------- N2 decompose ----------
  phase('Decompose')
  const plan = await agent(
    `당신은 개발 그래프의 N2(decompose) 노드다. ${spec.spec_path} 를 읽고 마일스톤 "${M}" 을 구현 태스크로 분해하라.
${feedbackForDecompose ? `이전 수용 게이트에서 미충족된 항목이 있다. 이를 해결하는 태스크만 만들어라:\n${feedbackForDecompose}\n` : ''}
규칙: 각 태스크는 한 에이전트가 한 번에 끝낼 수 있는 크기(파일 1~5개). 테스트 작성을 태스크 설명에 포함. 태스크 간 파일이 겹치지 않으면 independent=true.
순서는 의존 순서대로. 결과를 구조화해서 반환하라(코드는 수정하지 말 것).`,
    { agentType: 'planner', schema: TASKS, phase: 'Decompose', label: `decompose:${M}#${round}` },
  )
  const tasks = plan && plan.tasks ? plan.tasks : []
  if (!tasks.length) { log('decompose produced no tasks'); break }
  log(`round ${round}: ${tasks.length} task(s)`)

  // ---------- L1: implement -> verify loop, per task ----------
  phase('Implement')
  const allIndependent = tasks.every((t) => t.independent)
  const runTask = async (t) => {
    let feedback = ''
    let verdict = null
    for (let iter = 1; iter <= cfg.maxFixIters; iter++) {
      const impl = await agent(
        `당신은 개발 그래프의 N3(implement) 노드다. 마일스톤 "${M}" 의 태스크를 구현하라.
명세: ${spec.spec_path}
태스크 ${t.id}: ${t.title}
${t.description}
${t.files && t.files.length ? `대상 파일(참고): ${t.files.join(', ')}` : ''}
${feedback ? `\n이전 반복의 검증 실패 피드백(반드시 해결):\n${feedback}` : ''}
규칙: 테스트를 함께 작성한다. 끝나기 전에 \`bash scripts/harness/check.sh\` 를 직접 실행해 통과시킨다. 커밋은 하지 않는다.
구조화된 결과(done, summary, files_changed, notes)를 반환하라.`,
        { agentType: 'implementer', schema: IMPL, phase: 'Implement', label: `impl:${t.id}#${iter}` },
      )
      verdict = await agent(
        `당신은 개발 그래프의 N4(verify) 게이트다. 태스크 ${t.id} (${t.title}) 의 구현을 검증하라.
구현자 보고: ${impl ? impl.summary : '(없음)'}
1. \`bash scripts/harness/check.sh\` 를 실행한다(전체 모드).
2. 태스크 설명의 요구가 실제로 코드에 반영되었는지 변경 파일을 읽어 확인한다.
3. 요구에 대응하는 테스트가 존재하고 통과하는지 확인한다.
ok 는 세 가지가 모두 만족될 때만 true. failures 에는 구현자가 바로 고칠 수 있게 구체적으로(파일, 명령 출력 요약) 적는다. 코드는 수정하지 말 것.`,
        { agentType: 'verifier', schema: VERIFY, phase: 'Implement', label: `verify:${t.id}#${iter}` },
      )
      if (verdict && verdict.ok) { log(`${t.id}: verified on iteration ${iter}`); return { task: t, ok: true, iters: iter } }
      feedback = verdict ? list(verdict.failures) : 'verifier returned nothing'
      log(`${t.id}: verify failed (iteration ${iter}/${cfg.maxFixIters})`)
    }
    return { task: t, ok: false, iters: cfg.maxFixIters, failures: verdict ? verdict.failures : [] }
  }
  let results
  if (cfg.parallelTasks && allIndependent) {
    results = (await parallel(tasks.map((t) => () => runTask(t)))).filter(Boolean)
  } else {
    results = []
    for (const t of tasks) results.push(await runTask(t)) // sequential: tasks share one working tree
  }
  blockedTasks = results.filter((r) => !r.ok)
  if (blockedTasks.length) log(`blocked tasks after L1: ${blockedTasks.map((r) => r.task.id).join(', ')}`)

  // ---------- L2: review -> adversarial verify -> fix loop ----------
  phase('Review')
  for (let rr = 1; rr <= cfg.maxReviewRounds; rr++) {
    const review = await agent(
      `당신은 개발 그래프의 N5(review) 노드다. 마일스톤 "${M}" 의 작업 트리 변경(\`git status\`, \`git diff\`, 추적되지 않은 새 파일 포함)을 리뷰하라.
명세: ${spec.spec_path}
정확성 버그, 명세 위반, 누락된 테스트, 보안 문제를 찾아라. 스타일만의 문제는 minor. 각 finding 에 실패 시나리오를 적어라. 코드는 수정하지 말 것.`,
      { agentType: 'reviewer', schema: REVIEW, phase: 'Review', label: `review:${M}#${rr}` },
    )
    const blocking = review && review.findings ? review.findings.filter((f) => f.severity === 'blocking') : []
    if (!blocking.length) { log(`review round ${rr}: no blocking findings`); break }
    // N6: two independent skeptics per finding; a finding survives unless both refute it
    const judged = await parallel(
      blocking.map((f) => () =>
        parallel([0, 1].map((k) => () =>
          agent(
            `당신은 개발 그래프의 N6(adversarial verify) 게이트, 회의론자 #${k + 1}이다. 다음 리뷰 finding 을 반박하라.
파일: ${f.file}${f.line ? ':' + f.line : ''}
주장: ${f.summary}
실패 시나리오: ${f.failure_scenario || '(없음)'}
코드를 직접 읽고, 가능하면 재현(테스트/스크립트 실행)해 보라. 실제 결함이 아니거나 재현되지 않으면 refuted=true. 확신이 없으면 refuted=true.`,
            { agentType: 'reviewer', schema: VERDICT, phase: 'Review', label: `skeptic${k + 1}:${f.file}` },
          ),
        )).then((vs) => ({ f, real: vs.filter(Boolean).filter((v) => !v.refuted).length >= 1 })),
      ),
    )
    const confirmed = judged.filter(Boolean).filter((j) => j.real).map((j) => j.f)
    log(`review round ${rr}: ${blocking.length} blocking, ${confirmed.length} confirmed`)
    if (!confirmed.length) break
    // N7 fix
    await agent(
      `당신은 개발 그래프의 N7(fix) 노드다. 확정된 리뷰 findings 를 모두 고쳐라. 각 수정에 회귀 테스트를 추가하고 \`bash scripts/harness/check.sh\` 를 통과시킨다. 커밋은 하지 않는다.
${confirmed.map((f) => `- ${f.file}${f.line ? ':' + f.line : ''}: ${f.summary}`).join('\n')}`,
      { agentType: 'implementer', schema: IMPL, phase: 'Review', label: `fix:${M}#${rr}` },
    )
  }

  // ---------- N8 acceptance gate ----------
  phase('Acceptance')
  acceptance = await agent(
    `당신은 개발 그래프의 N8(acceptance) 게이트다. 마일스톤 "${M}" 의 수용조건을 실제 작업 트리에 대해 하나씩 검사하라.
명세: ${spec.spec_path}
수용조건:
${list(spec.acceptance_criteria)}
${blockedTasks.length ? `\n주의: 다음 태스크는 검증에 실패한 채 남아 있다: ${blockedTasks.map((r) => r.task.id).join(', ')}` : ''}
각 조건에 대해 명령 실행/파일 확인 등 근거를 수집한다. 하나라도 미충족이면 passed=false, unmet 에 조건과 근거를 적고 feedback 에 다음 분해 라운드를 위한 구체적 지시를 적어라. 코드는 수정하지 말 것.`,
    { agentType: 'acceptance-tester', schema: ACCEPT, phase: 'Acceptance', label: `accept:${M}#${round}` },
  )
  if (acceptance && acceptance.passed) { log(`acceptance passed (round ${round})`); break }
  feedbackForDecompose = acceptance ? `${list(acceptance.unmet)}\n\n${acceptance.feedback}` : 'acceptance gate returned nothing'
  log(`acceptance unmet (round ${round}/${cfg.maxAcceptanceRounds}): ${acceptance ? acceptance.unmet.length : '?'} item(s)`)
}

// ---------- N9 integrate ----------
phase('Integrate')
const finalStatus = acceptance && acceptance.passed && !blockedTasks.length ? 'done' : 'blocked'
const integ = await agent(
  `당신은 개발 그래프의 N9(integrate) 노드다. 마일스톤 "${M}" 을 마무리하라. 최종 상태: ${finalStatus}.
1. \`bash scripts/harness/check.sh --quick\` 가 통과하는지 확인한다(실패하면 커밋하되 보고서에 기록).
2. 작업 트리의 변경을 현재 브랜치에 커밋한다(메시지: "feat(${M}): <요약>"; CLAUDE.md 의 커밋 규칙을 따른다). 변경이 없으면 커밋하지 않는다.
3. reports/milestones/${M}.md 를 작성한다: 무엇을 했는지, 수용조건별 결과, 미해결 항목, 다음 단계.
   ${blockedTasks.length ? `blocked 태스크: ${blockedTasks.map((r) => `${r.task.id} (${(r.failures || []).join('; ')})`).join(', ')}` : ''}
   ${acceptance && !acceptance.passed ? `미충족 수용조건:\n${list(acceptance.unmet)}` : ''}
4. \`python3 -I scripts/harness/roadmap.py set ${M} ${finalStatus} "<한 줄 메모>"\` 로 로드맵 상태를 갱신하고 그 변경도 커밋한다.
commit(해시 또는 'none'), report_path, status 를 반환하라.`,
  { agentType: 'integrator', schema: INTEGRATE, phase: 'Integrate', label: `integrate:${M}` },
)

return {
  milestone: M,
  status: finalStatus,
  spec: spec.spec_path,
  commit: integ ? integ.commit : null,
  report: integ ? integ.report_path : null,
  blocked_tasks: blockedTasks.map((r) => r.task.id),
  unmet: acceptance ? acceptance.unmet : [],
}
