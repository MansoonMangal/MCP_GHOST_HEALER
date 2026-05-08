import { useEffect, useState, useCallback } from 'react'
import { fetchHealingHistory, type HealingRecord } from '../api/healingApi'

const DECISION_COLOR: Record<string, string> = {
  AUTO_HEAL: '#22c55e', MANUAL_REVIEW: '#f59e0b', FAIL: '#ef4444'
}
const DECISION_ICON: Record<string, string> = {
  AUTO_HEAL: '✅', MANUAL_REVIEW: '⚠️', FAIL: '❌'
}

export default function ExecutionTimeline() {
  const [records, setRecords] = useState<HealingRecord[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try { setRecords(await fetchHealingHistory(30)) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  // Group by test_name for timeline view
  const byTest: Record<string, HealingRecord[]> = {}
  records.forEach(r => {
    const key = r.test_name ?? 'unknown'
    if (!byTest[key]) byTest[key] = []
    byTest[key].push(r)
  })

  return (
    <>
      <div className="topbar">
        <div>
          <div className="topbar-title">Execution Timeline</div>
          <div className="topbar-sub">Healing events grouped by test, newest first</div>
        </div>
        <button id="refresh-timeline" className="refresh-btn" onClick={load}>↻ Refresh</button>
      </div>

      <div className="page-content">
        {loading ? (
          <div className="skeleton" style={{height:400,borderRadius:18}} />
        ) : records.length === 0 ? (
          <div className="empty-state"><div className="icon">⏱️</div><p>No execution data yet — run Playwright tests first</p></div>
        ) : (
          Object.entries(byTest).map(([testName, events]) => (
            <div key={testName} style={{marginBottom:24}}>
              <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:12}}>
                <div style={{width:10,height:10,borderRadius:'50%',background:'#6c63ff'}} />
                <span style={{fontWeight:700,fontSize:'0.9rem'}}>{testName}</span>
                <span style={{fontSize:'0.72rem',color:'#64748b',background:'rgba(108,99,255,0.1)',padding:'2px 8px',borderRadius:20}}>
                  {events.length} event{events.length !== 1 ? 's' : ''}
                </span>
              </div>

              <div style={{marginLeft:5,borderLeft:'2px solid #1e2540',paddingLeft:20}}>
                {events.map((r, i) => (
                  <div key={r.healing_id} style={{
                    position:'relative', marginBottom:12,
                    background:'#0f1322', border:'1px solid #1e2540',
                    borderRadius:12, padding:'14px 16px',
                  }}>
                    {/* Timeline dot */}
                    <div style={{
                      position:'absolute', left:-28, top:18,
                      width:10, height:10, borderRadius:'50%',
                      background:DECISION_COLOR[r.decision] ?? '#6c63ff',
                      border:'2px solid #0f1322',
                    }} />

                    <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:8}}>
                      <div style={{display:'flex',gap:8,alignItems:'center'}}>
                        <span>{DECISION_ICON[r.decision]}</span>
                        <span style={{fontSize:'0.82rem',fontWeight:600,color:DECISION_COLOR[r.decision]}}>{r.decision}</span>
                        <span style={{fontSize:'0.72rem',color:'#64748b'}}>
                          score: <strong style={{color:'#e8eaf6'}}>{r.confidence_score.toFixed(1)}</strong>
                        </span>
                      </div>
                      <span style={{fontSize:'0.7rem',color:'#64748b'}}>{new Date(r.timestamp).toLocaleString()}</span>
                    </div>

                    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
                      <div>
                        <div style={{fontSize:'0.65rem',color:'#64748b',marginBottom:2}}>ORIGINAL</div>
                        <code style={{fontSize:'0.78rem',color:'#ef4444'}}>{r.original_locator}</code>
                      </div>
                      <div>
                        <div style={{fontSize:'0.65rem',color:'#64748b',marginBottom:2}}>HEALED</div>
                        <code style={{fontSize:'0.78rem',color:'#22c55e'}}>{r.healed_locator ?? '—'}</code>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </>
  )
}
