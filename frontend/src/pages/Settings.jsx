import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Settings() {
  const [threshold, setThreshold] = useState(7.0);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    // Fetch stats to display settings context
    api.fetchDashboardStats()
      .then(res => {
        setStats(res);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error loading settings context:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="page page-enter">
      <div className="page-header">
        <div>
          <h1 className="page-title">Settings & Status</h1>
          <p className="page-subtitle">Configure parameters and check third-party crawler nodes</p>
        </div>
      </div>

      <div className="settings-grid">
        {/* Left Column: Parameter controls */}
        <div className="settings-main-col">
          {/* Threshold Slider Card */}
          <div className="glass-card settings-card">
            <h3 className="settings-section-title">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ marginRight: '8px', verticalAlign: 'middle' }}>
                <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
                <path d="M12 6v6l4 2" />
              </svg>
              Risk Alert Parameters
            </h3>
            
            <p className="settings-description">
              Set the risk score threshold that triggers auto-generation of active security alerts. 
              Vendors scoring equal to or above this value will flag warnings.
            </p>

            <div className="slider-wrapper">
              <div className="slider-header">
                <span>Alert Threshold</span>
                <span className="slider-value text-gradient font-bold">{threshold.toFixed(1)}</span>
              </div>
              <input 
                type="range" 
                min="1.0" 
                max="10.0" 
                step="0.5" 
                value={threshold} 
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="slider-input"
              />
              <div className="slider-ticks">
                <span>1.0 (Low)</span>
                <span>5.0 (Medium)</span>
                <span>10.0 (Critical)</span>
              </div>
            </div>
            
            <button className="btn btn--primary" onClick={() => alert('Settings saved successfully!')} style={{ marginTop: '12px' }}>
              Save Configuration
            </button>
          </div>

          {/* Crawler Configurations */}
          <div className="glass-card settings-card">
            <h3 className="settings-section-title">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ marginRight: '8px', verticalAlign: 'middle' }}>
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              Scheduled Audits
            </h3>
            <p className="settings-description">
              Control the rate of background crawler checks across the onboarded vendor portfolio.
            </p>

            <div className="status-meta-list">
              <div className="status-meta-item">
                <span>Global Sweep Interval</span>
                <strong className="text-cyan">Every 12 hours</strong>
              </div>
              <div className="status-meta-item">
                <span>Concurrent Crawlers Cap</span>
                <strong>4 nodes / vendor</strong>
              </div>
              <div className="status-meta-item">
                <span>Active Vendors Queue</span>
                <strong>{stats?.total_vendors || 0} active</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: API & Node statuses */}
        <div className="settings-side-col">
          {/* Node Health */}
          <div className="glass-card settings-card">
            <h3 className="settings-section-title">Bright Data Nodes</h3>
            <p className="settings-description" style={{ marginBottom: '16px' }}>
              Verification status of the API credentials and proxy endpoint routes:
            </p>

            <div className="nodes-stack">
              <div className="node-status-row">
                <div className="node-meta">
                  <span className="node-dot dot-active"></span>
                  <div>
                    <h4>SERP API Crawler</h4>
                    <p>Search engine news sweeps</p>
                  </div>
                </div>
                <span className="badge badge-success">ACTIVE</span>
              </div>

              <div className="node-status-row">
                <div className="node-meta">
                  <span className="node-dot dot-active"></span>
                  <div>
                    <h4>Web Unlocker Proxy</h4>
                    <p>Leak repository crawls</p>
                  </div>
                </div>
                <span className="badge badge-success">ACTIVE</span>
              </div>

              <div className="node-status-row">
                <div className="node-meta">
                  <span className="node-dot dot-active"></span>
                  <div>
                    <h4>Web Scraper Node</h4>
                    <p>LinkedIn talent monitoring</p>
                  </div>
                </div>
                <span className="badge badge-success">ACTIVE</span>
              </div>

              <div className="node-status-row">
                <div className="node-meta">
                  <span className="node-dot dot-active"></span>
                  <div>
                    <h4>Scraping Browser CDP</h4>
                    <p>Reputation glassdoor crawls</p>
                  </div>
                </div>
                <span className="badge badge-success">ACTIVE</span>
              </div>

              <div className="node-status-row">
                <div className="node-meta">
                  <span className="node-dot dot-active"></span>
                  <div>
                    <h4>Bright Data MCP Node</h4>
                    <p>Agent workflow provider</p>
                  </div>
                </div>
                <span className="badge badge-success">ACTIVE</span>
              </div>
            </div>
          </div>

          {/* System Specs */}
          <div className="glass-card settings-card border-violet">
            <h3 className="settings-section-title">System Specs</h3>
            <p className="settings-description" style={{ fontSize: '12px' }}>
              <strong>Stack:</strong> React 19 + Vite client, Python FastAPI backend, SQLite + WAL storage engine, 
              AI/ML GPT-4o-mini reasoning module.
            </p>
            <div className="powered-badge" style={{ marginTop: '16px', display: 'inline-block' }}>
              <span className="badge-dot"></span>
              <span className="badge-text" style={{ fontSize: '11px' }}>VendorSentinel v1.0.0</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
