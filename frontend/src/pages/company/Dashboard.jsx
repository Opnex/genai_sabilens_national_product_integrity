import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CompanySidebar from '../../components/layout/CompanySidebar';
import KPICard from '../../components/company/Overview/KPICard';
import TrendChart from '../../components/company/Overview/TrendChart';
import TopStatesChart from '../../components/company/Overview/TopStatesChart';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import MobileCompanyNav from '../../components/layout/MobileCompanyNav';

const Dashboard = () => {
  const navigate = useNavigate();
  const [companyData, setCompanyData] = useState(null);
  const [scanStats, setScanStats] = useState({
    total: 0,
    verified: 0,
    highRisk: 0,
    mostImitated: 'N/A'
  });
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);

  // Get current user from localStorage
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  
  useEffect(() => {
    loadCompanyData();
    
    // Handle resize for responsive design
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const loadCompanyData = () => {
    setLoading(true);
    
    // Get company details
    const companies = JSON.parse(localStorage.getItem('companies') || '[]');
    const company = companies.find(c => c.id === currentUser.companyId);
    
    if (!company) {
      // If no company found, redirect to login
      navigate('/company/login');
      return;
    }
    
    setCompanyData(company);
    
    // Get scan history for this company's products
    const allUsers = JSON.parse(localStorage.getItem('users') || '[]');
    const allScans = [];
    
    // Collect all scans from all users
    allUsers.forEach(user => {
      const historyKey = `scanHistory_${user.phone}`;
      const userScans = JSON.parse(localStorage.getItem(historyKey) || '[]');
      
      // Filter scans that match this company's products
      const companyScans = userScans.filter(scan => 
        scan.manufacturer?.toLowerCase().includes(company.name.toLowerCase()) ||
        scan.product?.toLowerCase().includes(company.name.toLowerCase())
      );
      
      allScans.push(...companyScans);
    });
    
    // Calculate stats
    const total = allScans.length;
    const verified = allScans.filter(s => s.status === 'authentic').length;
    const highRisk = allScans.filter(s => s.status === 'fake' || s.status === 'caution').length;
    
    // Find most imitated product
    const productCounts = {};
    allScans.forEach(scan => {
      if (scan.status === 'fake' || scan.status === 'caution') {
        productCounts[scan.product] = (productCounts[scan.product] || 0) + 1;
      }
    });
    
    let mostImitated = 'N/A';
    let maxCount = 0;
    Object.entries(productCounts).forEach(([product, count]) => {
      if (count > maxCount) {
        maxCount = count;
        mostImitated = product;
      }
    });
    
    setScanStats({
      total,
      verified,
      highRisk,
      mostImitated: mostImitated !== 'N/A' ? mostImitated : 'No counterfeits yet'
    });
    
    // Get recent alerts (last 5 scans)
    const recent = allScans
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 5);
    
    setRecentAlerts(recent);
    setLoading(false);
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  // Determine grid columns based on screen size
  const getKpiGridClass = () => {
    if (windowWidth < 640) return 'grid-cols-1'; // Mobile
    if (windowWidth < 1024) return 'grid-cols-2'; // Tablet
    return 'grid-cols-4'; // Desktop
  };

  const getChartGridClass = () => {
    if (windowWidth < 1024) return 'grid-cols-1'; // Mobile/Tablet
    return 'grid-cols-2'; // Desktop
  };

  const getQuickActionsGridClass = () => {
    if (windowWidth < 640) return 'grid-cols-1'; // Mobile
    if (windowWidth < 1024) return 'grid-cols-2'; // Tablet
    return 'grid-cols-3'; // Desktop
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        {/* Show different loading for mobile/desktop */}
        {windowWidth < 768 ? (
          <div className="flex flex-col items-center justify-center h-screen">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-gray-500">Loading your dashboard...</p>
          </div>
        ) : (
          <>
            <CompanySidebar />
            <div className="lg:ml-64 p-4 md:p-8 flex justify-center items-center h-screen">
              <div className="text-center">
                <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-gray-500">Loading your dashboard...</p>
              </div>
            </div>
          </>
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Header */}
      {windowWidth < 768 && (
        <div className="fixed top-0 left-0 right-0 bg-white mb-4 shadow-soft z-40 px-4 py-3">
          <div className="flex items-center justify-between ">
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <Icon name="Menu" size={24} className="text-gray-600" library="fi" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                <Icon name="Shield" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">{companyData?.name || 'Company'}</span>
            </div>
            <button className="relative p-2 hover:bg-gray-100 rounded-lg">
              <Icon name="Bell" size={20} className="text-gray-500" library="fi" />
              {recentAlerts.filter(a => a.status !== 'authentic').length > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Mobile Menu */}
      <MobileCompanyNav 
        isOpen={isMobileMenuOpen} 
        onClose={() => setIsMobileMenuOpen(false)}
        companyName={companyData?.name}
      />

      {/* Desktop Sidebar - hidden on mobile */}
      {windowWidth >= 768 && <CompanySidebar companyName={companyData?.name} />}
      
      {/* Main Content - responsive padding */}
      <div className={`${windowWidth >= 768 ? 'lg:ml-64' : ''} pt-16 md:pt-8 px-4 md:px-6 lg:px-8 pb-8`}>
        {/* Top Navbar - Desktop only */}
        {windowWidth >= 768 && (
          <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center mb-6 lg:mb-8 gap-4">
            <div>
              <p className="text-sm text-gray-500">{getGreeting()},</p>
              <h1 className="text-xl lg:text-2xl font-bold text-gray-900">{companyData?.name}</h1>
              <p className="text-xs text-gray-400 mt-1">CAC: {companyData?.registrationNumber}</p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative w-full sm:w-64">
                <input
                  type="text"
                  placeholder="Search your products..."
                  className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
                <Icon name="Search" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" library="fi" />
              </div>
              
              <button className="relative p-2 bg-white rounded-xl shadow-soft hover:shadow-card transition-shadow">
                <Icon name="Bell" size={20} className="text-gray-500" library="fi" />
                {recentAlerts.filter(a => a.status !== 'authentic').length > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
                )}
              </button>
              
              <div className="hidden lg:flex items-center gap-3">
                <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
                  <Icon name="Building" size={20} className="text-primary" library="fi" />
                </div>
                <div>
                  <p className="text-sm font-medium">{companyData?.city}, {companyData?.state}</p>
                  <p className="text-xs text-gray-400">Member since {new Date(companyData?.createdAt).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Welcome Banner - responsive */}
        <Card className="mb-6 lg:mb-8 bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 lg:p-6">
            <div>
              <h2 className="text-base lg:text-lg font-semibold text-gray-900 mb-2">Welcome to Your Brand Protection Dashboard</h2>
              <p className="text-sm text-gray-600">
                Monitor counterfeit activities, track reports, and protect your brand reputation.
              </p>
            </div>
            <button 
              onClick={() => navigate('/company/reports')}
              className="w-full sm:w-auto px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary-dark transition-colors text-sm whitespace-nowrap"
            >
              View Reports
            </button>
          </div>
        </Card>

        {/* KPI Cards - responsive grid */}
        <div className={`grid ${getKpiGridClass()} gap-4 lg:gap-6 mb-6 lg:mb-8`}>
          <KPICard
            title="Total Reports"
            value={scanStats.total.toString()}
            change={scanStats.total > 0 ? 12.5 : 0}
            icon="AlertTriangle"
            color="primary"
          />
          <KPICard
            title="Verified Authentic"
            value={scanStats.verified.toString()}
            change={scanStats.verified > 0 ? 8.2 : 0}
            icon="CheckCircle"
            color="success"
          />
          <KPICard
            title="Counterfeit Alerts"
            value={scanStats.highRisk.toString()}
            change={scanStats.highRisk > 0 ? 15.3 : 0}
            icon="AlertOctagon"
            color="danger"
          />
          <KPICard
            title="Most Imitated"
            value={scanStats.mostImitated.length > 20 ? scanStats.mostImitated.substring(0, 20) + '...' : scanStats.mostImitated}
            icon="Package"
            color="warning"
          />
        </div>

        {/* Charts - responsive grid */}
        <div className={`grid ${getChartGridClass()} gap-4 lg:gap-6 mb-6 lg:mb-8`}>
          <div className="w-full overflow-x-auto">
            <TrendChart companyId={currentUser.companyId} />
          </div>
          <div className="w-full overflow-x-auto">
            <TopStatesChart companyId={currentUser.companyId} />
          </div>
        </div>

        {/* Recent Alerts - responsive */}
        <Card className="mb-6 lg:mb-8">
          <div className="p-4 lg:p-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
              <h3 className="text-base lg:text-lg font-semibold text-gray-900">Recent Alerts for Your Products</h3>
              <button 
                onClick={() => navigate('/company/reports')}
                className="text-primary text-sm font-medium hover:underline"
              >
                View All
              </button>
            </div>

            {recentAlerts.length > 0 ? (
              <div className="space-y-3">
                {recentAlerts.map((alert, index) => (
                  <div 
                    key={index} 
                    className="flex flex-col sm:flex-row sm:items-center justify-between p-3 border border-gray-100 rounded-lg hover:bg-gray-50 cursor-pointer gap-3"
                    onClick={() => navigate('/company/reports')}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        alert.status === 'authentic' ? 'bg-success/10' :
                        alert.status === 'caution' ? 'bg-warning/10' : 'bg-danger/10'
                      }`}>
                        <Icon 
                          name={alert.status === 'authentic' ? 'CheckCircle' : alert.status === 'caution' ? 'AlertTriangle' : 'XCircle'} 
                          size={20} 
                          className={
                            alert.status === 'authentic' ? 'text-success' :
                            alert.status === 'caution' ? 'text-warning' : 'text-danger'
                          } 
                          library="fi" 
                        />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-sm truncate">{alert.product}</p>
                        <p className="text-xs text-gray-400 truncate">{alert.location} • {alert.time}</p>
                      </div>
                    </div>
                    <div className="text-left sm:text-right ml-13 sm:ml-0">
                      <span className={`text-xs px-2 py-1 rounded-full inline-block ${
                        alert.status === 'authentic' ? 'bg-success/10 text-success' :
                        alert.status === 'caution' ? 'bg-warning/10 text-warning' : 'bg-danger/10 text-danger'
                      }`}>
                        {alert.status === 'authentic' ? 'Authentic' : alert.status === 'caution' ? 'Caution' : 'Counterfeit'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Icon name="Bell" size={32} className="text-gray-300 mx-auto mb-3" library="fi" />
                <p className="text-gray-400">No alerts yet for your products</p>
                <p className="text-sm text-gray-300 mt-1">When products are scanned, alerts will appear here</p>
              </div>
            )}
          </div>
        </Card>

        {/* Quick Actions - responsive grid */}
        <div className={`grid ${getQuickActionsGridClass()} gap-4`}>
          <Card className="p-4 hover:shadow-card transition-shadow cursor-pointer" onClick={() => navigate('/company/registry')}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <Icon name="Package" size={20} className="text-primary" library="fi" />
              </div>
              <div className="min-w-0">
                <h4 className="font-medium truncate">Product Registry</h4>
                <p className="text-xs text-gray-400 truncate">Manage your products</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 hover:shadow-card transition-shadow cursor-pointer" onClick={() => navigate('/company/evidence')}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <Icon name="Folder" size={20} className="text-primary" library="fi" />
              </div>
              <div className="min-w-0">
                <h4 className="font-medium truncate">Evidence Vault</h4>
                <p className="text-xs text-gray-400 truncate">View counterfeit evidence</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 hover:shadow-card transition-shadow cursor-pointer" onClick={() => navigate('/company/heatmap')}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <Icon name="Map" size={20} className="text-primary" library="fi" />
              </div>
              <div className="min-w-0">
                <h4 className="font-medium truncate">Risk Heat Map</h4>
                <p className="text-xs text-gray-400 truncate">View counterfeit hotspots</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;