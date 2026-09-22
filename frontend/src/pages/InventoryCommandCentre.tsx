import React, { useCallback, useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  InputAdornment,
} from '@mui/material'
import {
  CheckCircle,
  ErrorOutline,
  Inventory,
  LocalShipping,
  Refresh,
  Warning,
  Search,
} from '@mui/icons-material'
import { fetchCommandCentre, fetchProductIntelligence, decideRecommendation } from '../services/intelligenceApi'
import { CommandCentreResponse, ProductIntelligence, RecommendationRecord, RiskRecord } from '../types/intelligence'

const riskColor = (risk: string): 'default' | 'success' | 'warning' | 'error' => {
  if (risk === 'CRITICAL' || risk === 'HIGH') return 'error'
  if (risk === 'MEDIUM') return 'warning'
  if (risk === 'LOW') return 'success'
  return 'default'
}

const priorityColor = (priority: string): 'default' | 'primary' | 'warning' | 'error' => {
  if (priority === 'IMMEDIATE') return 'error'
  if (priority === 'HIGH_PRIORITY') return 'warning'
  if (priority === 'REVIEW') return 'primary'
  return 'default'
}

const formatNumber = (value?: number | null) => value == null ? '—' : value.toFixed(1)

export const InventoryCommandCentre: React.FC = () => {
  const [data, setData] = useState<CommandCentreResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedProduct, setSelectedProduct] = useState<ProductIntelligence | null>(null)
  const [selectedRecommendation, setSelectedRecommendation] = useState<RecommendationRecord | null>(null)
  const [decisionLoading, setDecisionLoading] = useState(false)
  const [riskSearch, setRiskSearch] = useState('')
  const [riskFilter, setRiskFilter] = useState('ALL')

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    setData(null)
    setSelectedProduct(null)
    setSelectedRecommendation(null)
    try {
      setData(await fetchCommandCentre(10))
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Unable to load inventory intelligence.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { void load() }, [load])

  const openProduct = async (productId: number) => {
    try {
      setSelectedProduct(await fetchProductIntelligence(productId))
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Unable to load product intelligence.')
    }
  }

  const handleDecision = async (decision: 'APPROVED' | 'REJECTED' | 'OVERRIDDEN') => {
    if (!selectedRecommendation) return
    const reason = decision === 'OVERRIDDEN' ? window.prompt('Enter the override reason:') || '' : undefined
    if (decision === 'OVERRIDDEN' && !reason) return
    setDecisionLoading(true)
    try {
      await decideRecommendation(selectedRecommendation.id, decision, reason)
      setSelectedRecommendation(null)
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Unable to record the recommendation decision.')
    } finally {
      setDecisionLoading(false)
    }
  }

  const filteredRisks = data?.top_risks.filter((risk) => {
    const matchesSearch = `${risk.product_name || ''} ${risk.product_id}`.toLowerCase().includes(riskSearch.toLowerCase())
    const matchesFilter = riskFilter === 'ALL' || risk.risk_level === riskFilter
    return matchesSearch && matchesFilter
  }) || []

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>
  }

  if (error) {
    return <Alert severity="error" action={<Button color="inherit" onClick={() => void load()}>Retry</Button>}>{error}</Alert>
  }

  if (!data) return <Alert severity="info">No inventory intelligence data is available yet.</Alert>

  const { summary } = data
  return (
    <Box>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ sm: 'center' }} spacing={2} sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={700}>AI Inventory Command Centre</Typography>
          <Typography color="text.secondary">Detect · Explain · Predict · Recommend · Decide</Typography>
        </Box>
        <Button startIcon={<Refresh />} variant="outlined" onClick={() => void load()}>Refresh intelligence</Button>
      </Stack>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Kpi title="Critical risks" value={summary.critical_risks} icon={<ErrorOutline />} color="error.main" />
        <Kpi title="High risks" value={summary.high_risks} icon={<Warning />} color="warning.main" />
        <Kpi title="Stockout risks" value={summary.stockout_risks} icon={<LocalShipping />} color="info.main" />
        <Kpi title="Excess inventory" value={summary.excess_inventory} icon={<Inventory />} color="secondary.main" />
        <Kpi title="Pending decisions" value={summary.pending_recommendations} icon={<CheckCircle />} color="success.main" />
        <Kpi title="Data quality" value={summary.data_quality_score == null ? '—' : `${summary.data_quality_score.toFixed(1)}%`} icon={<CheckCircle />} color="info.main" />
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 2 }}>
            <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" spacing={1.5} sx={{ mb: 1.5 }}>
              <Box><Typography variant="h6">Top inventory risks</Typography><Typography variant="caption" color="text.secondary">Click a product to inspect the evidence chain.</Typography></Box>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
                <TextField size="small" placeholder="Search products" value={riskSearch} onChange={(event) => setRiskSearch(event.target.value)} InputProps={{ startAdornment: <InputAdornment position="start"><Search fontSize="small" /></InputAdornment> }} />
                <ToggleButtonGroup size="small" exclusive value={riskFilter} onChange={(_, value) => value && setRiskFilter(value)}>
                  {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((filter) => <ToggleButton key={filter} value={filter}>{filter === 'ALL' ? 'All' : filter}</ToggleButton>)}
                </ToggleButtonGroup>
              </Stack>
            </Stack>
            <TableContainer>
              <Table size="small">
                <TableHead><TableRow><TableCell>Product</TableCell><TableCell>Risk</TableCell><TableCell>Score</TableCell><TableCell>ABC</TableCell><TableCell>Priority</TableCell></TableRow></TableHead>
                <TableBody>
                  {filteredRisks.map((risk: RiskRecord) => (
                    <TableRow key={risk.id} hover onClick={() => void openProduct(risk.product_id)} sx={{ cursor: 'pointer' }}>
                      <TableCell><Typography fontWeight={600}>{risk.product_name || `Product #${risk.product_id}`}</Typography><Typography variant="caption" color="text.secondary">ID {risk.product_id}</Typography></TableCell>
                      <TableCell><Chip label={risk.risk_level} color={riskColor(risk.risk_level)} size="small" /></TableCell>
                      <TableCell>{formatNumber(risk.total_score)}/100</TableCell>
                      <TableCell><Chip label={`ABC-${risk.abc_class || '—'}`} size="small" variant="outlined" /></TableCell>
                      <TableCell><Chip label={risk.priority} color={priorityColor(risk.priority)} size="small" /></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Stockout exposure</Typography>
            <List dense>
              {data.stockout_exposures.map((item) => (
                <ListItem key={item.id} disableGutters secondaryAction={<Chip label={item.stockout_risk} color={riskColor(item.stockout_risk)} size="small" />}>
                  <ListItemText primary={item.product_name || `Product #${item.product_id}`} secondary={`${formatNumber(item.days_until_stockout)} days cover · ${formatNumber(item.predicted_daily_demand)} units/day`} />
                </ListItem>
              ))}
              {data.stockout_exposures.length === 0 && <ListItem disableGutters><ListItemText primary="No exposure records available" /></ListItem>}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Pending AI recommendations</Typography>
            <Stack spacing={1.5}>
              {data.recommendations.map((recommendation) => (
                <Card key={recommendation.id} variant="outlined">
                  <CardContent sx={{ '&:last-child': { pb: 2 } }}>
                    <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }} justifyContent="space-between">
                      <Box sx={{ flex: 1 }}>
                        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 0.5 }}>
                          <Chip label={recommendation.recommendation_type.replace(/_/g, ' ')} size="small" />
                          <Chip label={recommendation.priority} color={priorityColor(recommendation.priority)} size="small" />
                          <Chip label={recommendation.product_name || `Product #${recommendation.product_id}`} size="small" variant="outlined" />
                        </Stack>
                        <Typography variant="body2">{recommendation.recommendation_text}</Typography>
                        <Typography variant="caption" color="text.secondary">Evidence coverage: {formatNumber(recommendation.confidence_score)}%</Typography>
                      </Box>
                      <Stack direction="row" spacing={1}>
                        <Button size="small" variant="contained" onClick={() => setSelectedRecommendation(recommendation)}>Review</Button>
                        <Button size="small" variant="outlined" onClick={() => void openProduct(recommendation.product_id)}>Details</Button>
                      </Stack>
                    </Stack>
                  </CardContent>
                </Card>
              ))}
              {data.recommendations.length === 0 && <Alert severity="success">There are no pending recommendations.</Alert>}
            </Stack>
          </Paper>
        </Grid>
      </Grid>

      <ProductDialog product={selectedProduct} onClose={() => setSelectedProduct(null)} />
      <DecisionDialog recommendation={selectedRecommendation} loading={decisionLoading} onClose={() => setSelectedRecommendation(null)} onDecision={(decision) => void handleDecision(decision)} />
    </Box>
  )
}

