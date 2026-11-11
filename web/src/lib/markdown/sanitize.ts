import { defaultSchema } from 'rehype-sanitize'
import type { Options as SanitizeOptions } from 'rehype-sanitize'

/**
 * MathML Core elements emitted by KaTeX (`output: 'mathml'`). Allow-listed so the
 * sanitizer keeps the formula tree instead of flattening it to text.
 */
const MATHML_TAGS = [
  'math',
  'semantics',
  'annotation',
  'annotation-xml',
  'mrow',
  'mi',
  'mn',
  'mo',
  'ms',
  'mtext',
  'mspace',
  'mfrac',
  'msqrt',
  'mroot',
  'mstyle',
  'merror',
  'mpadded',
  'mphantom',
  'menclose',
  'msub',
  'msup',
  'msubsup',
  'munder',
  'mover',
  'munderover',
  'mmultiscripts',
  'mprescripts',
  'none',
  'mtable',
  'mtr',
  'mtd',
  'mlabeledtr',
  'maction',
]

/** Attributes MathML needs; everything else on these elements is dropped. */
const MATHML_ATTRS = [
  'display',
  'displaystyle',
  'scriptlevel',
  'mathvariant',
  'stretchy',
  'fence',
  'separator',
  'lspace',
  'rspace',
  'accent',
  'accentunder',
  'largeop',
  'movablelimits',
  'symmetric',
  'maxsize',
  'minsize',
  'linethickness',
  'columnalign',
  'rowalign',
  'columnspan',
  'rowspan',
  'columnspacing',
  'rowspacing',
  'columnlines',
  'rowlines',
  'frame',
  'width',
  'height',
  'depth',
  'voffset',
  'encoding',
  'xmlns',
  'className',
]

/** highlight.js token classes produced by `rehype-highlight`. */
const HLJS_CLASS = /^hljs(-[a-z_]+)*$/

/**
 * Sanitizer schema for lesson bodies.
 *
 * The content comes from the repository, but the Markdown is rendered without
 * `dangerouslySetInnerHTML` and sanitized anyway (defence in depth, frontend.md §5).
 * `style` is deliberately NOT allowed anywhere — that is why KaTeX runs in MathML
 * mode, which needs no inline styles.
 */
export const lessonSanitizeSchema: SanitizeOptions = {
  ...defaultSchema,
  tagNames: [...(defaultSchema.tagNames ?? []), ...MATHML_TAGS],
  attributes: {
    ...defaultSchema.attributes,
    ...Object.fromEntries(MATHML_TAGS.map((tag) => [tag, MATHML_ATTRS])),
    // These replace (not extend) the default entries: hast-util-sanitize keeps
    // the first rule it finds per attribute, so appending a second `className`
    // rule would be ignored.
    code: [['className', /^language-./, HLJS_CLASS]],
    span: [['className', HLJS_CLASS]],
    div: [['className', 'math', 'math-display']],
    a: [...(defaultSchema.attributes?.a ?? []), ['target'], ['rel']],
    th: [...(defaultSchema.attributes?.th ?? []), ['scope'], ['align']],
    td: [...(defaultSchema.attributes?.td ?? []), ['align']],
  },
  protocols: {
    ...defaultSchema.protocols,
    href: ['http', 'https', 'mailto'],
    src: ['http', 'https'],
  },
}
