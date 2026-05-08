import { useEffect, useState, useCallback } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { fetchConfidenceReport, type ConfidenceReport } from '../api/healingApi'

const PIE_COLORS = ['#22c55e', '#f59e0b', '#ef4444']

export default function ConfidenceChart() {
  const [report, setReport] = useState<ConfidenceReport | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try { setReport(await fetchConfidenceReport()) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const pieData = report ? [
    { name: 'HIGH (Auto-Heal)', value: report.high_confidence_count },
    { name: 'MEDIUM (Review)', value: report.medium_confidence_count },
    { name: 'LOW (Fail)', value: report.low_confidence_count },
  ] : []

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload?.length) {
      return (
        <div style={{background:'#161b30',border:'1px solid #1e2540',borderRadius:8,padding:'10px 14px',fontSize:'0.82rem'}}>
          <div style={{fontWeight:700}}>{payload[0].payload.range}</div>
          <div style={{color:'#6c63ff'}}>Count: {payload[0].value}</div>
        </div>
      )
    }
    return null
  }

  if (loading) return <div className="page-content"><div className="skeleton" style={{height:400,borderRadius:18}} /></div>

  return (
    <>
      <div className="topbar">
        <div>
          <div className="topbar-title">Confidence Charts</div>
          <div className="topbar-sub">Score distribution and confidence level breakdown</div>
        </div>
        <button id="refresh-charts" className="refresh-btn" onClick={load}>↻ Refresh</button>
      </div>

      <div className="page-content">
        <div className="charts-row">
          {/* Score Distribution Bar Chart */}
          <div className="chart-card">
            <div className="card-header">
              <span className="card-title">Score Distribution (by 10-point range)</span>
              <span className="card-badge">{report?.total_healed ?? 0} events</span>
            </div>
            {(report?.score_distribution?.length ?? 0) === 0 ? (
              <div className="empty-state"><div className="icon">📊</div><p>No data yet — run tests first</p></div>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={report!.score_distribution} margin={{top:4,right:4,left:-20,bottom:4}}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2540" />
                  <XAxis dataKey="range" tick={{fill:'#64748b',fontSize:11}} />
                  <YAxis tick={{fill:'#64748b',fontSize:11}} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" fill="url(#barGrad)" radius={[4,4,0,0]} />
                  <defs>
                    <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6c63ff" />
                      <stop offset="100%" stopColor="#00d4ff" stopOpacity={0.6} />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Confidence Level Pie Chart */}
          <div className="chart-card">
            <div className="card-header">
              <span className="card-title">Confidence Levels</span>
            </div>
            {pieData.every(d => d.value === 0) ? (
              <div className="empty-state"><div className="icon">🥧</div><p>No data yet</p></div>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90}
                       paddingAngle={3} dataKey="value">
                    {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                  </Pie>
                  <Tooltip contentStyle={{background:'#161b30',border:'1px solid #1e2540',borderRadius:8,fontSize:'0.82rem'}} />
                  <Legend iconType="circle" iconSize={8} formatter={(v) => <span style={{color:'#e8eaf6',fontSize:'0.78rem'}}>{v}</span>} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Summary Stats */}
        <div className="stats-row">
          {[
            {label:'Average Score',value:`${report?.avg_confidence_score ?? 0}`,sub:'Overall'},
            {label:'Auto-Healed',value:`${report?.auto_heal_count ?? 0}`,sub:`${report?.success_rate_percent ?? 0}% success rate`},
            {label:'Manual Review',value:`${report?.manual_review_count ?? 0}`,sub:'Needs attention'},
            {label:'Failed',value:`${report?.fail_count ?? 0}`,sub:'No match found'},
          ].map(({label,value,sub}) => (
            <div key={label} className="stat-card">
              <div className="stat-label">{label}</div>
              <div className="stat-value">{value}</div>
              <div className="stat-sub">{sub}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}
