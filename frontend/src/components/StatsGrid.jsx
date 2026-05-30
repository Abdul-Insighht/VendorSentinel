import React from 'react';

export default function StatsGrid({ stats }) {
  const { total_vendors = 0, average_risk_score = 0, critical_vendors = 0, unread_alerts = 0 } = stats || {};

  // Determine class and color based on average risk score
  let riskColorClass = 'risk-color--low';
  if (average_risk_score >= 7.0) {
    riskColorClass = 'risk-color--critical';
  } else if (average_risk_score >= 5.0) {
    riskColorClass = 'risk-color--high';
  } else if (average_risk_score >= 3.0) {
    riskColorClass = 'risk-color--medium';
  }

  return (
    <div className="stats-grid">
      {/* Total Vendors */}
      <div className="stat-card stat-card--cyan glass-card">
        <div className="stat-icon stat-icon--cyan">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
            <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
            <line x1="6" y1="6" x2="6.01" y2="6" />
            <line x1="6" y1="18" x2="6.01" y2="18" />
          </svg>
        </div>
        <div className="stat-info">
          <span className="stat-value">{total_vendors}</span>
          <span className="stat-label">Total Vendors</span>
        </div>
      </div>

      {/* Average Risk Score */}
      <div className="stat-card stat-card--violet glass-card">
        <div className="stat-icon stat-icon--violet">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        </div>
        <div className="stat-info">
          <span className={`stat-value ${riskColorClass}`}>{average_risk_score.toFixed(1)}</span>
          <span className="stat-label">Average Risk</span>
        </div>
      </div>

      {/* Critical Vendors */}
      <div className="stat-card stat-card--red glass-card">
        <div className="stat-icon stat-icon--red">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <div className="stat-info">
          <span className="stat-value risk-color--critical">{critical_vendors}</span>
          <span className="stat-label">Critical Risks</span>
        </div>
      </div>

      {/* Active Alerts */}
      <div className="stat-card stat-card--amber glass-card">
        <div className="stat-icon stat-icon--amber">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
        </div>
        <div className="stat-info">
          <span className="stat-value risk-color--medium">{unread_alerts}</span>
          <span className="stat-label">Unread Alerts</span>
        </div>
      </div>
    </div>
  );
}
