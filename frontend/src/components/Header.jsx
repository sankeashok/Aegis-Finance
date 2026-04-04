import React from 'react';

const Header = ({ theme, onToggleTheme }) => {
  return (
    <header className="header glass-card">
      <div className="header-content container">
        <div className="logo-section">
          <span className="logo-icon">🛡️</span>
          <h1 className="logo-text">Aegis<span>Finance</span></h1>
        </div>

        <div className="header-actions">
          <div className="status-badge">
            <span className="status-dot"></span>
            LIVE • v1.3.5 AUTOMATED
          </div>

          <button className="theme-toggle" onClick={onToggleTheme} title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
