import React from 'react';

export default function AlertBanner({ alert, onDismiss }) {
  const { id, vendor_name, alert_type, severity, title, message, created_at } = alert;

  // Determine class based on severity
  const severityLower = (severity || 'info').toLowerCase();
  
  // Format date
  const formattedDate = created_at
    ? new Date(created_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    : '';

  return (
    <div className={`alert-banner glass-card alert-banner--${severityLower}`}>
      <div className="alert-banner-body">
        <div className="alert-meta-group">
          <div className={`alert-severity-dot dot-${severityLower}`}></div>
          <div>
            <div className="alert-header-row">
              <span className="alert-banner-vendor">{vendor_name}</span>
              <span className="alert-banner-time">{formattedDate}</span>
            </div>
            <h4 className="alert-banner-title">{title}</h4>
            {message && <p className="alert-message">{message}</p>}
          </div>
        </div>
        <button 
          className="alert-banner-dismiss"
          onClick={() => onDismiss(id)}
          title="Mark as Read"
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
