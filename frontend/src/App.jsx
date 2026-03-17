import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import ScrollToTop from './components/common/ScrollToTop';

// Consumer Pages
import MobileSplash from './pages/consumer/MobileSplash';
import LandingPage from './pages/consumer/LandingPage';
import Onboarding from './pages/consumer/Onboarding';
import ConsumerLogin from './pages/consumer/Login';
import ConsumerSignup from './pages/consumer/Signup';
import Home from './pages/consumer/Home';
import Scan from './pages/consumer/Scan';
import ScanResult from './pages/consumer/ScanResult';
import Profile from './pages/consumer/Profile';
import Report from './pages/consumer/Report';
import ScanHistory from './pages/consumer/ScanHistory';
import PrivacyPolicy from './pages/consumer/PrivacyPolicy';
import TermsOfService from './pages/consumer/TermsOfService';
import HelpSupport from './pages/consumer/HelpSupport';
import EditProfile from './pages/consumer/EditProfile';
import RoleSelect from './pages/consumer/RoleSelect';

// Company Pages
import CompanyLogin from './pages/company/Login';
import CompanySignup from './pages/company/Signup';
import CompanyDashboard from './pages/company/Dashboard';
import CompanyReports from './pages/company/Reports';
import CompanyHeatMap from './pages/company/HeatMap';
import CompanyRegistry from './pages/company/Registry';
import CompanyEvidence from './pages/company/EvidenceVault';
import CompanySettings from './pages/company/Settings';

// NAFDAC Pages
import NAFDACLogin from './pages/nafdac/Login';
import NAFDACSignup from './pages/nafdac/Signup';
import NAFDACDashboard from './pages/nafdac/NationalDashboard';
import NAFDACAlerts from './pages/nafdac/Alerts';
import NAFDACCases from './pages/nafdac/Cases';
import NAFDACVendors from './pages/nafdac/VendorTracker';
import NAFDACAnalytics from './pages/nafdac/Analytics';
import NAFDACExport from './pages/nafdac/ExportData';

// Home component with screen size detection
const HomeRedirect = () => {
  const navigate = useNavigate();
  
  useEffect(() => {
    const checkScreenSize = () => {
      if (window.innerWidth >= 1024) {
        navigate('/landing', { replace: true });
      } else {
        navigate('/mobile-splash', { replace: true });
      }
    };
    
    checkScreenSize();
    // Optional: Add resize listener if you want to handle screen resize
    // window.addEventListener('resize', checkScreenSize);
    // return () => window.removeEventListener('resize', checkScreenSize);
  }, [navigate]);
  
  return null;
};

// Protected Route Components
const ConsumerProtectedRoute = ({ children }) => {
  const user = JSON.parse(localStorage.getItem('currentUser') || '{}');

  if (!user || (!user.phone && !user.role)) {
    return <Navigate to="/login" replace />;
  }

  if (user.role === 'company' || user.role === 'company_admin') {
    return <Navigate to="/company/dashboard" replace />;
  }

  if (user.role === 'nafdac' || user.role === 'nafdac_admin' || user.role === 'nafdac_officer') {
    return <Navigate to="/nafdac/dashboard" replace />;
  }

  return children;
};

const CompanyProtectedRoute = ({ children }) => {
  const user = JSON.parse(localStorage.getItem('currentUser') || '{}');
  const isAuthenticated = user && (user.role === 'company' || user.role === 'company_admin');

  if (!isAuthenticated) {
    return <Navigate to="/company/login" replace />;
  }

  return children;
};

const NAFDACProtectedRoute = ({ children }) => {
  const user = JSON.parse(localStorage.getItem('currentUser') || '{}');
  const isAuthenticated = user && (user.role === 'nafdac' || user.role === 'nafdac_admin' || user.role === 'nafdac_officer');

  if (!isAuthenticated) {
    return <Navigate to="/nafdac/login" replace />;
  }

  return children;
};

