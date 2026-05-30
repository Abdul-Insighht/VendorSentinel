import React, { useState } from 'react';

export default function SignalCard({ signal }) {
  const [expanded, setExpanded] = useState(false);
  const { signal_type, severity, title, description, source_url, found_at, raw_data } = signal;

  // Icons based on signal type
  const getSignalIcon = () => {
    switch (signal_type.toLowerCase()) {
      case 'news':
      case 'serp_api':
        return (
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
            <path d="M16 8h2" />
            <path d="M16 12h2" />
            <path d="M16 16h2" />
            <path d="M6 8h6v8H6z" />
          </svg>
        );
      case 'credentials':
      case 'web_unlocker':
        return (
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        );
      case 'hiring':
      case 'web_scraper':
        return (
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
        );
      case 'health':
      case 'scraping_browser':
        return (
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
        );
      default:
        return (
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
        );
    }
  };

  // Format date
  const formattedDate = found_at 
    ? new Date(found_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    : '';

  // Parse raw data if string
  let parsedRaw = raw_data;
  if (typeof raw_data === 'string') {
    try {
      parsedRaw = JSON.parse(raw_data);
    } catch (_) {}
  }

  const severityLower = (severity || 'info').toLowerCase();

  return (
    <div className={`signal-card glass-card border-${severityLower}`}>
      <div className="signal-card-header">
        <div className="signal-title-group">
          <div className={`signal-type-icon icon-${signal_type.toLowerCase()}`}>
            {getSignalIcon()}
          </div>
          <div>
            <h4 className="signal-title">{title}</h4>
            <span className="signal-date">{formattedDate}</span>
          </div>
        </div>
        <span className={`signal-severity severity-${severityLower}`}>
          {severity || 'Info'}
        </span>
      </div>

      <div className="signal-card-body">
        <p className="signal-description">{description}</p>
        
        {source_url && (
          <div className="signal-source">
            <span className="source-label">Source URL:</span>
            <a href={source_url} target="_blank" rel="noopener noreferrer" className="source-link">
              {source_url}
            </a>
          </div>
        )}

        {parsedRaw && Object.keys(parsedRaw).length > 0 && (
          <div className="raw-data-section">
            <button 
              className="btn btn--ghost btn--sm raw-toggle" 
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? 'Hide Payload' : 'Show Payload'}
              <svg 
                viewBox="0 0 24 24" 
                width="14" 
                height="14" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                style={{ transform: expanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>
            {expanded && (
              <pre className="raw-json">
                <code>{JSON.stringify(parsedRaw, null, 2)}</code>
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
