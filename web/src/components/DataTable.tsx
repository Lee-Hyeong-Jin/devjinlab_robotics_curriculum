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

/**
 * Shared table for the resources list and the admin and audit screens.
 *
 * Below `md` a table with four columns does not fit a phone, and scrolling it sideways hides the
 * columns that explain each row. So each row is laid out as a stacked card there, with the column
 * name printed above every value but the first (frontend.md §4.2). The markup stays one table at
 * every width; the roles are spelled out because a `display` other than `table` makes some
 * browsers drop the table semantics from the accessibility tree.
 */
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
      <table role="table" className="block w-full border-collapse text-sm md:table">
        <caption
          className={cx(
            captionVisible
              ? 'text-muted block px-4 py-3 text-left text-sm md:table-caption'
              : 'sr-only',
          )}
        >
          {caption}
        </caption>
        <thead className="max-md:sr-only">
          <tr role="row" className="border-border-default bg-subtle border-b">
            {columns.map((column) => (
              <th
                key={column.key}
                role="columnheader"
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
        <tbody className="block md:table-row-group">
          {rows.map((row, index) => (
            <tr
              key={rowKey(row, index)}
              role="row"
              className="border-border-default flex flex-col gap-2 border-b px-4 py-3 last:border-b-0 md:table-row md:p-0"
            >
              {columns.map((column, columnIndex) => (
                <td
                  key={column.key}
                  className={cx(
                    // Below `md`: the first column is the row's title; the others read "name  value".
                    'text-primary min-w-0 align-top wrap-anywhere md:table-cell md:px-4 md:py-3',
                    columnIndex > 0
                      ? 'grid grid-cols-[5.5rem_minmax(0,1fr)] items-baseline justify-items-start gap-x-3'
                      : 'block font-medium md:font-normal',
                    column.hideOnMobile && 'max-sm:hidden',
                    column.className,
                  )}
                >
                  {/* The header row is visually hidden below `md`, so name the value here.
                      Hidden from assistive tech: it already reads the column header. */}
                  {columnIndex > 0 ? (
                    <span aria-hidden="true" className="text-muted text-xs font-semibold md:hidden">
                      {column.header}
                    </span>
                  ) : null}
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