const Kpi: React.FC<{ title: string; value: string | number; icon: React.ReactNode; color: string }> = ({ title, value, icon, color }) => (
  <Grid item xs={12} sm={6} md={4} lg={2.4}>
    <Card sx={{ height: '100%' }}><CardContent><Stack direction="row" justifyContent="space-between" alignItems="center"><Box><Typography variant="body2" color="text.secondary">{title}</Typography><Typography variant="h4" fontWeight={700}>{value}</Typography></Box><Box sx={{ color }}>{icon}</Box></Stack></CardContent></Card>
  </Grid>
)

const ProductDialog: React.FC<{ product: ProductIntelligence | null; onClose: () => void }> = ({ product, onClose }) => (
  <Dialog open={Boolean(product)} onClose={onClose} maxWidth="md" fullWidth>
    <DialogTitle>{product?.product.description || 'Product intelligence'}</DialogTitle>
    <DialogContent dividers>
      {product && <Stack spacing={2}>
        <Typography variant="body2" color="text.secondary">Barcode: {product.product.barcode} · Unit cost: {product.product.unit_cost.toFixed(2)}</Typography>
        <Divider />
        <Typography variant="h6">Risk explanations</Typography>
        {product.risk_scores[0]?.explanation?.map((item, index) => <Alert key={index} severity="info">{item}</Alert>)}
        <Typography variant="h6">Exposure</Typography>
        {product.exposures.map((item) => <Typography key={item.id} variant="body2">{item.stockout_risk} stockout risk · {formatNumber(item.days_until_stockout)} days · {item.excess_quantity.toFixed(1)} excess units</Typography>)}
        <Typography variant="h6">Recommendation history</Typography>
        {product.recommendations.map((item) => <Typography key={item.id} variant="body2">{item.status}: {item.recommendation_text}</Typography>)}
      </Stack>}
    </DialogContent>
    <DialogActions><Button onClick={onClose}>Close</Button></DialogActions>
  </Dialog>
)

