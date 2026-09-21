import React, { useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { Download, PlayArrow, PointOfSale, AutoAwesome } from '@mui/icons-material'
import { generateDemoTransactions, runDemoPipeline } from '../services/demoPosApi'
import { DemoPosResponse, DemoTransaction } from '../types/demoPos'

const scenarios = ['normal', 'high_demand', 'abnormal_adjustment', 'stock_discrepancy', 'supplier_delay']

export const DemoPOS: React.FC = () => {
  const [scenario, setScenario] = useState('normal')
  const [days, setDays] = useState('30')
  const [seed, setSeed] = useState('42')
  const [data, setData] = useState<DemoPosResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [pipelineLoading, setPipelineLoading] = useState(false)
  const [pipelineResult, setPipelineResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      setData(await generateDemoTransactions(scenario, Number(days) || 30, Number(seed) || 42))
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Unable to generate Demo POS transactions.')
    } finally {
      setLoading(false)
    }
  }

  const runPipeline = async () => {
    setPipelineLoading(true)
    setError(null)
    try {
      setPipelineResult(await runDemoPipeline(scenario, Math.max(Number(days) || 60, 30), Number(seed) || 42))
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Unable to run the AI pipeline. Apply migrations and check backend connectivity.')
    } finally {
      setPipelineLoading(false)
    }
  }

  const summary = useMemo(() => {
    if (!data) return null
    const transactions = data.transactions
    return {
      sales: transactions.filter((item) => item.event_type === 'SALE').length,
      receipts: transactions.filter((item) => item.event_type === 'RECEIPT').length,
      adjustments: transactions.filter((item) => item.event_type === 'ADJUSTMENT').length,
      value: transactions.reduce((total, item) => total + item.transaction_value, 0),
    }
  }, [data])

  const downloadCsv = () => {
    if (!data) return
    const headers = Object.keys(data.transactions[0] || {})
    const rows = data.transactions.map((item) => headers.map((header) => JSON.stringify((item as any)[header] ?? '')).join(','))
    const blob = new Blob([[headers.join(','), ...rows].join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `zivastock-demo-pos-${data.scenario}-${data.seed}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <Box>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ sm: 'center' }} spacing={2} sx={{ mb: 3 }}>
        <Box><Typography variant="h4" fontWeight={700}>Demo POS</Typography><Typography color="text.secondary">Generate safe, repeatable POS/ERP data for demonstration and research.</Typography></Box>
        <Button startIcon={<Download />} variant="outlined" disabled={!data} onClick={downloadCsv}>Download CSV</Button>
      </Stack>
      <Alert severity="info" sx={{ mb: 3 }}>This is a simulator, not a production POS. Generated records are simulated and should be labelled as simulated in research outputs.</Alert>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ sm: 'center' }}>
          <TextField select label="Scenario" value={scenario} onChange={(event) => setScenario(event.target.value)} sx={{ minWidth: 220 }}>
            {scenarios.map((item) => <MenuItem key={item} value={item}>{item.replace(/_/g, ' ')}</MenuItem>)}
          </TextField>
          <TextField type="number" label="Days" value={days} onChange={(event) => setDays(event.target.value)} inputProps={{ min: 1, max: 365 }} />
          <TextField type="number" label="Seed" value={seed} onChange={(event) => setSeed(event.target.value)} />
          <Button variant="contained" startIcon={<PlayArrow />} onClick={() => void run()} disabled={loading || pipelineLoading}>{loading ? 'Generating…' : 'Generate transactions'}</Button>
          <Button variant="outlined" color="secondary" startIcon={<AutoAwesome />} onClick={() => void runPipeline()} disabled={pipelineLoading}>{pipelineLoading ? 'Running AI pipeline…' : 'Load & analyse in AI'}</Button>
        </Stack>
      </Paper>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {pipelineResult && <Alert severity="success" sx={{ mb: 3 }}>
        {pipelineResult.message} Risk scores: {pipelineResult.risk_scores}; recommendations: {pipelineResult.recommendations}.
      </Alert>}

      {data && summary && <>
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Metric title="Records" value={data.records} />
          <Metric title="Sales" value={summary.sales} />
          <Metric title="Receipts" value={summary.receipts} />
          <Metric title="Adjustments" value={summary.adjustments} />
          <Metric title="Transaction value" value={summary.value.toFixed(2)} />
        </Grid>
        <Paper sx={{ p: 2 }}>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}><PointOfSale color="primary" /><Typography variant="h6">Generated transaction stream</Typography><Chip size="small" label={`Seed ${data.seed}`} /></Stack>
          <TableContainer sx={{ maxHeight: 560 }}>
            <Table stickyHeader size="small">
              <TableHead><TableRow><TableCell>Time</TableCell><TableCell>Product</TableCell><TableCell>Type</TableCell><TableCell align="right">Quantity</TableCell><TableCell align="right">Value</TableCell><TableCell>Reference</TableCell></TableRow></TableHead>
              <TableBody>{data.transactions.map((item: DemoTransaction) => <TableRow key={item.source_record_id} hover><TableCell>{new Date(item.event_timestamp).toLocaleString()}</TableCell><TableCell><Typography fontWeight={600}>{item.description}</Typography><Typography variant="caption" color="text.secondary">{item.barcode}</Typography></TableCell><TableCell><Chip size="small" label={item.event_type} color={item.event_type === 'ADJUSTMENT' ? 'error' : item.event_type === 'SALE' ? 'primary' : 'default'} /></TableCell><TableCell align="right">{item.quantity}</TableCell><TableCell align="right">{item.transaction_value.toFixed(2)}</TableCell><TableCell>{item.reference_number}</TableCell></TableRow>)}</TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </>}
    </Box>
  )
}

const Metric: React.FC<{ title: string; value: string | number }> = ({ title, value }) => <Grid item xs={12} sm={6} md={2.4}><Card><CardContent><Typography variant="body2" color="text.secondary">{title}</Typography><Typography variant="h5" fontWeight={700}>{value}</Typography></CardContent></Card></Grid>
