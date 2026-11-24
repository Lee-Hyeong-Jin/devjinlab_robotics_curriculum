import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

import { organizationSchema } from '@/lib/structured-data'

const WEB = process.cwd()

/** Width and height from a PNG's IHDR chunk. */
function pngSize(file: string): [number, number] {
  const data = readFileSync(join(WEB, file))
  expect(data.subarray(1, 4).toString('latin1'), file).toBe('PNG')
  return [data.readUInt32BE(16), data.readUInt32BE(20)]
}

/** The image sizes packed in an .ico (a 0 byte means 256). */
function icoSizes(file: string): number[] {
  const data = readFileSync(join(WEB, file))
  const count = data.readUInt16LE(4)
  return Array.from({ length: count }, (_unused, index) => data[6 + index * 16] || 256)
}

/**
 * What a search result shows beside the site's name is the favicon, and Google only takes one
 * whose side is a multiple of 48px, square, and reachable from the home page. These files are
 * binary and easy to replace with something that looks fine in a browser tab and is ignored by
 * a search engine, so their shape is pinned here.
 */
describe('site icons', () => {
  it('ships a favicon.ico with a 48px image, plus the sizes a browser tab uses', () => {
    const sizes = icoSizes('src/app/favicon.ico')
    expect(sizes).toContain(48)
    expect(sizes).toEqual(expect.arrayContaining([16, 32]))
  })

  it('offers square PNG icons whose side is a multiple of 48', () => {
    for (const file of ['src/app/icon1.png', 'src/app/icon2.png']) {
      const [width, height] = pngSize(file)
      expect(width, file).toBe(height)
      expect(width % 48, file).toBe(0)
    }
    expect(pngSize('src/app/icon1.png')[0]).toBe(96)
    expect(pngSize('src/app/icon2.png')[0]).toBe(192)
  })

  it('keeps the phone and manifest icons at their declared sizes', () => {
    expect(pngSize('src/app/apple-icon.png')).toEqual([180, 180])
    expect(pngSize('public/icon-192.png')).toEqual([192, 192])
    expect(pngSize('public/icon-512.png')).toEqual([512, 512])
  })

  it('names a logo in the organization markup that exists and is large enough', () => {
    const logo = String(organizationSchema('Site').logo)
    const path = new URL(logo).pathname
    // Google asks for at least 112x112 for an organization logo.
    const [width, height] = pngSize(join('public', path))
    expect(Math.min(width, height)).toBeGreaterThanOrEqual(112)
  })

  it('draws the same mark in the header as in the icon', () => {
    const icon = readFileSync(join(WEB, 'src/app/icon.svg'), 'utf8')
    const mark = readFileSync(join(WEB, 'src/components/BrandMark.tsx'), 'utf8')
    for (const path of ['M16 48h18', 'M25 48V34l14-12 9 8']) {
      expect(icon).toContain(path)
      expect(mark).toContain(path)
    }
  })
})
