import { useEffect, useState, useCallback } from 'react'
import { fetchHealingHistory, type HealingRecord } from '../api/healingApi'

export default function HealingHistory() {
  const [records, setRecords] = useState<HealingRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('ALL')
  const [selected, setSelected] = useState<HealingRecord | null>(null)

  const load = useCallback(async () => {
    try { setRecords(await fetchHealingHistory(100)) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const filtered = filter === 'ALL' ? records : records.filter(r => r.decision === filter)

  const decisionClass: Record<string,string> = {
    AUTO_HEAL: 'badge-auto', MANUAL_REVIEW: 'badge-manual', FAIL: 'badge-fail'
  }
  const levelClass: Record<string,string> = {
    HIGH: 'badge-high', MEDIUM: 'badge-medium', LOW: 'badge-low'
  }
  const scoreColor = (s: number) => s >= 85 ? '#22c55e' : s >= 60 ? '#f59e0b' : '#ef4444'

  return (
    <>
      <div className="topbar">
        <div>
          <div className="topbar-title">Healing History</div>
          <div className="topbar-sub">{filtered.length} of {records.length} records</div>
        </div>
        <div className="topbar-actions">
          {['ALL','AUTO_HEAL','MANUAL_REVIEW','FAIL'].map(f => (
            <button key={f} id={`filter-${f.toLowerCase()}`}
              onClick={() => setFilter(f)}
              style={{
                padding:'6px 12px', borderRadius:8, border:'1px solid',
                borderColor: filter===f ? '#6c63ff' : '#1e2540',
                background: filter===f ? 'rgba(108,99,255,0.15)' : 'transparent',
                color: filter===f ? '#6c63ff' : '#64748b',
                fontSize:'0.78rem', fontWeight:600, cursor:'pointer', fontFamily:'Inter,sans-serif'
              }}>
              {f}
            </button>
          ))}
          <button id="refresh-history" className="refresh-btn" onClick={load}>↻ Refresh</button>
        </div>
      </div>

      <div className="page-content">
        {loading ? (
          <div className="skeleton" style={{height:400,borderRadius:18}} />
        ) : filtered.length === 0 ? (
          <div className="empty-state"><div className="icon">📋</div><p>No healing records found. Run Playwright tests to populate this view.</p></div>
        ) : (
          <div style={{display:'grid',gridTemplateColumns:selected?'1fr 360px':'1fr',gap:16}}>
            <div className="table-card">
              <table>
                <thead>
                  <tr>
                    <th>Test Name</th><th>Original Locator</th><th>Healed Locator</th>
                    <th>Score</th><th>Level</th><th>Decision</th><th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(r => (
                    <tr key={r.healing_id} onClick={() => setSelected(r)}
                        style={{cursor:'pointer',background:selected?.healing_id===r.healing_id?'rgba(108,99,255,0.06)':''}}>
                      <td style={{maxWidth:160,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>
                        {r.test_name ?? <span style={{color:'#64748b'}}>—</span>}
                      </td>
                      <td><span className="mono" style={{color:'#ef4444'}}>{r.original_locator}</span></td>
                      <td><span className="mono" style={{color:'#22c55e'}}>{r.healed_locator ?? '—'}</span></td>
                      <td>
                        <div className="score-bar">
                          <div className="score-track">
                            <div className="score-fill" style={{width:`${r.confidence_score}%`,background:scoreColor(r.confidence_score)}} />
                          </div>
                          <span className="score-text" style={{color:scoreColor(r.confidence_score)}}>{r.confidence_score.toFixed(1)}</span>
                        </div>
                      </td>
                      <td><span className={`badge ${levelClass[r.confidence_level]}`}>{r.confidence_level}</span></td>
                      <td><span className={`badge ${decisionClass[r.decision]}`}>{r.decision}</span></td>
                      <td><span style={{fontSize:'0.72rem',color:'#64748b'}}>{new Date(r.timestamp).toLocaleString()}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {selected && (
              <div className="chart-card" style={{position:'sticky',top:64,alignSelf:'start'}}>
                <div className="card-header">
                  <span className="card-title">Score Breakdown</span>
                  <button onClick={() => setSelected(null)} style={{background:'none',border:'none',color:'#64748b',cursor:'pointer',fontSize:'1.1rem'}}>✕</button>
                </div>
                <div style={{marginBottom:12}}>
                  <div style={{fontSize:'0.72rem',color:'#64748b'}}>Healing ID</div>
                  <div style={{fontFamily:'monospace',fontSize:'0.72rem',color:'#6c63ff',wordBreak:'break-all'}}>{selected.healing_id}</div>
                </div>
                {selected.score_breakdown ? (
                  Object.entries(selected.score_breakdown).map(([k, v]) => (
                    <div key={k} style={{marginBottom:10}}>
                      <div style={{display:'flex',justifyContent:'space-between',marginBottom:4}}>
                        <span style={{fontSize:'0.75rem',color:'#64748b'}}>{k.replace(/_/g,' ')}</span>
                        <span style={{fontSize:'0.75rem',fontWeight:700,color:scoreColor(v as number)}}>{(v as number).toFixed(1)}</span>
                      </div>
                      <div className="score-track">
                        <div className="score-fill" style={{width:`${v}%`,background:scoreColor(v as number)}} />
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{color:'#64748b',fontSize:'0.82rem'}}>No breakdown available</div>
                )}
                <div style={{marginTop:16,padding:'12px',background:'rgba(0,0,0,0.2)',borderRadius:8}}>
                  <div style={{fontSize:'0.72rem',color:'#64748b',marginBottom:4}}>Failure Reason</div>
                  <div style={{fontSize:'0.75rem',wordBreak:'break-word'}}>{selected.failure_reason || '—'}</div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  )
}
