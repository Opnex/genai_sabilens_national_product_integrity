import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import ConsumerBottomNav from '../../components/layout/ConsumerBottomNav';
import { getUserScanHistory, clearScanHistory, generateMockScan, saveScanToHistory } from '../../services/scanHistory';
import Modal from '../../components/common/Modal';

const ScanHistory = () => {
  const navigate = useNavigate();
  const [scans, setScans] = useState([]);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedScan, setSelectedScan] = useState(null);
  const [showClearModal, setShowClearModal] = useState(false);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [sortOrder, setSortOrder] = useState('newest');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadScans();
  }, []);

  const loadScans = () => {
    setIsLoading(true);
    try {
      const history = getUserScanHistory();
      setScans(history);
      
      if (history.length === 0) {
        addMockScans();
      }
    } catch (error) {
      console.error('Error loading scans:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const addMockScans = () => {
    try {
      for (let i = 0; i < 8; i++) {
        const mockScan = generateMockScan(Math.random() > 0.3);
        saveScanToHistory(mockScan);
      }
      setTimeout(() => {
        const updatedHistory = getUserScanHistory();
        setScans(updatedHistory);
      }, 100);
    } catch (error) {
      console.error('Error adding mock scans:', error);
    }
  };

  const getFilteredScans = () => {
    let filtered = [...scans];
    
    if (filter !== 'all') {
      filtered = filtered.filter(scan => scan.status === filter);
    }
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(scan => 
        (scan.product?.toLowerCase() || '').includes(term) ||
        (scan.manufacturer?.toLowerCase() || '').includes(term) ||
        (scan.category?.toLowerCase() || '').includes(term)
      );
    }
    
    filtered.sort((a, b) => {
      const dateA = new Date(a.timestamp || a.date || 0).getTime();
      const dateB = new Date(b.timestamp || b.date || 0).getTime();
      return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
    });
    
    return filtered;
  };

  const handleScanClick = (scan) => {
    setSelectedScan(scan);
  };

  const handleViewDetails = () => {
    if (selectedScan) {
      if (selectedScan.status === 'authentic') {
        navigate('/scan/safe');
      } else if (selectedScan.status === 'fake') {
        navigate('/scan/fake');
      } else {
        navigate('/scan/caution');
      }
    }
  };

  const handleClearHistory = () => {
    try {
      clearScanHistory();
      setScans([]);
      setShowClearModal(false);
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  const getStatusBadge = (status) => {
    switch(status) {
      case 'authentic':
        return <span className="px-3 py-1 bg-success/10 text-success text-xs rounded-full font-medium">Authentic</span>;
      case 'caution':
        return <span className="px-3 py-1 bg-warning/10 text-warning text-xs rounded-full font-medium">Caution</span>;
      case 'fake':
        return <span className="px-3 py-1 bg-danger/10 text-danger text-xs rounded-full font-medium">Fake</span>;
      default:
        return null;
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'authentic':
        return <Icon name="CheckCircle" size={20} className="text-success" library="fi" />;
      case 'caution':
        return <Icon name="AlertTriangle" size={20} className="text-warning" library="fi" />;
      case 'fake':
        return <Icon name="XCircle" size={20} className="text-danger" library="fi" />;
      default:
        return <Icon name="HelpCircle" size={20} className="text-gray-400" library="fi" />;
    }
  };

  const filteredScans = getFilteredScans();

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <div className="bg-white px-6 pt-12 pb-4 sticky top-0 z-10 shadow-soft">
        <div className="flex items-center gap-4 mb-4">
          <button 
            onClick={() => navigate('/home')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Icon name="ArrowLeft" size={20} className="text-gray-600" library="fi" />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Scan History</h1>
        </div>

        {/* Search Bar */}
        <div className="relative mb-4">
          <Icon name="Search" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" library="fi" />
          <input
            type="text"
            placeholder="Search products, brands..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>

        {/* Filter Bar */}
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filter === 'all' 
                ? 'bg-primary text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All ({scans.length})
          </button>
          <button
            onClick={() => setFilter('authentic')}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filter === 'authentic' 
                ? 'bg-success text-white' 
                : 'bg-success/10 text-success hover:bg-success/20'
            }`}
          >
            Authentic
          </button>
          <button
            onClick={() => setFilter('caution')}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filter === 'caution' 
                ? 'bg-warning text-white' 
                : 'bg-warning/10 text-warning hover:bg-warning/20'
            }`}
          >
            Caution
          </button>
          <button
            onClick={() => setFilter('fake')}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filter === 'fake' 
                ? 'bg-danger text-white' 
                : 'bg-danger/10 text-danger hover:bg-danger/20'
            }`}
          >
            Fake
          </button>
          
          <button
            onClick={() => setShowFilterModal(true)}
            className="p-2 bg-gray-100 rounded-full text-gray-600 hover:bg-gray-200 transition-colors"
          >
            <Icon name="Sliders" size={18} library="fi" />
          </button>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="px-6 py-4">
        <div className="grid grid-cols-4 gap-3">
          <Card className="p-3 text-center">
            <p className="text-xl font-bold text-primary">{scans.length}</p>
            <p className="text-xs text-gray-400">Total</p>
          </Card>
          <Card className="p-3 text-center">
            <p className="text-xl font-bold text-success">{scans.filter(s => s.status === 'authentic').length}</p>
            <p className="text-xs text-gray-400">Safe</p>
          </Card>
          <Card className="p-3 text-center">
            <p className="text-xl font-bold text-warning">{scans.filter(s => s.status === 'caution').length}</p>
            <p className="text-xs text-gray-400">Caution</p>
          </Card>
          <Card className="p-3 text-center">
            <p className="text-xl font-bold text-danger">{scans.filter(s => s.status === 'fake').length}</p>
            <p className="text-xs text-gray-400">Fake</p>
          </Card>
        </div>
      </div>

      {/* Scans List */}
      <div className="px-6 py-2">
        {isLoading ? (
          <Card className="text-center py-12">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-500">Loading your scan history...</p>
          </Card>
        ) : filteredScans.length > 0 ? (
          <div className="space-y-3">
            {filteredScans.map((scan) => (
              <Card 
                key={scan.id} 
                className="cursor-pointer hover:shadow-card transition-all hover:scale-[1.02] active:scale-[0.98] p-3"
                onClick={() => handleScanClick(scan)}
              >
                <div className="flex gap-3">
                  {/* Product Image */}
                  <div className="w-20 h-20 rounded-xl overflow-hidden bg-gray-100 flex-shrink-0">
                    {scan.productImage ? (
                      <img 
                        src={scan.productImage} 
                        alt={scan.product}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200';
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Icon name="Package" size={32} className="text-gray-300" library="fi" />
                      </div>
                    )}
                  </div>
                  
                  {/* Scan Details */}
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                      <h3 className="font-semibold text-gray-900">{scan.product}</h3>
                      {getStatusBadge(scan.status)}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-1 mt-1 text-xs">
                      {scan.category && (
                        <div className="flex items-center gap-1">
                          <Icon name="Tag" size={10} className="text-gray-400" library="fi" />
                          <span className="text-gray-500 truncate">{scan.category}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-1">
                        <Icon name="Clock" size={10} className="text-gray-400" library="fi" />
                        <span className="text-gray-500 text-xs">{scan.time || 'Recently'}</span>
                      </div>
                    </div>
                    
                    {/* Similarity Bar for non-authentic items */}
                    {scan.status !== 'authentic' && scan.similarity && (
                      <div className="mt-2">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-gray-400">Similarity</span>
                          <span className={scan.status === 'fake' ? 'text-danger' : 'text-warning'}>
                            {scan.similarity}%
                          </span>
                        </div>
                        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${scan.status === 'fake' ? 'bg-danger' : 'bg-warning'}`}
                            style={{ width: `${scan.similarity}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="text-center py-12">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Icon name="Clock" size={32} className="text-gray-400" library="fi" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No scans yet</h3>
            <p className="text-sm text-gray-400 mb-6">Start scanning products to build your history</p>
            <Button 
              variant="primary" 
              onClick={() => navigate('/scan')}
              icon="Camera"
            >
              Scan Your First Product
            </Button>
          </Card>
        )}
      </div>

      {/* Clear History Button */}
      {scans.length > 0 && (
        <div className="px-6 py-4">
          <button
            onClick={() => setShowClearModal(true)}
            className="w-full py-3 text-danger border border-danger/20 rounded-xl hover:bg-danger/5 transition-colors flex items-center justify-center gap-2"
          >
            <Icon name="Trash2" size={18} library="fi" />
            Clear History
          </button>
        </div>
      )}

      {/* Scan Detail Modal */}
      <Modal
        isOpen={!!selectedScan}
        onClose={() => setSelectedScan(null)}
        type="custom"
        title={
          <div className="flex items-center gap-2">
            {selectedScan && getStatusIcon(selectedScan.status)}
            <span>Scan Details</span>
          </div>
        }
        message={
          selectedScan && (
            <div className="space-y-4">
              <div className="text-center">
                {/* Product Image in Modal */}
                <div className="w-32 h-32 mx-auto mb-3 rounded-xl overflow-hidden border border-gray-200">
                  <img 
                    src={selectedScan.productImage || 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200'} 
                    alt={selectedScan.product}
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-1">{selectedScan.product}</h3>
                {getStatusBadge(selectedScan.status)}
              </div>
              
              <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Date & Time</span>
                  <span className="text-sm font-medium">{selectedScan.time || 'Recently'}</span>
                </div>
                {selectedScan.category && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Category</span>
                    <span className="text-sm font-medium">{selectedScan.category}</span>
                  </div>
                )}
                {selectedScan.manufacturer && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Manufacturer</span>
                    <span className="text-sm font-medium">{selectedScan.manufacturer}</span>
                  </div>
                )}
                {selectedScan.nafdacNumber && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">NAFDAC Number</span>
                    <span className="text-sm font-mono font-medium">{selectedScan.nafdacNumber}</span>
                  </div>
                )}
                {selectedScan.batchNumber && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Batch Number</span>
                    <span className="text-sm font-mono font-medium">{selectedScan.batchNumber}</span>
                  </div>
                )}
                {selectedScan.expiryDate && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Expiry Date</span>
                    <span className="text-sm font-medium">{selectedScan.expiryDate}</span>
                  </div>
                )}
                {selectedScan.location && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Location</span>
                    <span className="text-sm font-medium">{selectedScan.location}</span>
                  </div>
                )}
              </div>

              <Button
                variant="primary"
                fullWidth
                onClick={handleViewDetails}
              >
                View Full Report
              </Button>
            </div>
          )
        }
      />

      {/* Clear History Confirmation Modal */}
      <Modal
        isOpen={showClearModal}
        onClose={() => setShowClearModal(false)}
        type="warning"
        title="Clear History"
        message={
          <div>
            <p className="text-gray-600 mb-4">Are you sure you want to clear all scan history? This action cannot be undone.</p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setShowClearModal(false)}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleClearHistory}
              >
                Clear All
              </Button>
            </div>
          </div>
        }
      />

      {/* Filter Options Modal */}
      <Modal
        isOpen={showFilterModal}
        onClose={() => setShowFilterModal(false)}
        type="info"
        title="Sort Options"
        message={
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Sort by</p>
              <div className="space-y-2">
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="sort"
                    checked={sortOrder === 'newest'}
                    onChange={() => setSortOrder('newest')}
                    className="w-4 h-4 text-primary"
                  />
                  <span className="text-sm">Newest first</span>
                </label>
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="sort"
                    checked={sortOrder === 'oldest'}
                    onChange={() => setSortOrder('oldest')}
                    className="w-4 h-4 text-primary"
                  />
                  <span className="text-sm">Oldest first</span>
                </label>
              </div>
            </div>
          </div>
        }
      />

      <ConsumerBottomNav />
    </div>
  );
};

export default ScanHistory;