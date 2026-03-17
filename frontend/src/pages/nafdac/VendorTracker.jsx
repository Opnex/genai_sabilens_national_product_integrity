import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NAFDACSidebar from '../../components/layout/NAFDACSidebar';
import VendorTable from '../../components/nafdac/Vendor/VendorTable';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import MobileNAFDACNav from '../../components/layout/MobileNAFDACNav';

const VendorTracker = () => {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [filterRisk, setFilterRisk] = useState('all');
  const [timeRange, setTimeRange] = useState('30d');
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [showVendorModal, setShowVendorModal] = useState(false);
  const [showBlacklistModal, setShowBlacklistModal] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Mock stats
  const stats = {
    total: 1247,
    highRisk: 156,
    recurring: 89,
    avgReports: 12.4
  };

  const vendors = [
    { location: 'Lagos Mainland Market', reportCount: 47, products: ['Malaria Tablets', 'Antibiotics'], riskLevel: 'Critical', lastReported: 'Today' },
    { location: 'Kano Central Market', reportCount: 32, products: ['Pain Relievers', 'Vitamins'], riskLevel: 'High', lastReported: 'Yesterday' },
    { location: 'Abuja Shopping Complex', reportCount: 28, products: ['Antibiotics', 'Vaccines'], riskLevel: 'High', lastReported: '2 days ago' },
    { location: 'Port Harcourt Market', reportCount: 21, products: ['Malaria Tablets'], riskLevel: 'Medium', lastReported: '3 days ago' },
    { location: 'Ibadan Central', reportCount: 15, products: ['Pain Relievers'], riskLevel: 'Medium', lastReported: '5 days ago' },
    { location: 'Benin City Market', reportCount: 12, products: ['Vitamins'], riskLevel: 'Low', lastReported: '1 week ago' },
  ];

  const filteredVendors = vendors.filter(v => {
    if (filterRisk !== 'all' && v.riskLevel.toLowerCase() !== filterRisk.toLowerCase()) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return v.location.toLowerCase().includes(term) ||
             v.products.some(p => p.toLowerCase().includes(term));
    }
    return true;
  });

  const handleVendorClick = (vendor) => {
    setSelectedVendor(vendor);
    setShowVendorModal(true);
  };

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
                <Icon name="Users" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">Vendor Tracker</span>
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
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Vendor Recurrence Tracker</h1>
          
          {windowWidth >= 768 && (
            <div className="flex gap-3">
              <div className="relative">
                <Icon name="Search" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" library="fi" />
                <input
                  type="text"
                  placeholder="Search vendors..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 w-64"
                />
              </div>
              
              <select
                value={filterRisk}
                onChange={(e) => setFilterRisk(e.target.value)}
                className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="all">All Risk Levels</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
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
              <div className="relative">
                <Icon name="Search" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" library="fi" />
                <input
                  type="text"
                  placeholder="Search vendors..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
              </div>
              
              <select
                value={filterRisk}
                onChange={(e) => setFilterRisk(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="all">All Risk Levels</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
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
            <p className="text-xs text-gray-400 mb-1">Total Vendors</p>
            <p className="text-lg md:text-2xl font-bold text-primary">{stats.total}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">High-Risk Vendors</p>
            <p className="text-lg md:text-2xl font-bold text-danger">{stats.highRisk}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Recurring Offenders</p>
            <p className="text-lg md:text-2xl font-bold text-warning">{stats.recurring}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Avg Reports/Vendor</p>
            <p className="text-lg md:text-2xl font-bold text-success">{stats.avgReports}</p>
          </Card>
        </div>

        {/* Vendor List - Mobile Card View */}
        {windowWidth < 768 ? (
          <div className="space-y-3">
            {filteredVendors.map((vendor, index) => (
              <Card 
                key={index} 
                className="p-4 cursor-pointer hover:shadow-card transition-all"
                onClick={() => handleVendorClick(vendor)}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold">{vendor.location}</h3>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    vendor.riskLevel === 'Critical' ? 'bg-danger/10 text-danger' :
                    vendor.riskLevel === 'High' ? 'bg-warning/10 text-warning' :
                    vendor.riskLevel === 'Medium' ? 'bg-primary/10 text-primary' :
                    'bg-success/10 text-success'
                  }`}>
                    {vendor.riskLevel}
                  </span>
                </div>
                
                <div className="flex flex-wrap gap-1 mb-2">
                  {vendor.products.map((product, i) => (
                    <span key={i} className="text-xs bg-gray-100 px-2 py-1 rounded-full">
                      {product}
                    </span>
                  ))}
                </div>
                
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">{vendor.reportCount} reports</span>
                  <span className="text-gray-400 text-xs">{vendor.lastReported}</span>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          /* Desktop Table View */
          <VendorTable 
            vendors={filteredVendors} 
            onVendorClick={handleVendorClick}
          />
        )}
      </div>

      {/* Vendor Detail Modal */}
      <Modal
        isOpen={showVendorModal}
        onClose={() => setShowVendorModal(false)}
        type="info"
        title={selectedVendor?.location}
        message={
          selectedVendor && (
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Risk Level</span>
                  <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                    selectedVendor.riskLevel === 'Critical' ? 'bg-danger/10 text-danger' :
                    selectedVendor.riskLevel === 'High' ? 'bg-warning/10 text-warning' :
                    selectedVendor.riskLevel === 'Medium' ? 'bg-primary/10 text-primary' :
                    'bg-success/10 text-success'
                  }`}>
                    {selectedVendor.riskLevel}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Total Reports</span>
                  <span className="text-sm font-medium">{selectedVendor.reportCount}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Last Reported</span>
                  <span className="text-sm font-medium">{selectedVendor.lastReported}</span>
                </div>
                
                <div>
                  <span className="text-sm text-gray-500 block mb-2">Products Involved</span>
                  <div className="flex flex-wrap gap-1">
                    {selectedVendor.products.map((product, i) => (
                      <span key={i} className="text-xs bg-gray-200 px-2 py-1 rounded-full">
                        {product}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setShowVendorModal(false)}
                >
                  Close
                </Button>
                <Button
                  variant="danger"
                  onClick={() => {
                    setShowVendorModal(false);
                    setShowBlacklistModal(true);
                  }}
                >
                  Blacklist Vendor
                </Button>
              </div>
            </div>
          )
        }
      />

      {/* Blacklist Confirmation Modal */}
      <Modal
        isOpen={showBlacklistModal}
        onClose={() => setShowBlacklistModal(false)}
        type="warning"
        title="Blacklist Vendor"
        message={
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to blacklist {selectedVendor?.location}? This vendor will be flagged for all enforcement actions.
            </p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setShowBlacklistModal(false)}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => {
                  setShowBlacklistModal(false);
                  alert(`${selectedVendor?.location} has been blacklisted`);
                }}
              >
                Confirm Blacklist
              </Button>
            </div>
          </div>
        }
      />
    </div>
  );
};

export default VendorTracker;