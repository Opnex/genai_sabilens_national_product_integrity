import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NAFDACSidebar from '../../components/layout/NAFDACSidebar';
import NationalMap from '../../components/nafdac/HeatMap/NationalMap';
import LiveAlertFeed from '../../components/nafdac/HeatMap/LiveAlertFeed';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import MobileNAFDACNav from '../../components/layout/MobileNAFDACNav';
import Button from '../../components/common/Button';

const NationalDashboard = () => {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [timeRange, setTimeRange] = useState('7d');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Mock stats
  const stats = {
    activeInvestigations: 156,
    criticalAlerts: 23,
    highRiskZones: 12,
    weeklyReports: 847
  };

  const regions = [
    { name: 'Lagos', risk: 'critical', reports: 245 },
    { name: 'Kano', risk: 'high', reports: 180 },
    { name: 'Abuja', risk: 'medium', reports: 145 },
    { name: 'Rivers', risk: 'high', reports: 120 },
    { name: 'Ogun', risk: 'low', reports: 95 },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Header */}
      {windowWidth < 768 && (
        <div className="fixed top-0 left-0 right-0 bg-white shadow-soft z-40 px-4 py-3 mb-4">
          <div className="flex items-center justify-between">
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <Icon name="Menu" size={24} className="text-gray-600" library="fi" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                <Icon name="Map" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">National Dashboard</span>
            </div>
            <button 
              onClick={() => setShowFilters(!showFilters)}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <Icon name="Filter" size={20} className="text-gray-600" library="fi" />
            </button>
          </div>
        </div>
      )}

      {/* Mobile Menu */}
      <MobileNAFDACNav 
        isOpen={isMobileMenuOpen} 
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* Desktop Sidebar */}
      {windowWidth >= 768 && <NAFDACSidebar />}
      
      {/* Main Content */}
      <div className={`${windowWidth >= 768 ? 'lg:ml-64' : ''} ${windowWidth < 768 ? 'pt-16' : 'pt-8'} px-4 md:px-6 lg:px-8 pb-8`}>
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">National Intelligence Dashboard</h1>
          
          {windowWidth >= 768 && (
            <div className="flex items-center gap-4">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search incidents..."
                  className="w-64 pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
                <Icon name="Search" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" library="fi" />
              </div>
              
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
            </div>
          )}
        </div>

        {/* Mobile Filters */}
        {windowWidth < 768 && showFilters && (
          <Card className="mb-4 p-4">
            <div className="space-y-3">
              <input
                type="text"
                placeholder="Search incidents..."
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
            </div>
          </Card>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Active Investigations</p>
            <p className="text-lg md:text-2xl font-bold text-primary">{stats.activeInvestigations}</p>
            <p className="text-xs text-success mt-1">↑ 12% from last week</p>
          </Card>
          
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Critical Alerts</p>
            <p className="text-lg md:text-2xl font-bold text-danger">{stats.criticalAlerts}</p>
            <p className="text-xs text-danger mt-1">↑ 8% from last week</p>
          </Card>
          
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">High-Risk Zones</p>
            <p className="text-lg md:text-2xl font-bold text-warning">{stats.highRiskZones}</p>
            <p className="text-xs text-gray-500 mt-1">Across 8 states</p>
          </Card>
          
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Reports This Week</p>
            <p className="text-lg md:text-2xl font-bold text-success">{stats.weeklyReports}</p>
            <p className="text-xs text-gray-500 mt-1">↑ 5% verified</p>
          </Card>
        </div>

        {/* Legend - Mobile */}
        {windowWidth < 768 && (
          <Card className="mb-4 p-3">
            <div className="grid grid-cols-4 gap-2 text-center">
              <div>
                <div className="w-3 h-3 bg-danger rounded-full mx-auto mb-1" />
                <span className="text-xs">Critical</span>
              </div>
              <div>
                <div className="w-3 h-3 bg-warning rounded-full mx-auto mb-1" />
                <span className="text-xs">High</span>
              </div>
              <div>
                <div className="w-3 h-3 bg-primary rounded-full mx-auto mb-1" />
                <span className="text-xs">Medium</span>
              </div>
              <div>
                <div className="w-3 h-3 bg-success rounded-full mx-auto mb-1" />
                <span className="text-xs">Low</span>
              </div>
            </div>
          </Card>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map Container */}
          <div className="lg:col-span-2">
            <NationalMap onRegionSelect={setSelectedRegion} />
          </div>

          {/* Live Alert Feed */}
          <div className="lg:col-span-1">
            <LiveAlertFeed />
          </div>
        </div>

        {/* Region Details - Mobile */}
        {selectedRegion && windowWidth < 768 && (
          <Card className="mt-4 p-4">
            <h3 className="font-semibold mb-3">{selectedRegion} Details</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Total Reports:</span>
                <span className="font-medium">156</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Counterfeit:</span>
                <span className="text-danger">45</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Suspicious:</span>
                <span className="text-warning">32</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Last Report:</span>
                <span className="text-gray-600">Today, 2:30 PM</span>
              </div>
              <Button variant="primary" size="sm" fullWidth className="mt-3">
                View Details
              </Button>
            </div>
          </Card>
        )}

        {/* Top Regions Table - Mobile */}
        {windowWidth < 768 && (
          <Card className="mt-4 p-4">
            <h3 className="font-semibold mb-3">Top Risk Regions</h3>
            <div className="space-y-2">
              {regions.map((region) => (
                <div key={region.name} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full bg-${region.risk === 'critical' ? 'danger' : region.risk === 'high' ? 'warning' : region.risk === 'medium' ? 'primary' : 'success'}`} />
                    <span className="font-medium">{region.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-400">{region.reports} reports</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full bg-${region.risk === 'critical' ? 'danger' : region.risk === 'high' ? 'warning' : region.risk === 'medium' ? 'primary' : 'success'}/10 text-${region.risk === 'critical' ? 'danger' : region.risk === 'high' ? 'warning' : region.risk === 'medium' ? 'primary' : 'success'}`}>
                      {region.risk}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default NationalDashboard;