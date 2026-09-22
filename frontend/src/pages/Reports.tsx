import { useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import {
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  type SelectChangeEvent,
  MenuItem,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableContainer,
} from '@mui/material'
import { AutoAwesome, Download } from '@mui/icons-material'
import * as XLSX from 'xlsx'
import api from '../services/api'

const reportTypes = [
  { value: 'variance', label: 'Variance Report' },
  { value: 'duplicates', label: 'Duplicate Report' },
  { value: 'missing', label: 'Missing Stock Report' },
  { value: 'productivity', label: 'User Productivity Report' },
]

export const Reports: React.FC = () => {
  const [reportType, setReportType] = useState('variance')
  const [sessionId, setSessionId] = useState('')
  const [sessions, setSessions] = useState<{ id: number; name: string; status: string }[]>([])
  const [data, setData] = useState<unknown>(null)
  const [loading, setLoading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiResult, setAiResult] = useState<{ message: string; risk_scores: number; recommendations: number } | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get('/sessions?page=1&limit=100')
      .then((res) => setSessions(res.data.items || []))
      .catch(() => {})
  }, [])

  const handleGenerate = async () => {
    if (!sessionId) {
      setError('Please enter a session ID')
      return
    }
    setLoading(true)
    setError('')
    try {
      const response = await api.get(`/reports/${reportType}`, {
        params: { session_id: Number(sessionId) },
      })
      setData(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate report')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyzeWithAI = async () => {
    if (!sessionId) {
      setError('Please select a session first')
      return
    }
    setAiLoading(true)
    setError('')
    setAiResult(null)
    try {
      const response = await api.post(`/reports/sessions/${Number(sessionId)}/analyze-ai`)
      setAiResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze stocktake with AI')
    } finally {
      setAiLoading(false)
    }
  }

  const getRows = (): Record<string, unknown>[] => {
    if (!data) return []
    if (Array.isArray(data)) return data as Record<string, unknown>[]
    const d = data as Record<string, unknown>
    for (const key of Object.keys(d)) {
      if (Array.isArray(d[key])) return d[key] as Record<string, unknown>[]
    }
    return [d]
  }

  const handleExportExcel = () => {
    const rows = getRows()
    if (!rows.length) return
    const ws = XLSX.utils.json_to_sheet(rows)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, reportType)
    XLSX.writeFile(wb, `zivastock_${reportType}_${sessionId}.xlsx`)
  }

  const handleExportCSV = () => {
    const rows = getRows()
    if (!rows.length) return
    const ws = XLSX.utils.json_to_sheet(rows)
    const csv = XLSX.utils.sheet_to_csv(ws)
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `zivastock_${reportType}_${sessionId}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const renderReportTable = (): ReactNode => {
    const rows = getRows()
    const cols = rows.length > 0 ? Object.keys(rows[0]) : []
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Report Preview — {rows.length} records
        </Typography>
        <TableContainer sx={{ maxHeight: 500 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                {cols.map((c) => <TableCell key={c} sx={{ fontWeight: 700 }}>{c}</TableCell>)}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.slice(0, 200).map((row, i) => (
                <TableRow key={i} hover>
                  {cols.map((c) => <TableCell key={c}>{String(row[c] ?? '')}</TableCell>)}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {rows.length > 200 && (
          <Typography variant="caption" color="text.secondary" mt={1} display="block">
            Showing first 200 of {rows.length} records. Export to see all.
          </Typography>
        )}
      </Paper>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Reports
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
          <FormControl sx={{ minWidth: 220 }}>
            <InputLabel>Report Type</InputLabel>
            <Select
              value={reportType}
              label="Report Type"
              onChange={(event: SelectChangeEvent<string>) => setReportType(event.target.value)}
            >
              {reportTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 220 }}>
            <InputLabel>Session</InputLabel>
            <Select
              value={sessionId}
              label="Session"
              onChange={(event: SelectChangeEvent<string>) => setSessionId(event.target.value)}
            >
              {sessions.length === 0 && (
                <MenuItem value="" disabled>
                  No sessions available
                </MenuItem>
              )}
              {sessions.map((s) => (
                <MenuItem key={s.id} value={String(s.id)}>
                  {s.id} — {s.name} ({s.status})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Generate'}
          </Button>

          <Button
            variant="outlined"
            color="secondary"
            startIcon={<AutoAwesome />}
            onClick={handleAnalyzeWithAI}
            disabled={!sessionId || aiLoading}
          >
            {aiLoading ? <CircularProgress size={22} /> : 'Analyze in AI'}
          </Button>

          {data != null ? (
            <>
              <Button variant="outlined" startIcon={<Download />} onClick={handleExportExcel} color="success">
                Export Excel
              </Button>
              <Button variant="outlined" startIcon={<Download />} onClick={handleExportCSV}>
                Export CSV
              </Button>
            </>
          ) : null}
        </Box>

        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {aiResult && <Alert severity="success" sx={{ mt: 2 }}>
          {aiResult.message} Risk scores: {aiResult.risk_scores}; recommendations: {aiResult.recommendations}. Open the AI Command Centre to review.
        </Alert>}
      </Paper>

      {data != null ? renderReportTable() : null}
    </Box>
  )
}
