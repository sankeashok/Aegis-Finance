import React from 'react';

const AegisGauge = ({ probability }) => {
  const percentage = Math.round(probability * 100);
  const strokeDasharray = 283; // Circumference of 2*PI*45
  const strokeDashoffset = strokeDasharray - (strokeDasharray * (percentage / 100));
  
  // Color based on risk
  let strokeColor = 'var(--success)';
  if (percentage > 70) strokeColor = 'var(--danger)';
  else if (percentage > 40) strokeColor = 'var(--warning)';

  return (
    <div className="gauge-container glass-card">
      <div className="gauge-wrapper">
        <svg viewBox="0 0 100 100" className="gauge-svg">
          {/* Background Arc */}
          <path
            d="M 20 80 A 40 40 0 1 1 80 80"
            fill="none"
            stroke="var(--bg-tertiary)"
            strokeWidth="8"
            strokeLinecap="round"
          />
          {/* Progress Arc */}
          <path
            d="M 20 80 A 40 40 0 1 1 80 80"
            fill="none"
            stroke={strokeColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray="188.5" // Half-circle circumference
            strokeDashoffset={188.5 - (188.5 * (percentage / 100))}
            style={{ transition: 'stroke-dashoffset 0.8s ease-out, stroke 0.5s ease' }}
          />
        </svg>
        
        <div className="gauge-text">
          <span className="gauge-value">{percentage}%</span>
          <span className="gauge-label">PROBABILITY</span>
        </div>
      </div>
      
      <div className="gauge-footer">
        <div className={`risk-indicator ${percentage > 50 ? 'risk-high' : 'risk-safe'}`}>
          {percentage > 50 ? '🛡️ HIGH RISK' : '✅ SAFE BASKET'}
        </div>
      </div>

      <style>{`
        .gauge-container {
          padding: 2.5rem;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 1.5rem;
        }
        .gauge-wrapper {
          position: relative;
          width: 240px;
          height: 160px;
        }
        .gauge-svg {
          width: 100%;
          height: 100%;
        }
        .gauge-text {
          position: absolute;
          bottom: 25px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
        }
        .gauge-value {
          font-size: 2.5rem;
          font-weight: 800;
          color: var(--text-primary);
          line-height: 1;
        }
        .gauge-label {
          font-size: 0.75rem;
          font-weight: 700;
          color: var(--text-muted);
          letter-spacing: 0.1em;
          margin-top: 0.5rem;
        }
        .gauge-footer {
          width: 100%;
        }
        .risk-indicator {
          padding: 0.75rem;
          border-radius: 8px;
          font-weight: 700;
          font-size: 0.875rem;
          letter-spacing: 0.05em;
          text-align: center;
        }
        .risk-high {
          background: rgba(239, 68, 68, 0.1);
          color: var(--danger);
          border: 1px solid rgba(239, 68, 68, 0.2);
        }
        .risk-safe {
          background: rgba(16, 185, 129, 0.1);
          color: var(--success);
          border: 1px solid rgba(16, 185, 129, 0.2);
        }
      `}</style>
    </div>
  );
};

export default AegisGauge;
