export const meta = {
  name: 'verify-fix',
  description: 'Standalone loop node L1: run the verification gate (scripts/harness/check.sh), fix failures, repeat until green or max iterations',
  whenToUse: 'The working tree has code changes and check.sh is red (or you want it proven green). Invoked by /verify-fix.',
  phases: [
    { title: 'Verify', detail: 'verifier runs check.sh and reports structured failures' },
    { title: 'Fix', detail: 'implementer fixes exactly the reported failures' },
  ],
}

const cfg = Object.assign({ maxIters: 3, scope: '' }, typeof args === 'string' ? { scope: args } : (args || {}))
const VERIFY = {
  type: 'object',
  properties: {
    ok: { type: 'boolean' },
    summary: { type: 'string' },
    failures: { type: 'array', items: { type: 'string' } },
  },
  required: ['ok', 'summary', 'failures'],
}
const IMPL = {
  type: 'object',
  properties: { done: { type: 'boolean' }, summary: { type: 'string' }, files_changed: { type: 'array', items: { type: 'string' } } },
  required: ['done', 'summary'],
}

let verdict = null
for (let iter = 1; iter <= cfg.maxIters; iter++) {
  phase('Verify')
  verdict = await agent(
    `당신은 개발 그래프의 N4(verify) 게이트다. \`bash scripts/harness/check.sh\` 를 실행하고 결과를 구조화해 보고하라.
${cfg.scope ? `추가로 확인할 범위: ${cfg.scope}` : ''}
failures 에는 구현자가 바로 고칠 수 있도록 파일/테스트 이름/오류 메시지 요약을 적는다. 코드는 수정하지 말 것.`,
    { agentType: 'verifier', schema: VERIFY, phase: 'Verify', label: `verify#${iter}` },
  )
  if (verdict && verdict.ok) { log(`green on iteration ${iter}`); break }
  if (iter === cfg.maxIters) { log(`still failing after ${cfg.maxIters} iterations; handing back to the human`); break }
  phase('Fix')
  await agent(
    `당신은 개발 그래프의 N7(fix) 노드다. 다음 검증 실패를 고쳐라. 원인을 찾아 고치고, 테스트를 약화시키거나 건너뛰는 방식은 금지한다. 끝나기 전에 \`bash scripts/harness/check.sh\` 를 직접 실행해 확인한다. 커밋은 하지 않는다.
${(verdict ? verdict.failures : ['verifier returned nothing']).map((f) => `- ${f}`).join('\n')}`,
    { agentType: 'implementer', schema: IMPL, phase: 'Fix', label: `fix#${iter}` },
  )
}
return { ok: !!(verdict && verdict.ok), summary: verdict ? verdict.summary : null, failures: verdict ? verdict.failures : [] }
