import { useEffect, useState, useCallback } from 'react'
import { fetchHealingHistory, fetchConfidenceReport, type HealingRecord, type ConfidenceReport } from '../api/healingApi'

export default function Dashboard() {
  const [report, setReport] = useState<ConfidenceReport | null>(null)
  const [recent, setRecent] = useState<HealingRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [spinning, setSpinning] = useState(false)
  const [lastRefresh, setLastRefresh] = useState(new Date())

  const load = useCallback(async () => {
    try {
      const [rep, hist] = await Promise.all([fetchConfidenceReport(), fetchHealingHistory(5)])
      setReport(rep)
      setRecent(hist)
      setLastRefresh(new Date())
    } catch {
      /* MCP server may not be running yet */
    } finally {
      setLoading(false)
      setSpinning(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const refresh = () => { setSpinning(true); load() }

  const decisionBadge = (d: string) => {
    const map: Record<string, string> = { AUTO_HEAL: 'badge-auto', MANUAL_REVIEW: 'badge-manual', FAIL: 'badge-fail' }
    return <span className={`badge ${map[d] ?? ''}`}>{d}</span>
  }

  const scoreColor = (s: number) =>
    s >= 85 ? '#22c55e' : s >= 60 ? '#f59e0b' : '#ef4444'

  if (loading) return (
    <div className="page-content">
      <div className="stats-row">
        {[1,2,3,4].map(i => <div key={i} className="stat-card"><div className="skeleton" style={{height:80}} /></div>)}
      </div>
    </div>
  )

  return (
    <>
      <div className="topbar">
        <div>
          <div className="topbar-title">Overview Dashboard</div>
          <div className="topbar-sub">Last updated: {lastRefresh.toLocaleTimeString()}</div>
        </div>
        <div className="topbar-actions">
          <button id="refresh-btn" className={`refresh-btn${spinning ? ' spinning' : ''}`} onClick={refresh}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            Refresh
          </button>
        </div>
      </div>

      <div className="page-content">
        {/* ── KPI Cards ───────────────────────────────────────── */}
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-icon">🧪</div>
            <div className="stat-label">Total Healing Events</div>
            <div className="stat-value">{report?.total_healed ?? 0}</div>
            <div className="stat-sub">All time</div>
          </div>
          <div className="stat-card green">
            <div className="stat-icon">✅</div>
            <div className="stat-label">Healing Success Rate</div>
            <div className="stat-value" style={{color:'#22c55e'}}>{report?.success_rate_percent ?? 0}%</div>
            <div className="stat-sub">{report?.auto_heal_count ?? 0} auto-healed</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🎯</div>
            <div className="stat-label">Avg Confidence Score</div>
            <div className="stat-value" style={{color:'#00d4ff'}}>{report?.avg_confidence_score ?? 0}</div>
            <div className="stat-sub">Out of 100</div>
          </div>
          <div className="stat-card amber">
            <div className="stat-icon">⚠️</div>
            <div className="stat-label">Manual Review Required</div>
            <div className="stat-value" style={{color:'#f59e0b'}}>{report?.manual_review_count ?? 0}</div>
            <div className="stat-sub">{report?.fail_count ?? 0} failures</div>
          </div>
        </div>

        {/* ── Confidence Level Breakdown ─────────────────────── */}
        <div className="charts-row">
          <div className="chart-card">
            <div className="card-header">
              <span className="card-title">Confidence Level Distribution</span>
              <span className="card-badge">Breakdown</span>
            </div>
            <div style={{display:'flex',gap:16,marginBottom:16}}>
              {[
                {label:'HIGH',count:report?.high_confidence_count??0,color:'#22c55e'},
                {label:'MEDIUM',count:report?.medium_confidence_count??0,color:'#f59e0b'},
                {label:'LOW',count:report?.low_confidence_count??0,color:'#ef4444'},
              ].map(({label,count,color}) => (
                <div key={label} style={{flex:1,background:'rgba(0,0,0,0.2)',borderRadius:10,padding:'14px 16px'}}>
                  <div style={{fontSize:'0.7rem',color:'#64748b',marginBottom:6}}>{label}</div>
                  <div style={{fontSize:'1.6rem',fontWeight:800,color}}>{count}</div>
                </div>
              ))}
            </div>
            {report && report.total_healed > 0 && (
              <div style={{height:14,borderRadius:7,overflow:'hidden',display:'flex',gap:2}}>
                {[
                  {pct:(report.high_confidence_count/report.total_healed)*100,color:'#22c55e'},
                  {pct:(report.medium_confidence_count/report.total_healed)*100,color:'#f59e0b'},
                  {pct:(report.low_confidence_count/report.total_healed)*100,color:'#ef4444'},
                ].map(({pct,color},i) => (
                  <div key={i} style={{width:`${pct}%`,background:color,minWidth:pct>0?4:0,borderRadius:7}} />
                ))}
              </div>
            )}
          </div>

          <div className="chart-card">
            <div className="card-header">
              <span className="card-title">Decision Summary</span>
            </div>
            {[
              {label:'AUTO_HEAL',count:report?.auto_heal_count??0,color:'#22c55e',icon:'✅'},
              {label:'MANUAL_REVIEW',count:report?.manual_review_count??0,color:'#f59e0b',icon:'⚠️'},
              {label:'FAIL',count:report?.fail_count??0,color:'#ef4444',icon:'❌'},
            ].map(({label,count,color,icon}) => (
              <div key={label} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:'1px solid #1e2540'}}>
                <span>{icon}</span>
                <span style={{flex:1,fontSize:'0.82rem'}}>{label}</span>
                <span style={{fontWeight:700,color}}>{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* ── Recent Healing Events ────────────────────────────── */}
        <div className="table-card">
          <div className="card-header">
            <span className="card-title">Recent Healing Events</span>
            <span className="card-badge">{recent.length} records</span>
          </div>
          {recent.length === 0 ? (
            <div className="empty-state"><div className="icon">🔬</div><p>Run Playwright tests to see healing events here</p></div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Test</th><th>Original Locator</th><th>Healed Locator</th>
                  <th>Score</th><th>Decision</th><th>Time</th>
                </tr>
              </thead>
              <tbody>
                {recent.map(r => (
                  <tr key={r.healing_id}>
                    <td><span style={{fontSize:'0.78rem'}}>{r.test_name ?? '—'}</span></td>
                    <td><span className="mono" style={{color:'#ef4444'}}>{r.original_locator}</span></td>
                    <td><span className="mono" style={{color:'#22c55e'}}>{r.healed_locator ?? '—'}</span></td>
                    <td>
                      <div className="score-bar">
                        <div className="score-track"><div className="score-fill" style={{width:`${r.confidence_score}%`,background:scoreColor(r.confidence_score)}} /></div>
                        <span className="score-text" style={{color:scoreColor(r.confidence_score)}}>{r.confidence_score.toFixed(1)}</span>
                      </div>
                    </td>
                    <td>{decisionBadge(r.decision)}</td>
                    <td><span style={{fontSize:'0.72rem',color:'#64748b'}}>{new Date(r.timestamp).toLocaleTimeString()}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  )
}
