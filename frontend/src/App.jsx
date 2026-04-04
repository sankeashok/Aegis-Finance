import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import RiskForm from './components/RiskForm'
import AegisGauge from './components/AegisGauge'
import ResultCard from './components/ResultCard'
import './App.css'

function App() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark')
  const [formData, setFormData] = useState({
    income: 85000,
    credit_score: 720,
    D_39: 1.0,
    D_42: null,
    D_43: null,
    D_114: 1.0
  })
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark')
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? null : parseFloat(value)
    }))
  }

  const handlePredict = async (e) => {
    if (e) e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      
      if (!response.ok) {
        throw new Error('API request failed. Is the backend running?')
      }
      
      const data = await response.json()
      setPrediction(data)
    } catch (err) {
      setError(err.message)
      setPrediction(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <Header theme={theme} onToggleTheme={toggleTheme} />
      
      {/* Elite Sticky Quick Action Bar (Mobile Only) */}
      <div className="sticky-mobile-actions glass-card">
        <div className="quick-info">
          <span className="quick-label">Current Risk:</span>
          <span className={`quick-status ${prediction ? prediction.status.toLowerCase().replace(' ', '-') : ''}`}>
            {prediction ? prediction.status : 'Awaiting...'}
          </span>
        </div>
        <button 
          onClick={handlePredict} 
          className="quick-run-btn" 
          disabled={loading}
        >
          {loading ? '...' : '🛡️ RUN'}
        </button>
      </div>

      <main className="container main-layout">
        <section className="output-section">
          {error && <div className="error-message glass-card">{error}</div>}
          
          <div className="result-display">
            <AegisGauge probability={prediction ? prediction.probability : 0} />
            <ResultCard prediction={prediction} loading={loading} />
          </div>
        </section>

        <section className="input-section">
          <RiskForm 
            formData={formData} 
            onChange={handleInputChange} 
            onSubmit={handlePredict} 
            loading={loading} 
          />
        </section>
      </main>
      
      <footer className="footer">
        <div className="footer-credits">
          🛡️ Aegis-Finance Risk Gateway V1.1.2 | Production Grade Inference
        </div>
        <div className="developer-tag">
          Developed by <a href="https://www.linkedin.com/in/ashok-sanke/" target="_blank" rel="noopener noreferrer">Ashok Sanke</a>
        </div>
      </footer>
    </div>
  )
}

export default App
