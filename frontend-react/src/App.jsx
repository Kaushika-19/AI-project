import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import TopHeader from './components/TopHeader';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import Pipeline from './pages/Pipeline';
import AIInsights from './pages/AIInsights';
import Actions from './pages/Actions';
import './index.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth <= 768) {
        setSidebarOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/': return 'Dashboard';
      case '/customers': return 'Customers';
      case '/pipeline': return 'Pipeline';
      case '/insights': return 'AI Insights';
      case '/actions': return 'Actions';
      default: return 'Dashboard';
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', width: '100vw', overflowX: 'hidden' }}>
      {/* Mobile Overlay */}
      {window.innerWidth <= 768 && sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
          style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 90
          }}
        />
      )}

      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      <main className={`main-content ${sidebarOpen ? 'open' : 'closed'}`} id="mainContent" style={{ flex: 1 }}>
        <TopHeader
          title={getPageTitle()}
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
        />

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/pipeline" element={<Pipeline />} />
          <Route path="/insights" element={<AIInsights />} />
          <Route path="/actions" element={<Actions />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
