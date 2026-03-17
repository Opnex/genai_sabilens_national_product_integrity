import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NAFDACSidebar from '../../components/layout/NAFDACSidebar';
import AlertList from '../../components/nafdac/Alerts/AlertList';
import AlertDetail from '../../components/nafdac/Alerts/AlertDetail';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import MobileNAFDACNav from '../../components/layout/MobileNAFDACNav';

const Alerts = () => {
  const navigate = useNavigate();
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('severity');
  const [timeRange, setTimeRange] = useState('7d');
  const [showFilters, setShowFilters] = useState(false);
  const [showAcknowledgeModal, setShowAcknowledgeModal] = useState(false);
  const [acknowledgeLoading, setAcknowledgeLoading] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Mock stats
  const stats = {
    total: 47,
    critical: 12,
    high: 18,
    medium: 17
  };

  const handleAcknowledgeAll = () => {
    setAcknowledgeLoading(true);
    setTimeout(() => {
      setAcknowledgeLoading(false);
      setShowAcknowledgeModal(false);
      alert('All alerts have been acknowledged');
    }, 1500);
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
                <Icon name="AlertTriangle" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">High-Risk Alerts</span>
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
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">High-Risk Alerts</h1>
          
          {windowWidth >= 768 && (
            <div className="flex gap-3">
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
              </select>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="severity">Sort by Severity</option>
                <option value="date">Sort by Date</option>
                <option value="reports">Sort by Reports</option>
              </select>
              
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
              
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setShowAcknowledgeModal(true)}
              >
                Acknowledge All
              </Button>
            </div>
          )}
        </div>

        {/* Mobile Filters */}
        {windowWidth < 768 && showFilters && (
          <Card className="mb-4 p-4">
            <div className="space-y-3">
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
              </select>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="severity">Sort by Severity</option>
                <option value="date">Sort by Date</option>
                <option value="reports">Sort by Reports</option>
              </select>
              
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
              
              <Button 
                variant="outline" 
                fullWidth
                onClick={() => setShowAcknowledgeModal(true)}
              >
                Acknowledge All
              </Button>
            </div>
          </Card>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Total Alerts</p>
            <p className="text-lg md:text-2xl font-bold text-primary">{stats.total}</p>
          </Card>
          <Card className="p-3 md:p-4 border-l-4 border-danger">
            <p className="text-xs text-gray-400 mb-1">Critical</p>
            <p className="text-lg md:text-2xl font-bold text-danger">{stats.critical}</p>
          </Card>
          <Card className="p-3 md:p-4 border-l-4 border-warning">
            <p className="text-xs text-gray-400 mb-1">High</p>
            <p className="text-lg md:text-2xl font-bold text-warning">{stats.high}</p>
          </Card>
          <Card className="p-3 md:p-4 border-l-4 border-primary">
            <p className="text-xs text-gray-400 mb-1">Medium</p>
            <p className="text-lg md:text-2xl font-bold text-primary">{stats.medium}</p>
          </Card>
        </div>

        {/* Alert List */}
        <AlertList onSelectAlert={setSelectedAlert} filter={filter} sortBy={sortBy} timeRange={timeRange} />

        {/* Alert Detail Modal */}
        {selectedAlert && (
          <AlertDetail
            alert={selectedAlert}
            onClose={() => setSelectedAlert(null)}
          />
        )}
      </div>

      {/* Acknowledge All Modal */}
      <Modal
        isOpen={showAcknowledgeModal}
        onClose={() => !acknowledgeLoading && setShowAcknowledgeModal(false)}
        type="warning"
        title="Acknowledge All Alerts"
        message={
          <div className="space-y-4">
            <p className="text-gray-600">
              This will mark all {stats.total} alerts as acknowledged. This action cannot be undone.
            </p>
            
            {acknowledgeLoading && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span>Processing...</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-primary animate-pulse" style={{ width: '100%' }} />
                </div>
              </div>
            )}
            
            <div className="flex gap-3 pt-4">
              <Button
                variant="outline"
                onClick={() => setShowAcknowledgeModal(false)}
                disabled={acknowledgeLoading}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleAcknowledgeAll}
                disabled={acknowledgeLoading}
              >
                {acknowledgeLoading ? 'Processing...' : 'Acknowledge All'}
              </Button>
            </div>
          </div>
        }
      />
    </div>
  );
};

export default Alerts;