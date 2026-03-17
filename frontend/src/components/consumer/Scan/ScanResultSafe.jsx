import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../common/Icon';
import Card from '../../common/Card';
import Button from '../../common/Button';
import { saveScanToHistory, getProductImage } from '../../../services/scanHistory';

const ScanResultSafe = ({ onBack, onReportIssue, onScanAnother }) => {
  const navigate = useNavigate();
  const [scanData, setScanData] = useState(null);

  useEffect(() => {
    // Get scan data from session storage
    const storedScan = sessionStorage.getItem('currentScan');
    let productImage = null;
    let isAuthentic = true;
    
    if (storedScan) {
      const parsed = JSON.parse(storedScan);
      productImage = parsed.productImage;
      isAuthentic = parsed.isAuthentic;
    }

    const scanData = {
      product: 'Nike Air Max 270',
      productImage: productImage || getProductImage('Nike Air Max 270', 'Footwear'),
      category: 'Footwear',
      manufacturer: 'Nike Inc.',
      nafdacNumber: 'B1-4022-XP',
      batchNumber: 'BATCH-2024-001',
      expiryDate: 'Oct 2026',
      status: 'authentic',
      similarity: 98,
      location: 'Lagos Market',
      time: 'Today, ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      verified: true,
      timestamp: new Date().toISOString()
    };
    
    setScanData(scanData);
    saveScanToHistory(scanData);
  }, []);

  if (!scanData) {
    return (
      <div className="px-6 py-8 flex justify-center">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="px-6 py-8">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="mb-6"
      >
        <Icon name="ArrowLeft" size={24} className="text-gray-500" library="fi" />
      </button>

      {/* Result Card */}
      <Card className="mb-6 border-2 border-success/20 overflow-hidden">
        {/* Success Banner */}
        <div className="bg-success/5 p-6 text-center border-b border-success/10">
          <div className="w-20 h-20 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Icon name="CheckCircle" size={40} className="text-success" library="fi" />
          </div>
          <h1 className="text-3xl font-bold text-success mb-2">SAFE TO BUY</h1>
          <p className="text-gray-600">
            This item has been verified against the official database and matches all safety records.
          </p>
        </div>

        {/* Product Image */}
        <div className="p-4 border-b border-gray-100">
          <div className="bg-gray-100 rounded-xl h-48 flex items-center justify-center overflow-hidden">
            <img 
              src={scanData.productImage} 
              alt={scanData.product}
              className="w-full h-full object-contain"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400';
              }}
            />
          </div>
        </div>

        {/* Voice Report */}
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Icon name="Volume2" size={18} className="text-primary" library="fi" />
              <span className="text-sm font-medium text-gray-700">Listen to Report</span>
            </div>
            <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
              4 Languages
            </span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
            <button className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center hover:bg-primary/20 transition-colors">
              <Icon name="Play" size={18} className="text-primary" library="fi" />
            </button>
            <div className="flex-1">
              <div className="h-2 bg-gray-200 rounded-full">
                <div className="w-0 h-2 bg-primary rounded-full" />
              </div>
            </div>
            <span className="text-xs text-gray-400">0:00</span>
            <button className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
              <Icon name="Download" size={16} className="text-gray-400" library="fi" />
            </button>
          </div>
        </div>

        {/* Verification Details */}
        <div className="p-4 space-y-4">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <Icon name="Shield" size={18} className="text-primary" library="fi" />
            VERIFICATION DETAILS
          </h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 p-3 rounded-xl">
              <p className="text-xs text-gray-400 mb-1">NAFDAC Number</p>
              <p className="font-mono font-medium text-sm">{scanData.nafdacNumber}</p>
              <div className="flex items-center gap-1 mt-1">
                <Icon name="Check" size={12} className="text-success" library="fi" />
                <span className="text-xs text-success">Verified</span>
              </div>
            </div>

            <div className="bg-gray-50 p-3 rounded-xl">
              <p className="text-xs text-gray-400 mb-1">Category</p>
              <p className="font-medium text-sm">{scanData.category}</p>
            </div>

            <div className="bg-gray-50 p-3 rounded-xl">
              <p className="text-xs text-gray-400 mb-1">Expiry Status</p>
              <p className="font-medium text-sm text-success">Valid</p>
              <p className="text-xs text-gray-400">{scanData.expiryDate}</p>
            </div>

            <div className="bg-gray-50 p-3 rounded-xl">
              <p className="text-xs text-gray-400 mb-1">Manufacturer</p>
              <p className="font-medium text-sm">{scanData.manufacturer}</p>
            </div>

            <div className="bg-gray-50 p-3 rounded-xl">
              <p className="text-xs text-gray-400 mb-1">Batch Number</p>
              <p className="font-mono font-medium text-sm">{scanData.batchNumber}</p>
            </div>

            <div className="bg-gray-50 p-3 rounded-xl">
              <p className="text-xs text-gray-400 mb-1">Location</p>
              <p className="font-medium text-sm">{scanData.location}</p>
            </div>
          </div>

          {/* AI Confidence Score */}
          <div className="bg-primary/5 p-3 rounded-xl">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-primary">AI Confidence Score</span>
              <span className="text-sm font-bold text-primary">{scanData.similarity}%</span>
            </div>
            <div className="h-2 bg-primary/10 rounded-full overflow-hidden">
              <div className="w-[98%] h-full bg-primary rounded-full" style={{ width: `${scanData.similarity}%` }} />
            </div>
          </div>

          {/* Quality Seals */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs bg-success/10 text-success px-3 py-1 rounded-full flex items-center gap-1">
              <Icon name="Check" size={12} className="text-success" library="fi" />
              NAFDAC Registered
            </span>
            <span className="text-xs bg-success/10 text-success px-3 py-1 rounded-full flex items-center gap-1">
              <Icon name="Check" size={12} className="text-success" library="fi" />
              Quality Assured
            </span>
            <span className="text-xs bg-success/10 text-success px-3 py-1 rounded-full flex items-center gap-1">
              <Icon name="Check" size={12} className="text-success" library="fi" />
              Batch Verified
            </span>
          </div>
        </div>

        {/* Report Issue */}
        <button 
          onClick={onReportIssue}
          className="w-full text-center text-sm text-gray-400 py-4 border-t border-gray-100 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
        >
          <Icon name="Flag" size={16} className="text-gray-400" library="fi" />
          Something looks wrong? Report Issue
        </button>
      </Card>

      <div className="space-y-3">
        <Button
          variant="primary"
          fullWidth
          onClick={onScanAnother}
          icon="Camera"
        >
          Scan Another Product
        </Button>

        <Button
          variant="outline"
          fullWidth
          onClick={() => navigate('/scan-history')}
          icon="Clock"
        >
          View Scan History
        </Button>

        <Button
          variant="outline"
          fullWidth
          onClick={() => navigate('/home')}
          icon="Home"
        >
          Back to Home
        </Button>
      </div>

      {/* Trust Badge */}
      <div className="mt-6 text-center">
        <div className="flex items-center justify-center gap-2 text-xs text-gray-400">
          <Icon name="Shield" size={14} className="text-primary" library="fi" />
          <span>Verified by SabiLens AI • Report ID: {Math.random().toString(36).substr(2, 9).toUpperCase()}</span>
        </div>
      </div>
    </div>
  );
};

export default ScanResultSafe;