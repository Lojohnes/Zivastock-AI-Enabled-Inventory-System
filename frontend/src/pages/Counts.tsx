import { useEffect, useState } from 'react'
import { Alert, Box, Button, FormControl, InputLabel, MenuItem, Paper, Select, Tab, Tabs, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material'
import * as XLSX from 'xlsx'
import { AutoAwesome } from '@mui/icons-material'
import api from '../services/api'

const tabs = [
  { label: 'FirstCount Counts', path: 'first-counts', key: 'counts' },
  { label: 'SecondCount Counts', path: 'second-counts', key: 'counts' },
  { label: 'Comparison Counts', path: 'comparison', key: 'comparison' },
  { label: 'Consolidated Counts', path: 'consolidated', key: 'consolidated' },
]

export const Counts: React.FC = () => {
  const [sessions, setSessions] = useState<{ id: number; name: string }[]>([])
  const [sessionId, setSessionId] = useState('')
  const [tab, setTab] = useState(0)
  const [fileNumber, setFileNumber] = useState('')
  const [sectionNumber, setSectionNumber] = useState('')
  const [rows, setRows] = useState<Record<string, unknown>[]>([])
  const [aiLoading, setAiLoading] = useState(false)
  const [aiResult, setAiResult] = useState<{ message: string; risk_scores: number; recommendations: number } | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/sessions?page=1&limit=100').then((r) => setSessions(r.data.items || [])).catch((e) => setError(e.response?.data?.detail || 'Unable to load sessions'))
  }, [])

  const generate = async () => {
    if (!sessionId) return setError('Select a session first')
    setError('')
    try {
      const config = tabs[tab]
      const response = await api.get(`/reports/${config.path}`, { params: { session_id: Number(sessionId), file_number: fileNumber || undefined, section_number: sectionNumber || undefined } })
      setRows(response.data[config.key] || [])
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Unable to generate counts report')
    }
  }

  const analyzeWithAI = async () => {
    if (!sessionId) return setError('Select a session first')
    setAiLoading(true)
    setError('')
    setAiResult(null)
    try {
      const response = await api.post(`/reports/sessions/${Number(sessionId)}/analyze-ai`)
      setAiResult(response.data)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Unable to analyze stocktake with AI')
    } finally {
      setAiLoading(false)
    }
  }

  const exportExcel = () => {
    if (!rows.length) return
    const sheet = XLSX.utils.json_to_sheet(rows)
    const book = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(book, sheet, tabs[tab].label.slice(0, 31))
    XLSX.writeFile(book, `zivastock_${tabs[tab].path}_${sessionId}.xlsx`)
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Counts</Typography>
      <Paper sx={{ mb: 2 }}>
        <Tabs value={tab} onChange={(_, value) => { setTab(value); setRows([]) }} variant="scrollable">
          {tabs.map((item) => <Tab key={item.path} label={item.label} />)}
        </Tabs>
      </Paper>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
          <FormControl sx={{ minWidth: 240 }}>
            <InputLabel>Session</InputLabel>
            <Select value={sessionId} label="Session" onChange={(e) => setSessionId(e.target.value)}>
              {sessions.map((session) => <MenuItem key={session.id} value={String(session.id)}>{session.id} — {session.name}</MenuItem>)}
            </Select>
          </FormControl>
          <TextField label="File No" value={fileNumber} onChange={(e) => setFileNumber(e.target.value)} />
          <TextField label="Section No" value={sectionNumber} onChange={(e) => setSectionNumber(e.target.value)} />
          <Button variant="contained" onClick={generate}>Generate</Button>
          <Button variant="outlined" color="secondary" startIcon={<AutoAwesome />} onClick={analyzeWithAI} disabled={!sessionId || aiLoading}>{aiLoading ? 'Analyzing…' : 'Analyze in AI'}</Button>
          <Button variant="outlined" onClick={exportExcel} disabled={!rows.length}>Export Excel</Button>
          <Button variant="outlined" onClick={() => window.print()} disabled={!rows.length}>Print / Save PDF</Button>
        </Box>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {aiResult && <Alert severity="success" sx={{ mt: 2 }}>{aiResult.message} Risk scores: {aiResult.risk_scores}; recommendations: {aiResult.recommendations}. Open the AI Command Centre.</Alert>}
      </Paper>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>{tabs[tab].label} — {rows.length} records</Typography>
        <Box sx={{ overflow: 'auto' }}>
          <Table size="small">
            <TableHead><TableRow>{(rows[0] ? Object.keys(rows[0]) : []).map((key) => <TableCell key={key} sx={{ fontWeight: 700 }}>{key}</TableCell>)}</TableRow></TableHead>
            <TableBody>{rows.map((row, index) => <TableRow key={index}>{Object.keys(rows[0] || {}).map((key) => <TableCell key={key}>{String(row[key] ?? '')}</TableCell>)}</TableRow>)}</TableBody>
          </Table>
        </Box>
      </Paper>
    </Box>
  )
}
