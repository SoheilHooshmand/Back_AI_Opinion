import { useMemo, useState } from 'react'
import { Pagination, Paper, Select, Table, TextInput } from '@mantine/core'
import styles from './studies.module.css'
import { mockResults } from './mockData'

const PAGE_SIZE = 10

function StudiesPage() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)

  const filteredData = useMemo(() => {
    return mockResults.filter((row) => row.question.toLowerCase().includes(search.toLowerCase()))
  }, [search])

  const paginatedData = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE
    return filteredData.slice(start, start + PAGE_SIZE)
  }, [filteredData, page])

  return (
    <div className={styles.page}>
      {/* ---------- Header ---------- */}
      <div className={styles.header}>
        <button className={styles.backBtn}>← Results</button>
        <h1 className={styles.title}>Study name</h1>
      </div>

      {/* ---------- Filters ---------- */}
      <div className={styles.filters}>
        <TextInput placeholder="Search" value={search} onChange={(e) => setSearch(e.currentTarget.value)} />

        <Select
          placeholder="Action"
          data={[
            { label: 'Export CSV', value: 'csv' },
            { label: 'Delete', value: 'delete' },
          ]}
        />
      </div>

      {/* ---------- Table ---------- */}
      <Paper radius="md" withBorder className={styles.tableWrapper}>
        <Table horizontalSpacing="md" verticalSpacing="md" bg={'white'}>
          <thead className={styles.thead}>
            <tr>
              <th className={styles.th}>Question</th>
              <th
                style={{
                  borderRight: '1px solid #e9ecef',
                  padding: '12px 16px',
                  fontWeight: 500,
                  fontSize: '13px',
                  color: '#495057',
                }}
              >
                Silicon user ID
              </th>
              <th className={styles.th}>Silicon user answer</th>
              <th className={styles.th}>Data answer</th>
              <th className={styles.th}>Accuracy</th>
            </tr>
          </thead>

          <tbody>
            {paginatedData.map((row) => (
              <tr key={row.id} className={styles.tr}>
                <td className={styles.td}>{row.question}</td>
                <td className={styles.td}>{row.siliconUserId}</td>
                <td className={styles.td}>{row.siliconAnswer}</td>
                <td className={styles.td}>{row.dataAnswer}</td>
                <td className={styles.td}>{row.accuracy}</td>
              </tr>
            ))}

            {paginatedData.length === 0 && (
              <tr>
                <td colSpan={5} className={styles.empty}>
                  No results found
                </td>
              </tr>
            )}
          </tbody>
        </Table>
      </Paper>

      {/* ---------- Pagination ---------- */}
      <div className={styles.pagination}>
        <Pagination value={page} onChange={setPage} total={Math.ceil(filteredData.length / PAGE_SIZE)} />
      </div>
    </div>
  )
}

export default StudiesPage
