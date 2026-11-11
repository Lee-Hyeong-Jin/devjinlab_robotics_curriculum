# Restore drills

Each row is one run of `bash scripts/ops/restore_drill.sh`: back up, destroy the data, restore,
then check `/readyz` and that the recorded progress survived. The release checklist
(docs/architecture/operations.md §5) asks for one drill per release.

| Started (UTC) | Finished (UTC) | Dump | Done lessons before / after | Result |
|---|---|---|---|---|
| 2026-11-11T10:54:18Z | 2026-11-11T10:54:28Z | `rc-20261111T105420Z.dump` | 1 / 1 | PASS |
| 2026-11-11T16:22:39Z | 2026-11-11T16:23:05Z | `rc-20261111T162257Z.dump` | 1 / 1 | PASS |
