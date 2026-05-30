import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import VendorList from './pages/VendorList';
import VendorDetail from './pages/VendorDetail';
import ScanPage from './pages/ScanPage';
import Settings from './pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        {/* Fixed Left Sidebar */}
        <Sidebar />
        
        {/* Main Content Area */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/vendors" element={<VendorList />} />
            <Route path="/vendors/:id" element={<VendorDetail />} />
            <Route path="/scan" element={<ScanPage />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