function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <ScrollToTop />
      <Routes>
        {/* Root path - checks screen size */}
        <Route path="/" element={<HomeRedirect />} />
        
        {/* Desktop Routes */}
        <Route path="/landing" element={<LandingPage />} />
        
        {/* Mobile Consumer Routes */}
        <Route path="/mobile-splash" element={<MobileSplash />} />
        <Route path="/onboarding" element={<Onboarding />} />
        <Route path="/role-select" element={<RoleSelect />} />
        
        {/* Consumer Auth */}
        <Route path="/signup" element={<ConsumerSignup />} />
        <Route path="/login" element={<ConsumerLogin />} />

        {/* Company Auth */}
        <Route path="/company/login" element={<CompanyLogin />} />
        <Route path="/company/signup" element={<CompanySignup />} />

        {/* NAFDAC Auth */}
        <Route path="/nafdac/login" element={<NAFDACLogin />} />
        <Route path="/nafdac/signup" element={<NAFDACSignup />} />

        {/* Protected Consumer Routes */}
        <Route path="/home" element={<ConsumerProtectedRoute><Home /></ConsumerProtectedRoute>} />
        <Route path="/scan" element={<ConsumerProtectedRoute><Scan /></ConsumerProtectedRoute>} />
        <Route path="/scan/:result" element={<ConsumerProtectedRoute><ScanResult /></ConsumerProtectedRoute>} />
        <Route path="/report" element={<ConsumerProtectedRoute><Report /></ConsumerProtectedRoute>} />
        <Route path="/profile" element={<ConsumerProtectedRoute><Profile /></ConsumerProtectedRoute>} />
        <Route path="/scan-history" element={<ConsumerProtectedRoute><ScanHistory /></ConsumerProtectedRoute>} />
        <Route path="/privacy-policy" element={<ConsumerProtectedRoute><PrivacyPolicy /></ConsumerProtectedRoute>} />
        <Route path="/terms-of-service" element={<ConsumerProtectedRoute><TermsOfService /></ConsumerProtectedRoute>} />
        <Route path="/help-support" element={<ConsumerProtectedRoute><HelpSupport /></ConsumerProtectedRoute>} />
        <Route path="/edit-profile" element={<ConsumerProtectedRoute><EditProfile /></ConsumerProtectedRoute>} />

        {/* Protected Company Routes */}
        <Route path="/company/dashboard" element={<CompanyProtectedRoute><CompanyDashboard /></CompanyProtectedRoute>} />
        <Route path="/company/reports" element={<CompanyProtectedRoute><CompanyReports /></CompanyProtectedRoute>} />
        <Route path="/company/heatmap" element={<CompanyProtectedRoute><CompanyHeatMap /></CompanyProtectedRoute>} />
        <Route path="/company/registry" element={<CompanyProtectedRoute><CompanyRegistry /></CompanyProtectedRoute>} />
        <Route path="/company/evidence" element={<CompanyProtectedRoute><CompanyEvidence /></CompanyProtectedRoute>} />
        <Route path="/company/settings" element={<CompanyProtectedRoute><CompanySettings /></CompanyProtectedRoute>} />

        {/* Protected NAFDAC Routes */}
        <Route path="/nafdac/dashboard" element={<NAFDACProtectedRoute><NAFDACDashboard /></NAFDACProtectedRoute>} />
        <Route path="/nafdac/alerts" element={<NAFDACProtectedRoute><NAFDACAlerts /></NAFDACProtectedRoute>} />
        <Route path="/nafdac/cases" element={<NAFDACProtectedRoute><NAFDACCases /></NAFDACProtectedRoute>} />
        <Route path="/nafdac/vendors" element={<NAFDACProtectedRoute><NAFDACVendors /></NAFDACProtectedRoute>} />
        <Route path="/nafdac/analytics" element={<NAFDACProtectedRoute><NAFDACAnalytics /></NAFDACProtectedRoute>} />
        <Route path="/nafdac/export" element={<NAFDACProtectedRoute><NAFDACExport /></NAFDACProtectedRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;