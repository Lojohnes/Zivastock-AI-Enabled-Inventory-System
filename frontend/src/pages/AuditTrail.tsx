import React, { useCallback, useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  CircularProgress,
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
import { Refresh, Security } from '@mui/icons-material'
import api from '../services/api'

interface AuditAction {
  action: string
  entity_type: string
  entity_id?: number | null
  old_value?: Record<string, unknown> | null
  new_value?: Record<string, unknown> | null
  user?: { email?: string; first_name?: string; last_name?: string } | null
  ip_address?: string | null
  created_at: string
}

export const AuditTrail: React.FC = () => {
  const [actions, setActions] = useState<AuditAction[]>([])
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const response = await api.get('/reports/audit', {
        params: {
          start_date: startDate ? `${startDate}T00:00:00` : undefined,
          end_date: endDate ? `${endDate}T23:59:59` : undefined,
        },
      })
      setActions(response.data.actions || [])
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Unable to load audit trail. Check your audit-report permission.')
    } finally {
      setLoading(false)
    }
  }, [startDate, endDate])

  useEffect(() => { void load() }, [load])

  return (
    <Box>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ sm: 'center' }} spacing={2} sx={{ mb: 3 }}>
        <Box><Typography variant="h4" fontWeight={700}>Audit Trail</Typography><Typography color="text.secondary">Trace who did what, when and why.</Typography></Box>
        <Button startIcon={<Refresh />} variant="outlined" onClick={() => void load()}>Refresh</Button>
      </Stack>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ sm: 'center' }}>
          <TextField label="Start date" type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} InputLabelProps={{ shrink: true }} />
          <TextField label="End date" type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} InputLabelProps={{ shrink: true }} />
          <Button variant="contained" startIcon={<Security />} onClick={() => void load()}>Apply filters</Button>
        </Stack>
      </Paper>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Paper sx={{ p: 2 }}>
        {loading ? <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}><CircularProgress /></Box> : <TableContainer sx={{ maxHeight: 620 }}><Table stickyHeader size="small"><TableHead><TableRow><TableCell>Time</TableCell><TableCell>User</TableCell><TableCell>Action</TableCell><TableCell>Entity</TableCell><TableCell>Entity ID</TableCell><TableCell>Details</TableCell></TableRow></TableHead><TableBody>{actions.map((item, index) => <TableRow key={`${item.created_at}-${index}`} hover><TableCell>{new Date(item.created_at).toLocaleString()}</TableCell><TableCell>{item.user?.email || 'System'}</TableCell><TableCell>{item.action}</TableCell><TableCell>{item.entity_type}</TableCell><TableCell>{item.entity_id ?? '—'}</TableCell><TableCell>{JSON.stringify(item.new_value || item.old_value || {})}</TableCell></TableRow>)}</TableBody></Table></TableContainer>}
        {!loading && actions.length === 0 && <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>No audit events found for the selected period.</Typography>}
      </Paper>
    </Box>
  )
}
