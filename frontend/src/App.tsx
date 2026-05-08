import { useState } from 'react'
import Dashboard from './components/Dashboard'
import HealingHistory from './components/HealingHistory'
import ConfidenceChart from './components/ConfidenceChart'
import FailureHeatmap from './components/FailureHeatmap'
import ExecutionTimeline from './components/ExecutionTimeline'

type Page = 'dashboard' | 'history' | 'charts' | 'heatmap' | 'timeline'

const NAV = [
  { id: 'dashboard' as Page, icon: '📊', label: 'Overview' },
  { id: 'history' as Page, icon: '📋', label: 'Healing History' },
  { id: 'charts' as Page, icon: '📈', label: 'Confidence Charts' },
  { id: 'heatmap' as Page, icon: '🔥', label: 'Failure Heatmap' },
  { id: 'timeline' as Page, icon: '⏱️', label: 'Execution Timeline' },
]

export default function App() {
  const [page, setPage] = useState<Page>('dashboard')

  return (
    <div className="app-layout">
      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">🛡️</div>
          <div>
            <div className="brand-name">HealQA</div>
            <div className="brand-version">AI Self-Healing Platform v1.0</div>
          </div>
        </div>

        <div className="nav-section">
          <div className="nav-section-label">Analytics</div>
          {NAV.map(item => (
            <button
              key={item.id}
              id={`nav-${item.id}`}
              className={`nav-btn${page === item.id ? ' active' : ''}`}
              onClick={() => setPage(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
              {item.id === 'history' && <span className="nav-badge">LIVE</span>}
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="status-indicator">
            <div className="status-dot" />
            MCP Server: Online
          </div>
        </div>
      </aside>

      {/* ── Main Panel ──────────────────────────────────────────── */}
      <div className="main-panel">
        {page === 'dashboard'  && <Dashboard />}
        {page === 'history'   && <HealingHistory />}
        {page === 'charts'    && <ConfidenceChart />}
        {page === 'heatmap'   && <FailureHeatmap />}
        {page === 'timeline'  && <ExecutionTimeline />}
      </div>
    </div>
  )
}
