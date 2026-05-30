import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Welcome() {
  const navigate = useNavigate();

  return (
    <div className="welcome-page">
      {/* Dynamic Gold Dust Background Animation via Inline Styles */}
      <style>{`
        .welcome-page {
          min-height: 100vh;
          background: radial-gradient(circle at 50% 50%, #1c1813 0%, #0d0c0a 100%);
          color: var(--text-ivory);
          font-family: var(--font-display);
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 60px 24px;
          overflow-y: auto;
          position: relative;
        }

        .welcome-header {
          text-align: center;
          margin-bottom: 50px;
          max-width: 800px;
          z-index: 2;
        }

        .welcome-badge {
          display: inline-flex;
          align-items: center;
          padding: 8px 16px;
          background: rgba(220, 167, 66, 0.08);
          border: 1px solid rgba(220, 167, 66, 0.2);
          border-radius: 100px;
          color: var(--accent-gold);
          font-size: 0.85rem;
          text-transform: uppercase;
          letter-spacing: 0.15em;
          margin-bottom: 24px;
          font-weight: 600;
        }

        .welcome-title {
          font-size: 3.5rem;
          font-family: var(--font-serif);
          font-weight: 700;
          line-height: 1.1;
          color: var(--text-ivory);
          margin-bottom: 16px;
          text-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }

        .welcome-subtitle {
          font-size: 1.25rem;
          color: rgba(230, 226, 218, 0.7);
          line-height: 1.6;
          max-width: 600px;
          margin: 0 auto;
        }

        /* Call To Action Golden Button */
        .welcome-cta-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 16px 36px;
          background: linear-gradient(135deg, #dca742 0%, #b8862b 100%);
          border: 1px solid rgba(220, 167, 66, 0.3);
          border-radius: var(--radius-md);
          color: #0d0c0a;
          font-size: 1.1rem;
          font-weight: 700;
          cursor: pointer;
          transition: var(--transition-all);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          box-shadow: 0 4px 20px rgba(220, 167, 66, 0.25);
          margin-bottom: 60px;
          z-index: 2;
        }

        .welcome-cta-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 28px rgba(220, 167, 66, 0.4);
          background: linear-gradient(135deg, #e5b352 0%, #c49233 100%);
        }

        /* 3 Column Value Proposition Grid */
        .welcome-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 24px;
          width: 100%;
          max-width: 1200px;
          margin-bottom: 60px;
          z-index: 2;
        }

        .welcome-card {
          background: rgba(28, 24, 19, 0.45);
          border: 1px solid rgba(220, 167, 66, 0.1);
          backdrop-filter: blur(12px);
          border-radius: var(--radius-lg);
          padding: 32px;
          transition: var(--transition-all);
        }

        .welcome-card:hover {
          border-color: rgba(220, 167, 66, 0.25);
          transform: translateY(-4px);
        }

        .welcome-card-icon {
          font-size: 2rem;
          margin-bottom: 20px;
          color: var(--accent-gold);
        }

        .welcome-card h3 {
          font-size: 1.4rem;
          font-family: var(--font-serif);
          color: var(--text-ivory);
          margin-bottom: 12px;
        }

        .welcome-card p {
          font-size: 0.95rem;
          color: rgba(230, 226, 218, 0.65);
          line-height: 1.6;
        }

        /* Bright Data Platform Integration Cards */
        .bd-section {
          width: 100%;
          max-width: 1200px;
          text-align: center;
          margin-bottom: 60px;
          z-index: 2;
        }

        .bd-section h2 {
          font-size: 2.2rem;
          font-family: var(--font-serif);
          color: var(--text-ivory);
          margin-bottom: 30px;
        }

        .bd-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          gap: 20px;
        }

        .bd-card {
          background: rgba(13, 12, 10, 0.7);
          border: 1px solid rgba(220, 167, 66, 0.08);
          border-radius: var(--radius-md);
          padding: 24px;
          text-align: left;
        }

        .bd-card-title {
          font-size: 1.1rem;
          font-weight: 600;
          color: var(--accent-gold);
          margin-bottom: 8px;
        }

        .bd-card-desc {
          font-size: 0.9rem;
          color: rgba(230, 226, 218, 0.55);
          line-height: 1.5;
        }

        .welcome-footer {
          margin-top: auto;
          color: rgba(230, 226, 218, 0.4);
          font-size: 0.85rem;
          letter-spacing: 0.05em;
          text-transform: uppercase;
        }
      `}</style>

      {/* Header */}
      <div className="welcome-header">
        <div className="welcome-badge">
          🛡️ AI-Powered Supply-Chain Security
        </div>
        <h1 className="welcome-title">VendorSentinel</h1>
        <p className="welcome-subtitle">
          An always-on third-party risk intelligence system. Continuous web intelligence 
          crawling week-by-week warning signals before a breach ever makes the news.
        </p>
      </div>

      {/* CTA Button */}
      <button className="welcome-cta-btn" onClick={() => navigate('/dashboard')}>
        Enter Security Dashboard &rarr;
      </button>

      {/* Value Propositions Grid */}
      <div className="welcome-grid">
        <div className="welcome-card">
          <div className="welcome-card-icon">⚡</div>
          <h3>Continuous Polling vs PDFs</h3>
          <p>
            Traditional once-a-year PDF security questionnaires fail to detect live active threats. 
            VendorSentinel executes automated security sweeps every 6 hours across your entire portfolio.
          </p>
        </div>

        <div className="welcome-card">
          <div className="welcome-card-icon">🔐</div>
          <h3>Exposed Secrets Hunting</h3>
          <p>
            Bypassing complex anti-bot protection systems, we hunt GitHub public commits 
            and paste sites to locate leaked keys and passwords referencing your vendors' domains.
          </p>
        </div>

        <div className="welcome-card">
          <div className="welcome-card-icon">🤖</div>
          <h3>AI Scoring & Mitigation</h3>
          <p>
            All gathered intelligence signals (News, leaks, hiring distress, employee reviews) 
            are analyzed in real-time by a cyber-analyst AI model to generate scores, audits, and playbooks.
          </p>
        </div>
      </div>

      {/* Bright Data Section */}
      <div className="bd-section">
        <h2>Powered by Bright Data Infrastructure</h2>
        <div className="bd-grid">
          <div className="bd-card">
            <div className="bd-card-title">SERP API Crawler</div>
            <div className="bd-card-desc">Queries global search engine results for news of data breaches and fines.</div>
          </div>
          <div className="bd-card">
            <div className="bd-card-title">Web Unlocker Proxy</div>
            <div className="bd-card-desc">Bypasses strict anti-bot protections to scan Pastebin for exposed secrets.</div>
          </div>
          <div className="bd-card">
            <div className="bd-card-title">Web Scraper API</div>
            <div className="bd-card-desc">Aggregates LinkedIn job boards to locate security hiring spikes (hiring distress).</div>
          </div>
          <div className="bd-card">
            <div className="bd-card-title">Scraping Browser CDP</div>
            <div className="bd-card-desc">Playwright CDP sessions crawling Glassdoor morale and compliance postures.</div>
          </div>
        </div>
      </div>

      <div className="welcome-footer">
        Powered by Bright Data &amp; AI Layer &bull; VendorSentinel v1.0.0
      </div>
    </div>
  );
}
