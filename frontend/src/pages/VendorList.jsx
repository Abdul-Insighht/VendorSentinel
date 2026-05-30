import React, { useEffect, useState } from 'react';
import api from '../services/api';
import VendorCard from '../components/VendorCard';

export default function VendorList() {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Search & Filter
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSensitivity, setSelectedSensitivity] = useState('all');

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    website_url: '',
    category: 'general',
    data_sensitivity: 'medium',
    description: ''
  });

  const loadVendors = async () => {
    try {
      const data = await api.fetchVendors();
      setVendors(data || []);
      setError(null);
    } catch (err) {
      console.error("Error loading vendors:", err);
      setError("Failed to fetch vendors list.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVendors();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddVendorSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.domain) return;
    
    setSubmitting(true);
    try {
      await api.createVendor(formData);
      // Reset form & state
      setFormData({
        name: '',
        domain: '',
        website_url: '',
        category: 'general',
        data_sensitivity: 'medium',
        description: ''
      });
      setShowModal(false);
      await loadVendors();
    } catch (err) {
      console.error("Failed to add vendor:", err);
      alert("Error adding vendor: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // Filter vendors based on criteria
  const filteredVendors = vendors.filter(vendor => {
    const matchesSearch = 
      vendor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vendor.domain.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = 
      selectedCategory === 'all' || 
      vendor.category?.toLowerCase() === selectedCategory.toLowerCase();
    
    const matchesSensitivity = 
      selectedSensitivity === 'all' || 
      vendor.data_sensitivity?.toLowerCase() === selectedSensitivity.toLowerCase();

    return matchesSearch && matchesCategory && matchesSensitivity;
  });

  if (loading) {
    return (
      <div className="loading-center">
        <div className="spinner"></div>
        <span>Retrieving vendor directory ...</span>
      </div>
    );
  }

  return (
    <div className="page page-enter">
      <div className="page-header">
        <div>
          <h1 className="page-title">Vendor Directory</h1>
          <p className="page-subtitle">Add and manage third-party vendor connections and profiles</p>
        </div>
        <button className="btn btn--primary" onClick={() => setShowModal(true)}>
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ marginRight: '8px' }}>
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Add Vendor
        </button>
      </div>

      {error && (
        <div className="alert-banner border-critical" style={{ marginBottom: '24px' }}>
          <div className="alert-banner-body">
            <span style={{ color: 'var(--risk-critical)' }}>⚠️ {error}</span>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="filters-bar glass-card">
        <div className="search-input-wrapper">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="var(--text-muted)" strokeWidth="2" className="search-icon">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input 
            type="text" 
            placeholder="Search vendors by name or domain..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-dropdowns">
          <div className="select-wrapper">
            <select 
              value={selectedCategory} 
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Categories</option>
              <option value="cloud">Cloud Infrastructure</option>
              <option value="identity">Identity & Access</option>
              <option value="payment">Payment & Finance</option>
              <option value="infrastructure">IT Infrastructure</option>
              <option value="saas">SaaS Applications</option>
              <option value="communication">Communication</option>
              <option value="analytics">Data & Analytics</option>
              <option value="general">General</option>
            </select>
          </div>

          <div className="select-wrapper">
            <select 
              value={selectedSensitivity} 
              onChange={(e) => setSelectedSensitivity(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Sensitivities</option>
              <option value="low">Low Sensitivity</option>
              <option value="medium">Medium Sensitivity</option>
              <option value="high">High Sensitivity</option>
              <option value="critical">Critical Sensitivity</option>
            </select>
          </div>
        </div>
      </div>

      {filteredVendors.length === 0 ? (
        <div className="empty-state glass-card">
          <div className="empty-icon">🛡️</div>
          <h2>No matching vendors found</h2>
          <p>Try refining your search keyword or clearing the filters.</p>
          <button 
            className="btn btn--ghost"
            onClick={() => {
              setSearchTerm('');
              setSelectedCategory('all');
              setSelectedSensitivity('all');
            }}
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="dashboard-vendors-grid">
          {filteredVendors.map(vendor => (
            <VendorCard key={vendor.id} vendor={vendor} />
          ))}
        </div>
      )}

      {/* Modern High-End Form Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content glass-card page-enter">
            <div className="modal-header">
              <h3>Onboard Third-Party Vendor</h3>
              <button className="modal-close-btn" onClick={() => setShowModal(false)}>
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            
            <form onSubmit={handleAddVendorSubmit}>
              <div className="form-group">
                <label htmlFor="name">Company Name</label>
                <input 
                  type="text" 
                  id="name" 
                  name="name" 
                  required
                  placeholder="e.g. Acme Corp"
                  value={formData.name}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-row">
                <div className="form-group flex-1">
                  <label htmlFor="domain">Primary Domain</label>
                  <input 
                    type="text" 
                    id="domain" 
                    name="domain" 
                    required
                    placeholder="e.g. acme.com"
                    value={formData.domain}
                    onChange={handleInputChange}
                  />
                </div>
                
                <div className="form-group flex-1">
                  <label htmlFor="website_url">Website URL</label>
                  <input 
                    type="url" 
                    id="website_url" 
                    name="website_url" 
                    placeholder="e.g. https://acme.com"
                    value={formData.website_url}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group flex-1">
                  <label htmlFor="category">Category</label>
                  <div className="select-wrapper">
                    <select 
                      id="category" 
                      name="category"
                      value={formData.category}
                      onChange={handleInputChange}
                    >
                      <option value="general">General</option>
                      <option value="cloud">Cloud Infrastructure</option>
                      <option value="identity">Identity & Access</option>
                      <option value="payment">Payment & Finance</option>
                      <option value="infrastructure">IT Infrastructure</option>
                      <option value="saas">SaaS Applications</option>
                      <option value="communication">Communication</option>
                      <option value="analytics">Data & Analytics</option>
                    </select>
                  </div>
                </div>

                <div className="form-group flex-1">
                  <label htmlFor="data_sensitivity">Data Sensitivity</label>
                  <div className="select-wrapper">
                    <select 
                      id="data_sensitivity" 
                      name="data_sensitivity"
                      value={formData.data_sensitivity}
                      onChange={handleInputChange}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="description">Vendor Description</label>
                <textarea 
                  id="description" 
                  name="description" 
                  rows="3"
                  placeholder="Provide a brief explanation of what services this vendor handles and what data they can access..."
                  value={formData.description}
                  onChange={handleInputChange}
                ></textarea>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn btn--ghost" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn--primary" disabled={submitting}>
                  {submitting ? 'Creating Profile...' : 'Save & Onboard'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
