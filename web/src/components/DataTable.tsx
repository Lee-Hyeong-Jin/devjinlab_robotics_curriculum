import type { ReactNode } from 'react'

import { cx } from '@/lib/cx'

export interface Column<Row> {
  /** Stable key, also used as the React key. */
  key: string
  header: string
  cell: (row: Row) => ReactNode
  /** Hide below the `sm` breakpoint. */
  hideOnMobile?: boolean
  className?: string
}

export interface DataTableProps<Row> {
  /** Required: every data table gets a caption (WCAG 2.1 AA). */
  caption: string
  /** Render the caption visually, not only for assistive tech. */
  captionVisible?: boolean
  columns: ReadonlyArray<Column<Row>>
  rows: readonly Row[]
  rowKey: (row: Row, index: number) => string
  empty?: ReactNode
}

/** Shared table for the resources list, and later the admin and audit screens. */
export function DataTable<Row>({
  caption,
  captionVisible = false,
  columns,
  rows,
  rowKey,
  empty,
}: DataTableProps<Row>) {
  if (rows.length === 0 && empty) return <>{empty}</>
  return (
    <div className="border-border-default bg-surface overflow-x-auto rounded-[var(--radius-card)] border">
      <table className="w-full border-collapse text-sm">
        <caption
          className={cx(
            captionVisible ? 'text-muted px-4 py-3 text-left text-sm' : 'sr-only',
          )}
        >
          {caption}
        </caption>
        <thead>
          <tr className="border-border-default bg-subtle border-b">
            {columns.map((column) => (
              <th
                key={column.key}
                scope="col"
                className={cx(
                  'text-muted px-4 py-2.5 text-left text-xs font-semibold tracking-wide uppercase',
                  column.hideOnMobile && 'hidden sm:table-cell',
                  column.className,
                )}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={rowKey(row, index)} className="border-border-default border-b last:border-b-0">
              {columns.map((column) => (
                <td
                  key={column.key}
                  className={cx(
                    'text-primary px-4 py-3 align-top',
                    column.hideOnMobile && 'hidden sm:table-cell',
                    column.className,
                  )}
                >
                  {column.cell(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
