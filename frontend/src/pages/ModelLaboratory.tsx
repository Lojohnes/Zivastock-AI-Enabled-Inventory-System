import React, { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { Science, PlayArrow, Refresh } from '@mui/icons-material'
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { fetchModelVersions, fetchRecommendationOutcomeSummary, runScenario } from '../services/laboratoryApi'
import { ModelVersion, RecommendationOutcomeSummary, ScenarioResult } from '../types/laboratory'

const numberValue = (value: string) => Number(value) || 0

export const ModelLaboratory: React.FC = () => {
  const [models, setModels] = useState<ModelVersion[]>([])
  const [outcomes, setOutcomes] = useState<RecommendationOutcomeSummary | null>(null)
  const [scenario, setScenario] = useState<ScenarioResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [scenarioLoading, setScenarioLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [inputs, setInputs] = useState({ current_quantity: '127', predicted_daily_demand: '31', safety_stock: '29', horizon_days: '7', demand_change_pct: '20', supplier_delay_days: '0' })

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [modelData, outcomeData] = await Promise.all([fetchModelVersions(), fetchRecommendationOutcomeSummary()])
      setModels(modelData)
      setOutcomes(outcomeData)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Unable to load model-laboratory data.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { void load() }, [load])

  const executeScenario = async () => {
    setScenarioLoading(true)
    setError(null)
    try {
      setScenario(await runScenario({
        current_quantity: numberValue(inputs.current_quantity),
        predicted_daily_demand: numberValue(inputs.predicted_daily_demand),
        safety_stock: numberValue(inputs.safety_stock),
        horizon_days: numberValue(inputs.horizon_days),
        demand_change_pct: numberValue(inputs.demand_change_pct),
        supplier_delay_days: numberValue(inputs.supplier_delay_days),
      }))
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Unable to execute scenario.')
    } finally {
      setScenarioLoading(false)
    }
  }

  const chartData = useMemo(() => {
    if (!scenario) return []
    return [
      { label: 'Now', stock: scenario.current_quantity },
      { label: 'Horizon', stock: scenario.ending_quantity_after_horizon },
    ]
  }, [scenario])

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>
  return (
    <Box>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ sm: 'center' }} spacing={2} sx={{ mb: 3 }}>
        <Box><Typography variant="h4" fontWeight={700}>AI Model Laboratory</Typography><Typography color="text.secondary">Reproducibility, comparison and decision scenarios</Typography></Box>
        <Button startIcon={<Refresh />} variant="outlined" onClick={() => void load()}>Refresh registry</Button>
      </Stack>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <MetricCard title="Registered models" value={models.length} />
        <MetricCard title="Recommendations completed" value={outcomes?.completed || 0} />
        <MetricCard title="Recommendation success" value={`${(outcomes?.success_rate || 0).toFixed(1)}%`} />
        <MetricCard title="Pending decisions" value={outcomes?.pending || 0} />
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={7}>
          <Paper sx={{ p: 2 }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}><Science color="primary" /><Typography variant="h6">Model registry and evaluation</Typography></Stack>
            <Table size="small">
              <TableHead><TableRow><TableCell>Algorithm</TableCell><TableCell>Version</TableCell><TableCell>Status</TableCell><TableCell>Metrics</TableCell></TableRow></TableHead>
              <TableBody>{models.map((model) => <TableRow key={model.id}><TableCell>{model.algorithm}</TableCell><TableCell>{model.version}</TableCell><TableCell>{model.status}</TableCell><TableCell><Typography variant="caption">{Object.entries(model.evaluation_metrics || {}).map(([key, value]) => `${key}: ${value}`).join(' · ') || 'No metrics recorded'}</Typography></TableCell></TableRow>)}</TableBody>
            </Table>
            {models.length === 0 && <Alert severity="info" sx={{ mt: 2 }}>No trained or evaluated models are registered yet. Run the anomaly experiment endpoint to populate this registry.</Alert>}
          </Paper>
        </Grid>

        <Grid item xs={12} lg={5}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>What-if scenario</Typography>
            <Grid container spacing={1.5}>
              <ScenarioField label="Current stock" value={inputs.current_quantity} name="current_quantity" setInputs={setInputs} />
              <ScenarioField label="Daily demand" value={inputs.predicted_daily_demand} name="predicted_daily_demand" setInputs={setInputs} />
              <ScenarioField label="Safety stock" value={inputs.safety_stock} name="safety_stock" setInputs={setInputs} />
              <ScenarioField label="Horizon days" value={inputs.horizon_days} name="horizon_days" setInputs={setInputs} />
              <ScenarioField label="Demand change %" value={inputs.demand_change_pct} name="demand_change_pct" setInputs={setInputs} />
              <ScenarioField label="Supplier delay days" value={inputs.supplier_delay_days} name="supplier_delay_days" setInputs={setInputs} />
            </Grid>
            <Button fullWidth variant="contained" startIcon={<PlayArrow />} sx={{ mt: 2 }} onClick={() => void executeScenario()} disabled={scenarioLoading}>{scenarioLoading ? 'Calculating…' : 'Run scenario'}</Button>
            {scenario && <Box sx={{ mt: 2 }}><Alert severity={scenario.stockout_risk === 'CRITICAL' || scenario.stockout_risk === 'HIGH' ? 'error' : 'info'}>Stockout risk: {scenario.stockout_risk} · {scenario.days_until_stockout == null ? 'No stockout estimated' : `${scenario.days_until_stockout.toFixed(1)} days`}</Alert><Box sx={{ height: 180, mt: 1 }}><ResponsiveContainer width="100%" height="100%"><LineChart data={chartData}><XAxis dataKey="label" /><YAxis /><Tooltip /><Line type="monotone" dataKey="stock" stroke="#1976d2" strokeWidth={3} /></LineChart></ResponsiveContainer></Box><Typography variant="caption" color="text.secondary">Ending quantity after scenario horizon: {scenario.ending_quantity_after_horizon.toFixed(1)} units</Typography></Box>}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}><Typography variant="h6" sx={{ mb: 2 }}>Recommendation outcome analytics</Typography><Grid container spacing={2}><MetricCard title="Approved" value={outcomes?.approved || 0} /><MetricCard title="Rejected" value={outcomes?.rejected || 0} /><MetricCard title="Overridden" value={outcomes?.overridden || 0} /><MetricCard title="Successful outcomes" value={outcomes?.outcomes.success || 0} /></Grid></Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

const MetricCard: React.FC<{ title: string; value: string | number }> = ({ title, value }) => <Grid item xs={12} sm={6} md={3}><Card><CardContent><Typography variant="body2" color="text.secondary">{title}</Typography><Typography variant="h4" fontWeight={700}>{value}</Typography></CardContent></Card></Grid>

const ScenarioField: React.FC<{ label: string; value: string; name: string; setInputs: React.Dispatch<React.SetStateAction<any>> }> = ({ label, value, name, setInputs }) => <Grid item xs={6}><TextField fullWidth size="small" type="number" label={label} value={value} onChange={(event) => setInputs((current: any) => ({ ...current, [name]: event.target.value }))} /></Grid>
