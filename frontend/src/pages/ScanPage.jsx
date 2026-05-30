import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function ScanPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);

  const loadHistory = async () => {
    try {
      const data = await api.fetchScanHistory();
      setHistory(data || []);
      
      // Check if any scan in progress
      const isAnyRunning = (data || []).some(scan => scan.status.toLowerCase() === 'running');
      setScanning(isAnyRunning);
      setError(null);
    } catch (err) {
      console.error("Error loading scan history:", err);
      setError("Failed to fetch scan logs.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  // Poll scan history when a scan is active
  useEffect(() => {
    let interval;
    if (scanning) {
      interval = setInterval(loadHistory, 3000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [scanning]);

  const handleTriggerFullScan = async () => {
    setScanning(true);
    try {
      await api.triggerScan();
      // Load history immediately to show the running scan
      await loadHistory();
    } catch (err) {
      console.error("Failed to trigger full scan:", err);
      setError("Failed to start full scan: " + err.message);
      setScanning(false);
    }
  };

  // Date formatter
  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="loading-center">
        <div className="spinner"></div>
        <span>Opening threat intelligence logs ...</span>
      </div>
    );
  }

  return (
    <div className="page page-enter">
      <div className="page-header">
        <div>
          <h1 className="page-title">Scan Center</h1>
          <p className="page-subtitle">Initiate manual threats scanning and view system sweep history</p>
        </div>
      </div>

      {error && (
        <div className="alert-banner border-critical" style={{ marginBottom: '24px' }}>
          <div className="alert-banner-body">
            <span style={{ color: 'var(--risk-critical)' }}>⚠️ {error}</span>
          </div>
        </div>
      )}

      {/* Main Trigger Scan Card */}
      <div className="glass-card trigger-scan-card">
        <div className="radar-section">
          <div className={`radar-container ${scanning ? 'scanning' : ''}`}>
            <div className="radar-sweep"></div>
            <div className="radar-ring r1"></div>
            <div className="radar-ring r2"></div>
            <div className="radar-ring r3"></div>
            <div className="radar-blip b1"></div>
            <div className="radar-blip b2"></div>
            <div className="radar-shield-icon">🛡️</div>
          </div>
        </div>

        <div className="radar-info-section">
          <h2>Continuous Threat Sweep</h2>
          <p>
            Triggering a system-wide threat scan initiates a multi-layered web crawl using Bright Data's 
            full infrastructure stack.
          </p>
          <ul className="radar-features-list">
            <li>
              <strong>Bright Data SERP API:</strong> Search engines monitor for latest news breaches.
            </li>
            <li>
              <strong>Bright Data Web Unlocker:</strong> Code repositories scan for exposed credentials.
            </li>
            <li>
              <strong>Bright Data Web Scraper API:</strong> Job boards check for key talent distress.
            </li>
            <li>
              <strong>Bright Data Scraping Browser:</strong> Glassdoor and corporate pages analyze reputation.
            </li>
          </ul>

          <button 
            className={`btn btn--lg ${scanning ? 'btn--ghost' : 'btn--primary'}`}
            onClick={handleTriggerFullScan}
            disabled={scanning}
            style={{ minWidth: '240px', marginTop: '12px' }}
          >
            {scanning ? (
              <>
                <div className="spinner spinner-sm" style={{ marginRight: '8px' }}></div>
                System Scan In Progress...
              </>
            ) : (
              <>
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ marginRight: '8px' }}>
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                </svg>
                Trigger System-Wide Scan
              </>
            )}
          </button>
        </div>
      </div>

      {/* Scan History Section */}
      <div className="scan-history-section">
        <div className="flex-between mb-md">
          <h2 className="section-title">Scan Log Audit</h2>
          <span className="badge badge--neutral">{history.length} sweeps recorded</span>
        </div>

        <div className="glass-card history-table-card">
          {history.length === 0 ? (
            <div className="empty-signals-state">
              <h3>No scan records found</h3>
              <p>Trigger your first system scan above to populate these logs.</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Scan UUID</th>
                    <th>Status</th>
                    <th>Vendors Swept</th>
                    <th>Findings Detected</th>
                    <th>Started At</th>
                    <th>Completed At</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map(scan => {
                    const statusLower = scan.status.toLowerCase();
                    return (
                      <tr key={scan.scan_id}>
                        <td className="uuid-cell" title={scan.scan_id}>{scan.scan_id.substring(0, 8)}...</td>
                        <td>
                          <span className={`status-badge badge-${statusLower}`}>
                            {statusLower === 'running' && <span className="running-indicator-dot"></span>}
                            {scan.status}
                          </span>
                        </td>
                        <td>{scan.vendors_scanned}</td>
                        <td>
                          <span className={`signals-count ${scan.total_signals_found > 0 ? 'risk-color--medium' : 'risk-color--low'}`}>
                            {scan.total_signals_found} signals
                          </span>
                        </td>
                        <td>{formatDate(scan.started_at)}</td>
                        <td>{formatDate(scan.completed_at)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