const DecisionDialog: React.FC<{ recommendation: RecommendationRecord | null; loading: boolean; onClose: () => void; onDecision: (decision: 'APPROVED' | 'REJECTED' | 'OVERRIDDEN') => void }> = ({ recommendation, loading, onClose, onDecision }) => (
  <Dialog open={Boolean(recommendation)} onClose={onClose} maxWidth="sm" fullWidth>
    <DialogTitle>Review AI recommendation</DialogTitle>
    <DialogContent dividers>
      <Typography variant="body1" sx={{ mb: 2 }}>{recommendation?.recommendation_text}</Typography>
      <Typography variant="subtitle2">Evidence</Typography>
      {recommendation?.evidence.map((item, index) => <Typography key={index} variant="body2" color="text.secondary">• {item}</Typography>)}
      <Alert severity="warning" sx={{ mt: 2 }}>AI recommends; an authorised manager must decide. An anomaly is not proof of misconduct.</Alert>
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose} disabled={loading}>Cancel</Button>
      <Button onClick={() => onDecision('REJECTED')} disabled={loading}>Reject</Button>
      <Button onClick={() => onDecision('OVERRIDDEN')} disabled={loading}>Override</Button>
      <Button variant="contained" onClick={() => onDecision('APPROVED')} disabled={loading}>Approve</Button>
    </DialogActions>
  </Dialog>
)
