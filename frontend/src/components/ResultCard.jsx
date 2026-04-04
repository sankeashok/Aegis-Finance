import React from 'react';

const ResultCard = ({ prediction, loading }) => {
  if (loading) {
    return (
      <div className="result-card glass-card loading-state">
        <div className="loading-spinner"></div>
        <p>Crunching Risk Data...</p>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="result-card glass-card empty-state">
        <p>Awaiting Application Submission...</p>
        <span className="info-text">Select 'Run Risk Assessment' to see the engine's decision.</span>
      </div>
    );
  }

  const isSafe = prediction.status === 'Safe';

  return (
    <div className={`result-card glass-card result-container ${isSafe ? 'border-safe' : 'border-danger'}`}>
      <div className="result-header">
        <span className="result-label">ENGINE DECISION</span>
        <h2 className="result-status">{prediction.status}</h2>
      </div>

      <div className="result-body">
        <div className="info-item">
          <span className="info-label">Probability of Default</span>
          <span className="info-value">{(prediction.probability * 100).toFixed(2)}%</span>
        </div>
        
        <div className="info-item">
          <span className="info-label">Recommended Action</span>
          <span className="info-value action-value">{prediction.action}</span>
        </div>

        {/* Risk Drivers (Phase 2) */}
        {prediction.drivers && prediction.drivers.length > 0 && (
          <div className="drivers-section">
            <span className="info-label">Key Risk Drivers</span>
            <div className="drivers-list">
              {prediction.drivers.map((driver, idx) => (
                <div key={idx} className={`driver-item ${driver.impact.toLowerCase()}`}>
                  <div className="driver-header">
                    <span className="driver-feature">{driver.feature}</span>
                    <span className={`driver-badge ${driver.impact.toLowerCase()}`}>
                      {driver.impact === 'Positive' ? '✓ Safe' : '⚠ Risk'}
                    </span>
                  </div>
                  <p className="driver-desc">{driver.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="result-footer">
        <div className="security-certificate">
          🛡️ Aegis-Finance Verifier v1.0.0
        </div>
      </div>

      <style>{`
        .result-card {
          padding: 2.5rem;
          min-height: 250px;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: flex-start;
          text-align: left;
        }
        .empty-state {
          text-align: center;
          align-items: center;
          color: var(--text-muted);
        }
        .empty-state .info-text {
          font-size: 0.8rem;
          margin-top: 0.5rem;
        }
        .loading-state {
          text-align: center;
          align-items: center;
          gap: 1.5rem;
          color: var(--text-secondary);
        }
        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid var(--bg-tertiary);
          border-top: 4px solid var(--accent-primary);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .result-container {
          justify-content: flex-start;
          gap: 2rem;
        }
        .border-safe { border-bottom: 6px solid var(--success); }
        .border-danger { border-bottom: 6px solid var(--danger); }
        
        .result-label {
          font-size: 0.75rem;
          font-weight: 800;
          color: var(--text-muted);
          letter-spacing: 0.15em;
          margin-bottom: 0.5rem;
          display: block;
        }
        .result-status {
          font-size: 2rem;
          font-weight: 800;
          color: var(--text-primary);
          margin: 0;
        }
        .result-body {
          width: 100%;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .info-item {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        .info-label {
          font-size: 0.875rem;
          color: var(--text-secondary);
        }
        .info-value {
          font-size: 1.125rem;
          font-weight: 700;
          color: var(--text-primary);
          font-family: 'JetBrains Mono', monospace;
        }
        .action-value {
          color: var(--accent-primary);
        }

        .drivers-section {
          margin-top: 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        .drivers-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        .driver-item {
          padding: 0.825rem;
          background: rgba(255, 255, 255, 0.02);
          border-radius: 8px;
          border-left: 3px solid var(--border-subtle);
          transition: all 0.2s ease;
        }
        .driver-item:hover {
          background: rgba(255, 255, 255, 0.04);
          transform: translateX(4px);
        }
        .driver-item.positive { border-left-color: var(--success); }
        .driver-item.negative { border-left-color: var(--danger); }
        
        .driver-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.25rem;
        }
        .driver-feature {
          font-size: 0.85rem;
          font-weight: 700;
          color: var(--text-primary);
        }
        .driver-badge {
          font-size: 0.65rem;
          font-weight: 800;
          padding: 0.1rem 0.5rem;
          border-radius: 4px;
          text-transform: uppercase;
        }
        .driver-badge.positive { background: rgba(16, 185, 129, 0.1); color: var(--success); }
        .driver-badge.negative { background: rgba(239, 68, 68, 0.1); color: var(--danger); }
        
        .driver-desc {
          font-size: 0.75rem;
          color: var(--text-muted);
          margin: 0;
          line-height: 1.4;
        }

        .result-footer {
          margin-top: auto;
          width: 100%;
          padding-top: 1.5rem;
          border-top: 1px solid var(--border-subtle);
        }
        .security-certificate {
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--text-muted);
          opacity: 0.6;
        }
      `}</style>
    </div>
  );
};

export default ResultCard;
