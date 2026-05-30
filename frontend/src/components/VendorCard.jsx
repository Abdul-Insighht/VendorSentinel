import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function VendorCard({ vendor }) {
  const navigate = useNavigate();
  const { id, name, domain, category, data_sensitivity, risk_score, risk_level, last_scanned } = vendor;

  // Determine class and color based on risk score
  let riskColorClass = 'risk-low';
  if (risk_score >= 7.0) {
    riskColorClass = 'risk-critical';
  } else if (risk_score >= 5.0) {
    riskColorClass = 'risk-high';
  } else if (risk_score >= 3.0) {
    riskColorClass = 'risk-medium';
  }

  // Format last scanned date
  const formattedDate = last_scanned 
    ? new Date(last_scanned).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    : 'Never scanned';

  return (
    <div 
      className={`vendor-card glass-card glass-card-interactive`} 
      onClick={() => navigate(`/vendors/${id}`)}
      style={{ cursor: 'pointer' }}
    >
      <div className="vendor-card-header">
        <div>
          <h3 className="vendor-card-title">{name}</h3>
          <span className="vendor-card-domain">{domain}</span>
        </div>
        <div className={`risk-badge-dot ${riskColorClass}`}>
          <span className="dot"></span>
          <span className="score">{risk_score.toFixed(1)}</span>
        </div>
      </div>

      <div className="vendor-card-body">
        <div className="badge-row">
          <span className="badge category-badge">
            {category || 'General'}
          </span>
          <span className={`badge sensitivity-badge sensitivity-${(data_sensitivity || 'medium').toLowerCase()}`}>
            {data_sensitivity || 'Medium'} sensitivity
          </span>
        </div>
      </div>

      <div className="vendor-card-footer">
        <span className="last-scanned">
          <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          {formattedDate}
        </span>
        <span className="badge badge--info">
          Report →
        </span>
      </div>
    </div>
  );
}
