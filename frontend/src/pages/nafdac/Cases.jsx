import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NAFDACSidebar from '../../components/layout/NAFDACSidebar';
import CaseDetail from '../../components/nafdac/Cases/CaseDetail';
import Card from '../../components/common/Card';
import Icon from '../../components/common/Icon';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import MobileNAFDACNav from '../../components/layout/MobileNAFDACNav';

const Cases = () => {
  const navigate = useNavigate();
  const [selectedCase, setSelectedCase] = useState('CASE-2024-001');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const cases = [
    { id: 'CASE-2024-001', product: 'Malaria Tablets', location: 'Lagos', status: 'active', reports: 24, severity: 'critical', date: '2024-01-15' },
    { id: 'CASE-2024-002', product: 'Antibiotics', location: 'Kano', status: 'active', reports: 18, severity: 'high', date: '2024-01-14' },
    { id: 'CASE-2024-003', product: 'Pain Relievers', location: 'Abuja', status: 'closed', reports: 12, severity: 'medium', date: '2024-01-13' },
    { id: 'CASE-2024-004', product: 'Children\'s Vaccines', location: 'Port Harcourt', status: 'active', reports: 32, severity: 'critical', date: '2024-01-12' },
    { id: 'CASE-2024-005', product: 'Vitamin C', location: 'Ibadan', status: 'active', reports: 8, severity: 'low', date: '2024-01-11' },
    { id: 'CASE-2024-006', product: 'Antimalarial', location: 'Benin', status: 'pending', reports: 15, severity: 'high', date: '2024-01-10' },
  ];

  const filteredCases = cases.filter(c => {
    if (filter !== 'all' && c.status !== filter) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return c.product.toLowerCase().includes(term) || 
             c.location.toLowerCase().includes(term) ||
             c.id.toLowerCase().includes(term);
    }
    return true;
  });

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'critical': return 'text-danger bg-danger/10';
      case 'high': return 'text-warning bg-warning/10';
      case 'medium': return 'text-primary bg-primary/10';
      case 'low': return 'text-success bg-success/10';
      default: return 'text-gray-500 bg-gray-100';
    }
  };

  const stats = {
    total: cases.length,
    active: cases.filter(c => c.status === 'active').length,
    critical: cases.filter(c => c.severity === 'critical').length,
    evidence: '2.4 GB'
  };

  const handleExport = () => {
    setExporting(true);
    setExportProgress(0);
    
    const interval = setInterval(() => {
      setExportProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setExporting(false);
            setShowExportModal(false);
            alert('Case bundle exported successfully!');
          }, 500);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
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
                <Icon name="Folder" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">Evidence Cases</span>
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
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Evidence Cases</h1>
          
          {windowWidth >= 768 && (
            <div className="flex gap-3">
              <div className="relative">
                <Icon name="Search" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" library="fi" />
                <input
                  type="text"
                  placeholder="Search cases..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 w-64"
                />
              </div>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="all">All Cases</option>
                <option value="active">Active</option>
                <option value="pending">Pending</option>
                <option value="closed">Closed</option>
              </select>
              <Button 
                variant="primary" 
                icon="Download"
                onClick={() => setShowExportModal(true)}
              >
                Export
              </Button>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Total Cases</p>
            <p className="text-lg md:text-2xl font-bold text-primary">{stats.total}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Active Cases</p>
            <p className="text-lg md:text-2xl font-bold text-warning">{stats.active}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Critical</p>
            <p className="text-lg md:text-2xl font-bold text-danger">{stats.critical}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs text-gray-400 mb-1">Evidence Size</p>
            <p className="text-lg md:text-2xl font-bold text-success">{stats.evidence}</p>
          </Card>
        </div>

        {/* Mobile Search/Filter */}
        {windowWidth < 768 && (
          <div className="space-y-3 mb-4">
            <div className="relative">
              <Icon name="Search" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" library="fi" />
              <input
                type="text"
                placeholder="Search cases..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              <option value="all">All Cases</option>
              <option value="active">Active</option>
              <option value="pending">Pending</option>
              <option value="closed">Closed</option>
            </select>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Case List Sidebar */}
          <div className="lg:col-span-1">
            <Card>
              <h3 className="font-semibold text-lg mb-4 px-2">Active Cases ({filteredCases.length})</h3>
              <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
                {filteredCases.map((case_) => (
                  <button
                    key={case_.id}
                    onClick={() => setSelectedCase(case_.id)}
                    className={`w-full text-left p-3 rounded-lg transition-all ${
                      selectedCase === case_.id
                        ? 'bg-primary/10 text-primary border-l-4 border-primary'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <p className="font-medium text-sm">{case_.id}</p>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getSeverityColor(case_.severity)}`}>
                        {case_.severity}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600 mb-1">{case_.product}</p>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-400">{case_.location}</span>
                      <span className={case_.status === 'active' ? 'text-success' : 'text-gray-400'}>
                        {case_.reports} reports
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </Card>
          </div>

          {/* Case Detail */}
          <div className="lg:col-span-3">
            <CaseDetail caseId={selectedCase} />
          </div>
        </div>
      </div>

      {/* Export Modal */}
      <Modal
        isOpen={showExportModal}
        onClose={() => !exporting && setShowExportModal(false)}
        type="info"
        title="Export Case Bundle"
        message={
          <div className="space-y-4">
            <p className="text-gray-600">
              This will export all selected cases with evidence files.
            </p>
            
            <div className="space-y-2">
              <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <input type="checkbox" defaultChecked className="w-4 h-4 text-primary" />
                  <span className="text-sm">Include evidence images</span>
                </div>
                <span className="text-xs text-gray-400">156 files</span>
              </label>
              
              <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <input type="checkbox" defaultChecked className="w-4 h-4 text-primary" />
                  <span className="text-sm">Include forensic reports</span>
                </div>
                <span className="text-xs text-gray-400">42 files</span>
              </label>
              
              <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <input type="checkbox" defaultChecked className="w-4 h-4 text-primary" />
                  <span className="text-sm">Include case summaries</span>
                </div>
                <span className="text-xs text-gray-400">12 files</span>
              </label>
            </div>
            
            {exporting && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span>Creating export bundle...</span>
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
                {exporting ? 'Exporting...' : 'Export Bundle'}
              </Button>
            </div>
          </div>
        }
      />
    </div>
  );
};

export default Cases;