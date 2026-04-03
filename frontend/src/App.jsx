import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import RiskForm from './components/RiskForm'
import AegisGauge from './components/AegisGauge'
import ResultCard from './components/ResultCard'
import './App.css'

function App() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark')
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

  const handlePredict = async (formData) => {
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
      
      const data = await response.ok ? await response.json() : null
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
      
      <main className="container main-layout">
        <section className="input-section">
          <RiskForm onSubmit={handlePredict} loading={loading} />
        </section>
        
        <section className="output-section">
          {error && <div className="error-message glass-card">{error}</div>}
          
          <div className="result-display">
            <AegisGauge probability={prediction ? prediction.probability : 0} />
            <ResultCard prediction={prediction} loading={loading} />
          </div>
        </section>
      </main>
      
      <footer className="footer">
        <p>🛡️ Aegis-Finance Risk Gateway V1.0.0 | Production Grade Inference</p>
      </footer>
    </div>
  )
}

export default App
