import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NAFDACSidebar from '../../components/layout/NAFDACSidebar';
import CategoryChart from '../../components/nafdac/Analytics/CategoryChart';
import TrendComparison from '../../components/nafdac/Analytics/TrendComparison';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import MobileNAFDACNav from '../../components/layout/MobileNAFDACNav';

const Analytics = () => {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [timeRange, setTimeRange] = useState('90d');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Mock data
  const stats = {
    totalCounterfeits: 1847,
    mostAffected: 'Drugs',
    fastestGrowing: 'Dairy',
    growth: '+28%'
  };

  const categoryStats = [
    { label: 'Fake Drugs %', value: '45%', change: '+8%', color: 'danger' },
    { label: 'Fake Dairy %', value: '25%', change: '+12%', color: 'warning' },
    { label: 'Fake Beverages %', value: '20%', change: '-3%', color: 'primary' },
    { label: 'Fake Cosmetics %', value: '10%', change: '+5%', color: 'success' },
  ];

  const handleExport = () => {
    setExporting(true);
    setTimeout(() => {
      setExporting(false);
      setShowExportModal(false);
      alert('Analytics report exported successfully!');
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
                <Icon name="PieChart" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">Analytics</span>
            </div>
            <button 
              onClick={() => setShowExportModal(true)}
              className="p-2 bg-primary/10 text-primary rounded-lg"
            >
              <Icon name="Download" size={20} library="fi" />
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
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Category Analytics</h1>
          
          {windowWidth >= 768 && (
            <div className="flex gap-3">
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
                <option value="180d">Last 6 Months</option>
                <option value="365d">Last Year</option>
              </select>
              
              <Button 
                variant="primary" 
                icon="Download"
                onClick={() => setShowExportModal(true)}
              >
                Export Report
              </Button>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4 mb-6">
          <Card className="p-4">
            <p className="text-sm text-gray-400 mb-2">Total Counterfeits</p>
            <p className="text-2xl md:text-3xl font-bold text-primary">{stats.totalCounterfeits}</p>
            <p className="text-xs text-success mt-2">↑ 12% from last quarter</p>
          </Card>
          
          <Card className="p-4">
            <p className="text-sm text-gray-400 mb-2">Most Affected Category</p>
            <p className="text-2xl md:text-3xl font-bold text-danger">{stats.mostAffected}</p>
            <p className="text-xs text-gray-500 mt-2">45% of total cases</p>
          </Card>
          
          <Card className="p-4 sm:col-span-2 lg:col-span-1">
            <p className="text-sm text-gray-400 mb-2">Fastest Growing</p>
            <p className="text-2xl md:text-3xl font-bold text-warning">{stats.fastestGrowing}</p>
            <p className="text-xs text-danger mt-2">{stats.growth} this quarter</p>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 mb-6">
          <div className="w-full overflow-x-auto">
            <CategoryChart 
              onCategoryClick={setSelectedCategory}
              timeRange={timeRange}
            />
          </div>
          <div className="w-full overflow-x-auto">
            <TrendComparison timeRange={timeRange} />
          </div>
        </div>

        {/* Category Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
          {categoryStats.map((stat, i) => (
            <Card 
              key={i} 
              className="p-3 md:p-4 cursor-pointer hover:shadow-card transition-all"
              onClick={() => setSelectedCategory(stat.label)}
            >
              <p className="text-xs text-gray-400 mb-1">{stat.label}</p>
              <p className="text-xl md:text-2xl font-bold text-gray-900">{stat.value}</p>
              <p className={`text-xs mt-2 ${stat.change.startsWith('+') ? 'text-danger' : 'text-success'}`}>
                {stat.change} from last quarter
              </p>
            </Card>
          ))}
        </div>

        {/* Mobile Export Button */}
        {windowWidth < 768 && (
          <Button 
            variant="primary" 
            icon="Download"
            fullWidth
            className="mt-4"
            onClick={() => setShowExportModal(true)}
          >
            Export Analytics Report
          </Button>
        )}
      </div>

      {/* Export Modal */}
      <Modal
        isOpen={showExportModal}
        onClose={() => !exporting && setShowExportModal(false)}
        type="info"
        title="Export Analytics Report"
        message={
          <div className="space-y-4">
            <p className="text-gray-600">
              This will generate a comprehensive analytics report for the selected time period.
            </p>
            
            <div className="space-y-2">
              <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <input type="checkbox" defaultChecked className="w-4 h-4 text-primary" />
                  <span className="text-sm">Include charts and graphs</span>
                </div>
              </label>
              
              <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <input type="checkbox" defaultChecked className="w-4 h-4 text-primary" />
                  <span className="text-sm">Include raw data tables</span>
                </div>
              </label>
              
              <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <input type="checkbox" className="w-4 h-4 text-primary" />
                  <span className="text-sm">Include trend analysis</span>
                </div>
              </label>
            </div>
            
            {exporting && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span>Generating report...</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-primary animate-pulse" style={{ width: '100%' }} />
                </div>
              </div>
            )}
            
            <div className="flex gap-3 pt-4">
              <Button
                variant="outline"
                onClick={() => setShowExportModal(false)}
                disabled={exporting}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleExport}
                disabled={exporting}
                icon="Download"
              >
                {exporting ? 'Generating...' : 'Export Report'}
              </Button>
            </div>
          </div>
        }
      />
    </div>
  );
};

export default Analytics;