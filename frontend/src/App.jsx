import React from 'react';
import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import VendorList from './pages/VendorList';
import VendorDetail from './pages/VendorDetail';
import ScanPage from './pages/ScanPage';
import Settings from './pages/Settings';
import Welcome from './pages/Welcome';

// Layout that wraps all dashboard sub-pages and includes the Sidebar
function DashboardLayout() {
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Full-screen Welcome / Landing page without Sidebar */}
        <Route path="/" element={<Welcome />} />
        
        {/* All Dashboard pages under the shared Sidebar Layout */}
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/vendors" element={<VendorList />} />
          <Route path="/vendors/:id" element={<VendorDetail />} />
          <Route path="/scan" element={<ScanPage />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Dashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
