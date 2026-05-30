import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import StatsGrid from '../components/StatsGrid';
import VendorCard from '../components/VendorCard';
import AlertBanner from '../components/AlertBanner';

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [vendors, setVendors] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      const [statsRes, vendorsRes, alertsRes] = await Promise.all([
        api.fetchDashboardStats(),
        api.fetchVendors(),
        api.fetchAlerts()
      ]);
      setStats(statsRes);
      setVendors(vendorsRes || []);
      setAlerts(alertsRes || []);
      setError(null);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
      setError("Failed to load dashboard data. Please make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleDismissAlert = async (alertId) => {
    try {
      await api.markAlertRead(alertId);
      // Refresh local state immediately
      setAlerts(prev => prev.filter(a => a.id !== alertId));
      if (stats) {
        setStats(prev => ({
          ...prev,
          unread_alerts: Math.max(0, prev.unread_alerts - 1)
        }));
      }
    } catch (err) {
      console.error("Failed to dismiss alert:", err);
    }
  };

  if (loading) {
    return (
      <div className="loading-center">
        <div className="spinner"></div>
        <span>Analyzing vendor security signals ...</span>
      </div>
    );
  }

  return (
    <div className="page page-enter">
      <div className="page-header">
        <div>
          <h1 className="page-title">Risk Dashboard</h1>
          <p className="page-subtitle">Real-time threat intelligence and vendor risk analysis</p>
        </div>
        <button className="btn btn--primary" onClick={() => navigate('/vendors')}>
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ marginRight: '8px' }}>
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Manage Vendors
        </button>
      </div>

      {error && (
        <div className="alert-banner border-critical" style={{ marginBottom: '24px' }}>
          <div className="alert-banner-body">
            <span style={{ color: 'var(--risk-critical)' }}>⚠️ {error}</span>
          </div>
        </div>
      )}

      <StatsGrid stats={stats} />

      {vendors.length === 0 ? (
        <div className="empty-state glass-card">
          <div className="empty-icon">🛡️</div>
          <h2>No Vendors Monitored</h2>
          <p>Get started by adding your first third-party vendor to begin scanning for risks and data breaches.</p>
          <button className="btn btn--primary" onClick={() => navigate('/vendors')}>
            Add First Vendor
          </button>
        </div>
      ) : (
        <div className="dashboard-grid">
          {/* Top Vendors column */}
          <div>
            <div className="flex-between mb-md">
              <h2 className="section-title">High-Risk Portfolios</h2>
              <span className="badge badge--neutral">{vendors.length} vendors total</span>
            </div>
            <div className="dashboard-vendors-grid">
              {vendors.map(vendor => (
                <VendorCard key={vendor.id} vendor={vendor} />
              ))}
            </div>
          </div>

          {/* Active Alerts column */}
          <div>
            <div className="flex-between mb-md">
              <h2 className="section-title">Security Alerts</h2>
              {alerts.length > 0 && <span className="badge badge--critical">{alerts.length} active</span>}
            </div>
            <div className="dashboard-alerts">
              {alerts.length === 0 ? (
                <div className="empty-state glass-card">
                  <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="var(--text-muted)" strokeWidth="1.5" style={{ marginBottom: '12px' }}>
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                    <polyline points="22 4 12 14.01 9 11.01" />
                  </svg>
                  <span>No unresolved security alerts</span>
                </div>
              ) : (
                alerts.map(alert => (
                  <AlertBanner 
                    key={alert.id} 
                    alert={alert} 
                    onDismiss={handleDismissAlert} 
                  />
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
