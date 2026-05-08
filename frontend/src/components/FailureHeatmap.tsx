import { useEffect, useState, useCallback } from 'react'
import { fetchConfidenceReport, type ConfidenceReport } from '../api/healingApi'

export default function FailureHeatmap() {
  const [report, setReport] = useState<ConfidenceReport | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try { setReport(await fetchConfidenceReport()) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const maxCount = Math.max(...(report?.most_unstable_locators?.map(l => l.failure_count) ?? [1]), 1)

  return (
    <>
      <div className="topbar">
        <div>
          <div className="topbar-title">Failure Heatmap</div>
          <div className="topbar-sub">Most frequently failing locators — candidates for refactoring</div>
        </div>
        <button id="refresh-heatmap" className="refresh-btn" onClick={load}>↻ Refresh</button>
      </div>

      <div className="page-content">
        <div className="heatmap-card">
          <div className="card-header">
            <span className="card-title">🔥 Most Unstable Locators</span>
            <span className="card-badge">Top {report?.most_unstable_locators?.length ?? 0}</span>
          </div>

          {loading ? (
            <div className="skeleton" style={{height:300,borderRadius:12}} />
          ) : !report?.most_unstable_locators?.length ? (
            <div className="empty-state"><div className="icon">🔥</div><p>No failures recorded yet. Run tests to populate.</p></div>
          ) : (
            report.most_unstable_locators.map((item, i) => (
              <div key={item.locator} className="heatmap-item">
                <div className="heatmap-rank">#{i + 1}</div>
                <span className="heatmap-locator">{item.locator}</span>
                <div className="heatmap-bar-wrap">
                  <div className="heatmap-bar" style={{width:`${(item.failure_count / maxCount) * 100}%`}} />
                </div>
                <span className="heatmap-count">{item.failure_count}×</span>
              </div>
            ))
          )}
        </div>

        {/* ── Insight panel ─────────────────────────────────── */}
        {(report?.most_unstable_locators?.length ?? 0) > 0 && (
          <div className="chart-card">
            <div className="card-header">
              <span className="card-title">💡 Engineering Insights</span>
            </div>
            <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:12}}>
              {[
                {icon:'🎯',title:'Use data-testid',desc:'Add data-testid attributes to critical elements — most resilient to UI changes'},
                {icon:'🏷️',title:'Prefer aria-label',desc:'Semantic attributes are stable across redesigns and improve accessibility'},
                {icon:'📝',title:'Avoid class selectors',desc:'CSS classes change frequently during styling iterations — use ID or name instead'},
              ].map(({icon,title,desc}) => (
                <div key={title} style={{background:'rgba(0,0,0,0.2)',borderRadius:12,padding:'16px'}}>
                  <div style={{fontSize:'1.5rem',marginBottom:8}}>{icon}</div>
                  <div style={{fontWeight:700,marginBottom:4,fontSize:'0.85rem'}}>{title}</div>
                  <div style={{fontSize:'0.75rem',color:'#64748b',lineHeight:1.5}}>{desc}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  )
}
