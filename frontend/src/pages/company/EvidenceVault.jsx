import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CompanySidebar from '../../components/layout/CompanySidebar';
import EvidenceList from '../../components/company/Evidence/EvidenceList';
import DownloadPanel from '../../components/company/Evidence/DownloadPanel';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import MobileCompanyNav from '../../components/layout/MobileCompanyNav';
import Modal from '../../components/common/Modal';
import { createEvidenceZip, getEvidenceFiles } from '../../services/downloadService';

const EvidenceVault = () => {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [selectedCase, setSelectedCase] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // grid or list
  const [filter, setFilter] = useState('all');
  const [showDownloadModal, setShowDownloadModal] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [downloadResult, setDownloadResult] = useState(null);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
      if (window.innerWidth < 640) {
        setViewMode('list');
      }
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Mock stats
  const stats = {
    total: 47,
    images: 156,
    reports: 42,
    size: '156 MB'
  };

  const handleCaseSelect = (caseId) => {
    setSelectedCase(caseId);
  };

  const handleDownloadAll = async () => {
    if (!selectedCase) return;
    
    setDownloading(true);
    setDownloadProgress(0);
    
    // Simulate download progress
    const interval = setInterval(() => {
      setDownloadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
    
    // Get evidence files for this case
    const files = getEvidenceFiles(selectedCase);
    
    // Create ZIP (simulated)
    const result = await createEvidenceZip(selectedCase, files);
    
    clearInterval(interval);
    setDownloadProgress(100);
    setDownloadResult(result);
    
    // Show success in modal
    setTimeout(() => {
      setDownloading(false);
      setDownloadProgress(0);
      setDownloadResult(null);
      setShowDownloadModal(false);
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
                <Icon name="Folder" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">Evidence Vault</span>
            </div>
            <button 
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <Icon name={viewMode === 'grid' ? 'List' : 'Grid'} size={20} className="text-gray-600" library="fi" />
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
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-gray-900">Evidence Vault</h1>
            <p className="text-sm text-gray-500 mt-1">Manage and download case evidence</p>
          </div>
          
          {windowWidth >= 768 && (
            <div className="flex gap-3">
              <select 
                className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="all">All Cases</option>
                <option value="critical">Critical</option>
                <option value="high">High Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="low">Low Risk</option>
              </select>
              
              <button 
                onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                className="p-2 bg-white border border-gray-200 rounded-xl hover:bg-gray-50"
                title={viewMode === 'grid' ? 'Switch to list view' : 'Switch to grid view'}
              >
                <Icon name={viewMode === 'grid' ? 'List' : 'Grid'} size={20} className="text-gray-600" library="fi" />
              </button>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
          <Card className="p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Total Cases</p>
            <p className="text-lg md:text-2xl font-bold text-primary">{stats.total}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Evidence Images</p>
            <p className="text-lg md:text-2xl font-bold text-success">{stats.images}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Reports</p>
            <p className="text-lg md:text-2xl font-bold text-warning">{stats.reports}</p>
          </Card>
          <Card className="p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-400 mb-1">Total Size</p>
            <p className="text-lg md:text-2xl font-bold text-danger">{stats.size}</p>
          </Card>
        </div>

        {/* Mobile Filters */}
        {windowWidth < 768 && (
          <div className="mb-4">
            <select 
              className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="all">All Cases</option>
              <option value="critical">Critical</option>
              <option value="high">High Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="low">Low Risk</option>
            </select>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Evidence List */}
          <div className="lg:col-span-2">
            <EvidenceList 
              viewMode={viewMode}
              filter={filter}
              onCaseSelect={handleCaseSelect}
            />
          </div>
          
          {/* Download Panel - Desktop */}
          {windowWidth >= 1024 && (
            <div className="lg:col-span-1">
              <DownloadPanel 
                selectedCase={selectedCase}
                onDownloadAll={() => setShowDownloadModal(true)}
              />
            </div>
          )}
        </div>

        {/* Mobile Download Panel */}
        {windowWidth < 1024 && selectedCase && (
          <Card className="fixed bottom-0 left-0 right-0 z-50 p-4 rounded-t-2xl shadow-soft bg-white border-t border-gray-200 animate-slideUp">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Selected Case</p>
                <p className="text-xs text-gray-400">{selectedCase}</p>
              </div>
              <Button 
                variant="primary" 
                size="sm" 
                icon="Download"
                onClick={() => setShowDownloadModal(true)}
              >
                Download All
              </Button>
            </div>
          </Card>
        )}
      </div>

      {/* Download Modal */}
      <Modal
        isOpen={showDownloadModal}
        onClose={() => !downloading && setShowDownloadModal(false)}
        type={downloadResult ? 'success' : 'info'}
        title={downloadResult ? 'Download Complete' : 'Download Evidence'}
        message={
          downloadResult ? (
            <div className="text-center">
              <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Icon name="CheckCircle" size={32} className="text-success" library="fi" />
              </div>
              <p className="text-gray-600 mb-2">
                Successfully downloaded {downloadResult.fileCount} files
              </p>
              <p className="text-sm text-gray-400">
                Total size: {downloadResult.size}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-gray-600">
                Prepare to download all evidence files for case {selectedCase}
              </p>
              
              {downloading && (
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span>Creating ZIP archive...</span>
                    <span>{downloadProgress}%</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary transition-all duration-200"
                      style={{ width: `${downloadProgress}%` }}
                    />
                  </div>
                </div>
              )}
              
              <div className="flex gap-3 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setShowDownloadModal(false)}
                  disabled={downloading}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={handleDownloadAll}
                  disabled={downloading}
                  icon="Download"
                >
                  {downloading ? 'Creating ZIP...' : 'Download All'}
                </Button>
              </div>
            </div>
          )
        }
      />

      <style jsx>{`
        @keyframes slideUp {
          from {
            transform: translateY(100%);
          }
          to {
            transform: translateY(0);
          }
        }
        .animate-slideUp {
          animation: slideUp 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default EvidenceVault;