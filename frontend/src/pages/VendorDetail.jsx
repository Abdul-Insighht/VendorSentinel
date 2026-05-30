import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import RiskGauge from '../components/RiskGauge';
import SignalCard from '../components/SignalCard';

export default function VendorDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [vendor, setVendor] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('all');

  const loadReport = async () => {
    try {
      setError(null);
      // Fetch full vendor report
      const data = await api.fetchVendorReport(id);
      setVendor(data.vendor);
      setReport(data);
    } catch (err) {
      console.error("Error loading vendor report:", err);
      setError("Failed to retrieve vendor profile or scanning logs.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
  }, [id]);

  const handleScanNow = async () => {
    setScanning(true);
    try {
      await api.triggerVendorScan(id);
      // Wait a moment and fetch updated report
      // In production, you would poll or receive a socket event. 
      // For this hackathon, we wait for the scan to finish and then reload.
      setTimeout(async () => {
        await loadReport();
        setScanning(false);
      }, 5000);
    } catch (err) {
      console.error("Scan trigger failed:", err);
      setError("Failed to run vendor scan: " + err.message);
      setScanning(false);
    }
  };

  const handleDeleteVendor = async () => {
    if (!window.confirm(`Are you sure you want to offboard ${vendor?.name}? This will permanently delete their risk history.`)) {
      return;
    }
    
    try {
      await api.deleteVendor(id);
      navigate('/vendors');
    } catch (err) {
      console.error("Failed to delete vendor:", err);
      alert("Error deleting vendor: " + err.message);
    }
  };

  if (loading) {
    return (
      <div className="loading-center">
        <div className="spinner"></div>
        <span>Compiling vendor risk intelligence report ...</span>
      </div>
    );
  }

  if (error && !vendor) {
    return (
      <div className="page page-enter">
        <button className="btn btn--ghost" onClick={() => navigate('/vendors')} style={{ marginBottom: '16px' }}>
          ← Back to Directory
        </button>
        <div className="empty-state glass-card">
          <div className="empty-icon">⚠️</div>
          <h2>Error Loading Profile</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  // Group signals by type
  const signals = report?.signals || [];
  const latestRisk = report?.risk_history?.[0] || {};
  
  const newsSignals = signals.filter(s => s.signal_type.toLowerCase() === 'news' || s.signal_type.toLowerCase() === 'serp_api');
  const credSignals = signals.filter(s => s.signal_type.toLowerCase() === 'credentials' || s.signal_type.toLowerCase() === 'web_unlocker');
  const hiringSignals = signals.filter(s => s.signal_type.toLowerCase() === 'hiring' || s.signal_type.toLowerCase() === 'web_scraper');
  const healthSignals = signals.filter(s => s.signal_type.toLowerCase() === 'health' || s.signal_type.toLowerCase() === 'scraping_browser');

  const getFilteredSignals = () => {
    switch (activeTab) {
      case 'news': return newsSignals;
      case 'credentials': return credSignals;
      case 'hiring': return hiringSignals;
      case 'health': return healthSignals;
      default: return signals;
    }
  };

  const activeSignals = getFilteredSignals();

  // Determine risk level text and style class
  const currentScore = vendor?.risk_score || 0;
  let riskClass = 'risk-low';
  if (currentScore >= 7.0) {
    riskClass = 'risk-critical';
  } else if (currentScore >= 5.0) {
    riskClass = 'risk-high';
  } else if (currentScore >= 3.0) {
    riskClass = 'risk-medium';
  }

  return (
    <div className="page page-enter">
      {/* Detail Header & Navigation */}
      <div className="detail-navigation">
        <button className="btn btn--ghost btn--sm" onClick={() => navigate('/vendors')}>
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ marginRight: '6px' }}>
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
          Back to Directory
        </button>

        <div className="detail-actions">
          <button 
            className="btn btn--danger btn--sm"
            onClick={handleDeleteVendor}
            disabled={scanning}
          >
            Offboard Vendor
          </button>
          
          <button 
            className={`btn ${scanning ? 'btn--ghost' : 'btn--primary'}`}
            onClick={handleScanNow}
            disabled={scanning}
          >
            {scanning ? (
              <>
                <div className="spinner spinner-sm" style={{ marginRight: '8px' }}></div>
                Scanning in progress...
              </>
            ) : (
              <>
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ marginRight: '8px' }}>
                  <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
                </svg>
                Scan Profile Now
              </>
            )}
          </button>
        </div>
      </div>

      {scanning && (
        <div className="scan-progress-banner glass-card pulse-cyan" style={{ marginBottom: '24px' }}>
          <div className="scan-progress-content">
            <div className="radar-ping"></div>
            <div>
              <h4>Bright Data Search Agents Activated</h4>
              <p>Crawling news portals, leaked repositories, job boards, and organizational review pages in real-time...</p>
            </div>
          </div>
          <div className="scan-progress-bar-wrapper">
            <div className="scan-progress-bar-fill"></div>
          </div>
        </div>
      )}

      {/* Main Vendor Profile Header Card */}
      <div className="vendor-profile-header glass-card">
        <div className="profile-details-column">
          <div className="profile-badge-row">
            <span className="badge category-badge">{vendor?.category}</span>
            <span className={`badge sensitivity-badge sensitivity-${vendor?.data_sensitivity?.toLowerCase()}`}>
              {vendor?.data_sensitivity} Sensitivity
            </span>
          </div>
          <h1 className="profile-title">{vendor?.name}</h1>
          <span className="profile-domain">{vendor?.domain}</span>
          
          {vendor?.website_url && (
            <a href={vendor.website_url} target="_blank" rel="noopener noreferrer" className="profile-website-link">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '6px' }}>
                <circle cx="12" cy="12" r="10" />
                <line x1="2" y1="12" x2="22" y2="12" />
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              </svg>
              {vendor.website_url}
            </a>
          )}

          {vendor?.description && <p className="profile-description">{vendor.description}</p>}
        </div>

        <div className="profile-gauge-column">
          <RiskGauge score={currentScore} size={160} />
        </div>
      </div>

      {/* AI Analysis and Recommendations */}
      {latestRisk.id ? (
        <div className="ai-analysis-grid">
          {/* AI Reasoning card */}
          <div className="glass-card ai-reasoning-card border-violet">
            <div className="ai-header">
              <div className="ai-icon">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
                </svg>
              </div>
              <h3>AI Threat Assessment</h3>
            </div>
            <p className="ai-text">{latestRisk.ai_reasoning || 'No analysis log recorded for this scan.'}</p>
          </div>

          {/* Recommended Actions card */}
          <div className="glass-card recommended-actions-card">
            <div className="ai-header">
              <div className="ai-icon icon-action">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="9 11 12 14 22 4" />
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                </svg>
              </div>
              <h3>Risk Mitigation Playbook</h3>
            </div>
            <ul className="actions-list">
              {latestRisk.recommended_actions 
                ? latestRisk.recommended_actions.split('\n').filter(line => line.trim()).map((action, index) => (
                    <li key={index} className="action-item">
                      <span className="action-bullet"></span>
                      <span className="action-text">{action.replace(/^[-\*\d\.\s]+/, '')}</span>
                    </li>
                  ))
                : <li className="action-item">No actions recommended. Vendor score is within acceptable limits.</li>
              }
            </ul>
          </div>
        </div>
      ) : (
        <div className="glass-card empty-ai-state" style={{ marginBottom: '24px' }}>
          <div className="empty-ai-icon">✨</div>
          <h3>AI Analysis Pending</h3>
          <p>Please click "Scan Profile Now" to activate Bright Data threat gathering agents and generate a risk report.</p>
        </div>
      )}

      {/* Threat signals listing with Tab Navigation */}
      <div className="signals-section">
        <div className="section-tabs-header">
          <h2 className="section-title">Collected Threat Signals</h2>
          
          <div className="tab-navigation">
            <button className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`} onClick={() => setActiveTab('all')}>
              All Signals ({signals.length})
            </button>
            <button className={`tab-btn ${activeTab === 'news' ? 'active' : ''}`} onClick={() => setActiveTab('news')}>
              📰 News ({newsSignals.length})
            </button>
            <button className={`tab-btn ${activeTab === 'credentials' ? 'active' : ''}`} onClick={() => setActiveTab('credentials')}>
              🔑 Leaks ({credSignals.length})
            </button>
            <button className={`tab-btn ${activeTab === 'hiring' ? 'active' : ''}`} onClick={() => setActiveTab('hiring')}>
              👥 Hiring ({hiringSignals.length})
            </button>
            <button className={`tab-btn ${activeTab === 'health' ? 'active' : ''}`} onClick={() => setActiveTab('health')}>
              🏢 Health ({healthSignals.length})
            </button>
          </div>
        </div>

        <div className="signals-stack">
          {activeSignals.length === 0 ? (
            <div className="empty-signals-state glass-card">
              <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="var(--text-muted)" strokeWidth="1">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <h3>No signals in this category</h3>
              <p>Either the last scan was clean, or you haven't triggered a scan for this vendor yet.</p>
            </div>
          ) : (
            activeSignals.map((signal, idx) => (
              <SignalCard key={signal.id || idx} signal={signal} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
