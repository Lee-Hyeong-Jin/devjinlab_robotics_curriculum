import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

const WEB = process.cwd()

/**
 * A device with no math font (most phones) drew a matrix with brackets one line tall (#30).
 * The fix is three things that have to stay together: the font package, its import, and the
 * family being named in the stylesheet.
 */
describe('the math web font', () => {
  it('is a dependency under an open licence, with its file present', () => {
    const pkg = JSON.parse(readFileSync(join(WEB, 'package.json'), 'utf8'))
    expect(pkg.dependencies['@fontsource/stix-two-math']).toMatch(/^\d/)
    const font = join(WEB, 'node_modules/@fontsource/stix-two-math')
    expect(JSON.parse(readFileSync(join(font, 'package.json'), 'utf8')).license).toBe('OFL-1.1')
    expect(existsSync(join(font, 'files/stix-two-math-latin-400-normal.woff2'))).toBe(true)
  })

  it('is imported by the root layout and named for formulas, after the installed fonts', () => {
    const layout = readFileSync(join(WEB, 'src/app/layout.tsx'), 'utf8')
    expect(layout).toContain("import '@fontsource/stix-two-math/400.css'")
    const css = readFileSync(join(WEB, 'src/app/globals.css'), 'utf8')
    const rule = /\nmath \{\s*font-family:([^;]+);/.exec(css)?.[1] ?? ''
    const families = rule.split(',').map((name) => name.trim().replace(/'/g, ''))
    expect(families).toContain('STIX Two Math')
    // Fonts a platform already has come first, so they are used without a download.
    expect(families.indexOf('Cambria Math')).toBeLessThan(families.indexOf('STIX Two Math'))
    expect(families.at(-1)).toBe('math')
  })
})
