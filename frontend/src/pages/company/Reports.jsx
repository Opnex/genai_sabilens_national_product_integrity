import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CompanySidebar from '../../components/layout/CompanySidebar';
import ReportsTable from '../../components/company/Reports/ReportsTable';
import ForensicDetail from '../../components/company/Reports/ForensicDetail';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import MobileCompanyNav from '../../components/layout/MobileCompanyNav';
import Modal from '../../components/common/Modal';
import Button from '../../components/common/Button';
import { exportReports, exportReportAsPDF } from '../../services/downloadService';

const Reports = () => {
  const navigate = useNavigate();
  const [selectedReport, setSelectedReport] = useState(null);
  const [companyReports, setCompanyReports] = useState([]);
  const [filteredReports, setFilteredReports] = useState([]);
  const [filters, setFilters] = useState({
    category: 'all',
    severity: 'all',
    dateRange: 'all'
  });
  const [loading, setLoading] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [showFilters, setShowFilters] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportFormat, setExportFormat] = useState('csv');
  const [exportLoading, setExportLoading] = useState(false);

  // Get current user
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  const companyId = currentUser.companyId;

  useEffect(() => {
    loadCompanyReports();
    
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
      if (window.innerWidth >= 768) {
        setShowFilters(true);
      }
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const loadCompanyReports = () => {
    setLoading(true);
    
    // Get company details
    const companies = JSON.parse(localStorage.getItem('companies') || '[]');
    const company = companies.find(c => c.id === companyId);
    
    if (!company) return;

    // Get all scans from all users
    const allUsers = JSON.parse(localStorage.getItem('users') || '[]');
    const reports = [];
    
    allUsers.forEach(user => {
      const historyKey = `scanHistory_${user.phone}`;
      const userScans = JSON.parse(localStorage.getItem(historyKey) || '[]');
      
      // Filter scans that match this company
      const companyScans = userScans.filter(scan => 
        scan.manufacturer?.toLowerCase().includes(company.name.toLowerCase()) ||
        scan.product?.toLowerCase().includes(company.name.toLowerCase())
      ).map(scan => ({
        ...scan,
        id: scan.id || `report_${Date.now()}_${Math.random()}`,
        companyId: company.id,
        companyName: company.name
      }));
      
      reports.push(...companyScans);
    });
    
    // Sort by date (newest first)
    reports.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    setCompanyReports(reports);
    setFilteredReports(reports);
    setLoading(false);
  };

  const applyFilters = () => {
    let filtered = [...companyReports];
    
    if (filters.severity !== 'all') {
      filtered = filtered.filter(r => r.status === filters.severity);
    }
    
    if (filters.category !== 'all') {
      filtered = filtered.filter(r => r.category?.toLowerCase() === filters.category.toLowerCase());
    }
    
    if (filters.dateRange !== 'all') {
      const now = new Date();
      const days = filters.dateRange === '7' ? 7 : filters.dateRange === '30' ? 30 : 90;
      const cutoff = new Date(now.setDate(now.getDate() - days));
      filtered = filtered.filter(r => new Date(r.timestamp) > cutoff);
    }
    
    setFilteredReports(filtered);
  };

  useEffect(() => {
    applyFilters();
  }, [filters]);

  const handleExport = () => {
    setExportLoading(true);
    
    setTimeout(() => {
      if (exportFormat === 'csv') {
        exportReports(filteredReports, `counterfeit-reports-${new Date().toISOString().split('T')[0]}.csv`);
      } else if (exportFormat === 'pdf') {
        // For PDF, export each report individually or combine them
        filteredReports.slice(0, 10).forEach(report => {
          exportReportAsPDF(report);
        });
      }
      
      setExportLoading(false);
      setShowExportModal(false);
    }, 1000);
  };

  const stats = {
    total: companyReports.length,
    critical: companyReports.filter(r => r.status === 'fake').length,
    high: companyReports.filter(r => r.status === 'caution').length,
    medium: companyReports.filter(r => r.status === 'authentic').length
  };

  // Responsive grid classes
  const getStatsGridClass = () => {
    if (windowWidth < 640) return 'grid-cols-2';
    if (windowWidth < 1024) return 'grid-cols-4';
    return 'grid-cols-4';
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
              <span className="font-bold text-lg">Reports</span>
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
      <MobileCompanyNav 
        isOpen={isMobileMenuOpen} 
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* Desktop Sidebar */}
      {windowWidth >= 768 && <CompanySidebar />}
      
      {/* Main Content */}
      <div className={`${windowWidth >= 768 ? 'lg:ml-64' : ''} ${windowWidth < 768 ? 'pt-16' : 'pt-8'} px-4 md:px-6 lg:px-8 pb-8`}>
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Counterfeit Reports</h1>
          
          {/* Desktop Filters */}
          {windowWidth >= 768 && (
            <div className="flex flex-wrap gap-3">
              <select 
                className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm"
                value={filters.severity}
                onChange={(e) => setFilters({...filters, severity: e.target.value})}
              >
                <option value="all">All Severities</option>
                <option value="fake">Counterfeit</option>
                <option value="caution">Suspicious</option>
                <option value="authentic">Authentic</option>
              </select>
              
              <select 
                className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm"
                value={filters.dateRange}
                onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
              >
                <option value="all">All Time</option>
                <option value="7">Last 7 Days</option>
                <option value="30">Last 30 Days</option>
                <option value="90">Last 90 Days</option>
              </select>
              
              <button 
                onClick={() => setShowExportModal(true)}
                className="px-4 py-2 bg-primary text-white rounded-xl flex items-center gap-2 hover:bg-primary-dark transition-colors text-sm"
                disabled={filteredReports.length === 0}
              >
                <Icon name="Download" size={18} library="fi" />
                <span className="hidden sm:inline">Export ({filteredReports.length})</span>
              </button>
            </div>
          )}
        </div>

        {/* Mobile Filters Collapsible */}
        {windowWidth < 768 && showFilters && (
          <Card className="mb-6 p-4">
            <div className="space-y-3">
              <select 
                className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm"
                value={filters.severity}
                onChange={(e) => setFilters({...filters, severity: e.target.value})}
              >
                <option value="all">All Severities</option>
                <option value="fake">Counterfeit</option>
                <option value="caution">Suspicious</option>
                <option value="authentic">Authentic</option>
              </select>
              
              <select 
                className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm"
                value={filters.dateRange}
                onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
              >
                <option value="all">All Time</option>
                <option value="7">Last 7 Days</option>
                <option value="30">Last 30 Days</option>
                <option value="90">Last 90 Days</option>
              </select>
              
              <button 
                onClick={() => setShowExportModal(true)}
                className="w-full px-4 py-3 bg-primary text-white rounded-xl flex items-center justify-center gap-2 hover:bg-primary-dark transition-colors text-sm"
                disabled={filteredReports.length === 0}
              >
                <Icon name="Download" size={18} library="fi" />
                Export Reports ({filteredReports.length})
              </button>
            </div>
          </Card>
        )}
        
        {/* Stats Cards */}
        <div className={`grid ${getStatsGridClass()} gap-3 md:gap-4 mb-6`}>
          <Card className="p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Total Reports</p>
            <p className="text-lg md:text-2xl font-bold text-gray-900">{stats.total}</p>
          </Card>
          <Card className="p-3 md:p-4 border-l-4 border-danger">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Counterfeit</p>
            <p className="text-lg md:text-2xl font-bold text-danger">{stats.critical}</p>
          </Card>
          <Card className="p-3 md:p-4 border-l-4 border-warning">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Suspicious</p>
            <p className="text-lg md:text-2xl font-bold text-warning">{stats.high}</p>
          </Card>
          <Card className="p-3 md:p-4 border-l-4 border-success">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Authentic</p>
            <p className="text-lg md:text-2xl font-bold text-success">{stats.medium}</p>
          </Card>
        </div>

        {/* Reports Table */}
        {loading ? (
          <Card className="p-8 text-center">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-500">Loading your reports...</p>
          </Card>
        ) : filteredReports.length > 0 ? (
          <div className="overflow-x-auto -mx-4 md:mx-0">
            <div className="inline-block min-w-full align-middle">
              <div className="md:hidden">
                {/* Mobile Card View */}
                <div className="space-y-3 px-4">
                  {filteredReports.slice(0, 10).map((report) => (
                    <Card 
                      key={report.id} 
                      className="p-4 cursor-pointer hover:shadow-card transition-all"
                      onClick={() => setSelectedReport(report)}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                          report.status === 'authentic' ? 'bg-success/10' :
                          report.status === 'caution' ? 'bg-warning/10' : 'bg-danger/10'
                        }`}>
                          <Icon 
                            name={report.status === 'authentic' ? 'CheckCircle' : report.status === 'caution' ? 'AlertTriangle' : 'XCircle'} 
                            size={20} 
                            className={
                              report.status === 'authentic' ? 'text-success' :
                              report.status === 'caution' ? 'text-warning' : 'text-danger'
                            } 
                            library="fi" 
                          />
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between items-start">
                            <h3 className="font-medium text-gray-900">{report.product}</h3>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              report.status === 'authentic' ? 'bg-success/10 text-success' :
                              report.status === 'caution' ? 'bg-warning/10 text-warning' : 'bg-danger/10 text-danger'
                            }`}>
                              {report.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mt-1">{report.location}</p>
                          <div className="flex justify-between items-center mt-2 text-xs text-gray-400">
                            <span>{report.date || new Date(report.timestamp).toLocaleDateString()}</span>
                            <span>Score: {report.similarity || 0}%</span>
                          </div>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
              
              {/* Desktop Table View */}
              <div className="hidden md:block">
                <ReportsTable 
                  reports={filteredReports} 
                  onRowClick={setSelectedReport} 
                />
              </div>
            </div>
          </div>
        ) : (
          <Card className="p-8 md:p-12 text-center">
            <Icon name="FileText" size={48} className="text-gray-300 mx-auto mb-4" library="fi" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Reports Found</h3>
            <p className="text-sm text-gray-400">There are no reports matching your criteria.</p>
          </Card>
        )}
      </div>

      {/* Export Modal */}
      <Modal
        isOpen={showExportModal}
        onClose={() => !exportLoading && setShowExportModal(false)}
        type="info"
        title="Export Reports"
        message={
          <div className="space-y-4">
            <p className="text-gray-600">Choose export format:</p>
            
            <div className="space-y-2">
              <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <input
                    type="radio"
                    name="exportFormat"
                    value="csv"
                    checked={exportFormat === 'csv'}
                    onChange={(e) => setExportFormat(e.target.value)}
                    className="w-4 h-4 text-primary"
                  />
                  <div>
                    <p className="font-medium">CSV Format</p>
                    <p className="text-xs text-gray-400">Compatible with Excel, Google Sheets</p>
                  </div>
                </div>
                <Icon name="FileText" size={20} className="text-gray-400" library="fi" />
              </label>
              
              <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <input
                    type="radio"
                    name="exportFormat"
                    value="pdf"
                    checked={exportFormat === 'pdf'}
                    onChange={(e) => setExportFormat(e.target.value)}
                    className="w-4 h-4 text-primary"
                  />
                  <div>
                    <p className="font-medium">PDF Format</p>
                    <p className="text-xs text-gray-400">Printable reports (first 10 reports)</p>
                  </div>
                </div>
                <Icon name="File" size={20} className="text-gray-400" library="fi" />
              </label>
            </div>
            
            <p className="text-xs text-gray-400">
              Exporting {filteredReports.length} reports
            </p>
            
            <div className="flex gap-3 pt-4">
              <Button
                variant="outline"
                onClick={() => setShowExportModal(false)}
                disabled={exportLoading}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleExport}
                disabled={exportLoading}
              >
                {exportLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Exporting...
                  </div>
                ) : (
                  'Export Now'
                )}
              </Button>
            </div>
          </div>
        }
      />

      {/* Forensic Detail Modal */}
      {selectedReport && (
        <ForensicDetail
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
        />
      )}
    </div>
  );
};

export default Reports;