'use client'

import {
  createContext,
  isValidElement,
  useContext,
  useRef,
  useState,
  type HTMLAttributes,
  type ReactNode,
} from 'react'

export interface CodeToolLabels {
  copy: string
  copied: string
  download: string
}

const DEFAULT_LABELS: CodeToolLabels = {
  copy: 'Copy',
  copied: 'Copied',
  download: 'Download .py',
}

const LabelsContext = createContext<CodeToolLabels>(DEFAULT_LABELS)

/** Gives every code block under it its button labels in the reader's language. */
export function CodeToolLabelsProvider({
  labels,
  children,
}: {
  labels: CodeToolLabels
  children: ReactNode
}) {
  return <LabelsContext.Provider value={labels}>{children}</LabelsContext.Provider>
}

/** The language of a fenced block, from the `language-…` class highlight.js puts on `<code>`. */
function languageOf(children: ReactNode): string | null {
  const child = Array.isArray(children) ? children[0] : children
  if (!isValidElement<{ className?: string }>(child)) return null
  return /(?:^|\s)language-([\w+-]+)/.exec(child.props.className ?? '')?.[1] ?? null
}

/**
 * A fenced code block with "Copy" and, for Python, "Download .py" (#49).
 *
 * Selecting a forty-line example by hand, on a phone especially, was the only way to run it.
 * The text is read from the rendered block, so what is copied is exactly what is shown. The
 * buttons need JavaScript; without it the block is simply a code block.
 */
export function CodeBlock({ children, ...rest }: HTMLAttributes<HTMLPreElement>) {
  const labels = useContext(LabelsContext)
  const pre = useRef<HTMLPreElement>(null)
  const [copied, setCopied] = useState(false)
  const python = ['python', 'py', 'python3'].includes(languageOf(children) ?? '')

  const text = () => `${(pre.current?.textContent ?? '').replace(/\n$/, '')}\n`

  async function copy() {
    try {
      await navigator.clipboard.writeText(text())
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch {
      // No clipboard access (an insecure origin, a denied permission): nothing to report —
      // the code is still on screen to select.
    }
  }

  function download() {
    const url = URL.createObjectURL(new Blob([text()], { type: 'text/x-python' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'example.py'
    document.body.append(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="code-block">
      <div className="code-tools">
        <button type="button" onClick={copy}>
          <span aria-live="polite">{copied ? labels.copied : labels.copy}</span>
        </button>
        {python ? (
          <button type="button" onClick={download}>
            {labels.download}
          </button>
        ) : null}
      </div>
      <pre ref={pre} {...rest}>
        {children}
      </pre>
    </div>
  )
}
