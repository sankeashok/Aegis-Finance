import React, { useState } from 'react';

const RiskForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    income: 85000,
    credit_score: 720,
    D_39: 1.0,
    D_42: null,
    D_43: null,
    D_114: 1.0
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? null : parseFloat(value)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="risk-form-container glass-card">
      <div className="form-header">
        <h2>Risk Assessment Info</h2>
        <p>Enter applicant details to calculate real-time credit default risk.</p>
      </div>
      
      <form onSubmit={handleSubmit} className="risk-form">
        <div className="form-grid">
          <div className="form-group full-width">
            <label>Annual Income (USD)</label>
            <input 
              type="number" 
              name="income" 
              value={formData.income || ''} 
              onChange={handleChange}
              placeholder="e.g. 75000"
              required 
            />
          </div>
          
          <div className="form-group full-width">
            <label>Credit Score (FICO)</label>
            <input 
              type="number" 
              name="credit_score" 
              value={formData.credit_score || ''} 
              onChange={handleChange}
              placeholder="300-850"
              min="300"
              max="850"
              required 
            />
          </div>

          <div className="form-divider">Delinquency Indicators (D_)</div>

          <div className="form-group">
            <label>D_39 (Delinquency 39)</label>
            <input 
              type="number" 
              step="0.01"
              name="D_39" 
              value={formData.D_39 ?? ''} 
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>D_114 (Categorical)</label>
            <select name="D_114" value={formData.D_114 ?? ''} onChange={handleChange}>
              <option value="1.0">Active/Recent</option>
              <option value="0.0">No Recent</option>
              <option value="">Unknown</option>
            </select>
          </div>

          <div className="form-group">
            <label>D_42 (High Sparsity)</label>
            <input 
              type="number" 
              step="0.01"
              name="D_42" 
              value={formData.D_42 ?? ''} 
              onChange={handleChange}
              placeholder="Optional"
            />
          </div>

          <div className="form-group">
            <label>D_43 (High Sparsity)</label>
            <input 
              type="number" 
              step="0.01"
              name="D_43" 
              value={formData.D_43 ?? ''} 
              onChange={handleChange}
              placeholder="Optional"
            />
          </div>
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'CALCULATING RISK...' : '🛡️ RUN RISK ASSESSMENT'}
        </button>
      </form>

      <style>{`
        .risk-form-container {
          padding: 2.5rem;
          text-align: left;
        }
        .form-header {
          margin-bottom: 2rem;
        }
        .form-header h2 {
          margin-bottom: 0.5rem;
          font-weight: 700;
        }
        .form-header p {
          color: var(--text-secondary);
          font-size: 0.95rem;
        }
        .risk-form {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1.25rem;
        }
        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .full-width {
          grid-column: span 2;
        }
        .form-group label {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-primary);
        }
        .form-divider {
          grid-column: span 2;
          font-size: 0.75rem;
          font-weight: 800;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.1em;
          margin-top: 1rem;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid var(--border-subtle);
        }
        .submit-btn {
          width: 100%;
          padding: 1rem;
          font-weight: 700;
          letter-spacing: 0.05em;
          margin-top: 1rem;
        }
        @media (max-width: 640px) {
          .form-grid {
            grid-template-columns: 1fr;
          }
          .full-width {
            grid-column: span 1;
          }
          .form-divider {
            grid-column: span 1;
          }
        }
      `}</style>
    </div>
  );
};

export default RiskForm;
