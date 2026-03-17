import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NAFDACSidebar from '../../components/layout/NAFDACSidebar';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import MobileNAFDACNav from '../../components/layout/MobileNAFDACNav';

const ExportData = () => {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [selectedDataType, setSelectedDataType] = useState('reports');
  const [dateRange, setDateRange] = useState('30');
  const [exportFormat, setExportFormat] = useState('csv');
  const [showExportModal, setShowExportModal] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportComplete, setExportComplete] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleExport = () => {
    setExporting(true);
    setExportProgress(0);
    
    const interval = setInterval(() => {
      setExportProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setExporting(false);
            setExportComplete(true);
          }, 500);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleExportComplete = () => {
    setExportComplete(false);
    setShowExportModal(false);
    setExportProgress(0);
    
    // Simulate file download
    setTimeout(() => {
      alert(`Export completed: ${selectedDataType} data exported successfully`);
    }, 100);
  };

  // Mock data stats
  const stats = {
    reports: 1247,
    cases: 356,
    vendors: 89,
    analytics: '12MB'
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
                <Icon name="Download" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">Export Data</span>
            </div>
            <div className="w-10" /> {/* Spacer */}
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
        <div className="mb-8">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Export Data</h1>
          <p className="text-sm text-gray-500 mt-1">Export NAFDAC data for analysis and reporting</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Total Reports</p>
            <p className="text-lg md:text-2xl font-bold text-primary">{stats.reports}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Active Cases</p>
            <p className="text-lg md:text-2xl font-bold text-warning">{stats.cases}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Vendors Tracked</p>
            <p className="text-lg md:text-2xl font-bold text-success">{stats.vendors}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Data Size</p>
            <p className="text-lg md:text-2xl font-bold text-danger">{stats.analytics}</p>
          </Card>
        </div>

        {/* Export Options */}
        <Card className="p-4 md:p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Export Options</h2>
          
          <div className="space-y-6">
            {/* Data Type Selection */}
            <div>
              <label className="text-sm text-gray-500 mb-2 block">Select Data to Export</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button
                  onClick={() => setSelectedDataType('reports')}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selectedDataType === 'reports'
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 hover:border-primary/50'
                  }`}
                >
                  <Icon name="AlertTriangle" size={24} className={selectedDataType === 'reports' ? 'text-primary' : 'text-gray-400'} library="fi" />
                  <p className="font-medium text-sm mt-2">Reports</p>
                  <p className="text-xs text-gray-400">{stats.reports} records</p>
                </button>

                <button
                  onClick={() => setSelectedDataType('cases')}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selectedDataType === 'cases'
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 hover:border-primary/50'
                  }`}
                >
                  <Icon name="Folder" size={24} className={selectedDataType === 'cases' ? 'text-primary' : 'text-gray-400'} library="fi" />
                  <p className="font-medium text-sm mt-2">Cases</p>
                  <p className="text-xs text-gray-400">{stats.cases} records</p>
                </button>

                <button
                  onClick={() => setSelectedDataType('vendors')}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selectedDataType === 'vendors'
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 hover:border-primary/50'
                  }`}
                >
                  <Icon name="Users" size={24} className={selectedDataType === 'vendors' ? 'text-primary' : 'text-gray-400'} library="fi" />
                  <p className="font-medium text-sm mt-2">Vendors</p>
                  <p className="text-xs text-gray-400">{stats.vendors} records</p>
                </button>

                <button
                  onClick={() => setSelectedDataType('analytics')}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selectedDataType === 'analytics'
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 hover:border-primary/50'
                  }`}
                >
                  <Icon name="PieChart" size={24} className={selectedDataType === 'analytics' ? 'text-primary' : 'text-gray-400'} library="fi" />
                  <p className="font-medium text-sm mt-2">Analytics</p>
                  <p className="text-xs text-gray-400">Summary data</p>
                </button>
              </div>
            </div>

            {/* Date Range */}
            <div>
              <label className="text-sm text-gray-500 mb-2 block">Date Range</label>
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="w-full md:w-64 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 90 days</option>
                <option value="365">Last year</option>
                <option value="all">All time</option>
              </select>
            </div>

            {/* Export Format */}
            <div>
              <label className="text-sm text-gray-500 mb-2 block">Export Format</label>
              <div className="flex flex-wrap gap-3">
                <label className="flex items-center gap-2 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="format"
                    value="csv"
                    checked={exportFormat === 'csv'}
                    onChange={(e) => setExportFormat(e.target.value)}
                    className="w-4 h-4 text-primary"
                  />
                  <div>
                    <p className="font-medium">CSV</p>
                    <p className="text-xs text-gray-400">Compatible with Excel</p>
                  </div>
                </label>

                <label className="flex items-center gap-2 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="format"
                    value="json"
                    checked={exportFormat === 'json'}
                    onChange={(e) => setExportFormat(e.target.value)}
                    className="w-4 h-4 text-primary"
                  />
                  <div>
                    <p className="font-medium">JSON</p>
                    <p className="text-xs text-gray-400">For developers</p>
                  </div>
                </label>

                <label className="flex items-center gap-2 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="format"
                    value="pdf"
                    checked={exportFormat === 'pdf'}
                    onChange={(e) => setExportFormat(e.target.value)}
                    className="w-4 h-4 text-primary"
                  />
                  <div>
                    <p className="font-medium">PDF</p>
                    <p className="text-xs text-gray-400">Printable report</p>
                  </div>
                </label>
              </div>
            </div>

            {/* Export Button */}
            <div className="pt-4 border-t border-gray-100">
              <Button
                variant="primary"
                onClick={() => setShowExportModal(true)}
                icon="Download"
                fullWidth={windowWidth < 640}
              >
                Export Data
              </Button>
            </div>
          </div>
        </Card>

        {/* Recent Exports */}
        <Card className="mt-6 p-4 md:p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Recent Exports</h3>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <Icon name="FileText" size={18} className="text-primary" library="fi" />
                <div>
                  <p className="text-sm font-medium">reports_2024_01_15.csv</p>
                  <p className="text-xs text-gray-400">2.4 MB • Jan 15, 2024</p>
                </div>
              </div>
              <button className="p-2 hover:bg-gray-200 rounded-lg">
                <Icon name="Download" size={16} className="text-gray-400" library="fi" />
              </button>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <Icon name="FileText" size={18} className="text-primary" library="fi" />
                <div>
                  <p className="text-sm font-medium">cases_2024_01_14.json</p>
                  <p className="text-xs text-gray-400">856 KB • Jan 14, 2024</p>
                </div>
              </div>
              <button className="p-2 hover:bg-gray-200 rounded-lg">
                <Icon name="Download" size={16} className="text-gray-400" library="fi" />
              </button>
            </div>
          </div>
        </Card>
      </div>

      {/* Export Modal */}
      <Modal
        isOpen={showExportModal}
        onClose={() => !exporting && setShowExportModal(false)}
        type={exportComplete ? 'success' : 'info'}
        title={exportComplete ? 'Export Complete' : 'Export Data'}
        message={
          exportComplete ? (
            <div className="text-center">
              <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Icon name="CheckCircle" size={32} className="text-success" library="fi" />
              </div>
              <p className="text-gray-600 mb-2">
                Your data has been exported successfully
              </p>
              <p className="text-sm text-gray-400">
                File: {selectedDataType}_{new Date().toISOString().split('T')[0]}.{exportFormat}
              </p>
              <Button
                variant="primary"
                onClick={handleExportComplete}
                className="mt-4"
              >
                Download File
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-gray-600">
                Preparing to export {selectedDataType} data...
              </p>
              
              {exporting && (
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span>Processing data...</span>
                    <span>{exportProgress}%</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary transition-all duration-200"
                      style={{ width: `${exportProgress}%` }}
                    />
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
                  {exporting ? 'Exporting...' : 'Confirm Export'}
                </Button>
              </div>
            </div>
          )
        }
      />
    </div>
  );
};

export default ExportData;