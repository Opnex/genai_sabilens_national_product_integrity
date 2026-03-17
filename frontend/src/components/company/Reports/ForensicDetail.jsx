import React, { useState } from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';
import Button from '../../common/Button';

const ForensicDetail = ({ report, onClose }) => {
  const [comparisonPosition, setComparisonPosition] = useState(50);

  if (!report) return null;

  return (
    <Card className="fixed inset-0 z-50 m-4 overflow-auto">
      <div className="sticky top-0 bg-white p-4 border-b border-gray-100 flex justify-between items-center">
        <h2 className="text-xl font-bold">Forensic Analysis</h2>
        <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
          <Icon name="X" size={20} />
        </button>
      </div>

      <div className="p-6">
        {/* Split View Comparison */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          {/* Left - Uploaded Image */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-3">Uploaded Image</h3>
            <div className="bg-gray-100 rounded-xl h-64 flex items-center justify-center">
              <Icon name="Image" size={48} className="text-gray-300" />
            </div>
          </div>

          {/* Right - Master Artwork */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-3">Master Artwork</h3>
            <div className="bg-gray-100 rounded-xl h-64 flex items-center justify-center">
              <Icon name="Image" size={48} className="text-gray-300" />
            </div>
          </div>

          {/* Comparison Slider */}
          <div className="col-span-2 mt-4">
            <div className="flex items-center gap-4">
              <span className="text-xs text-gray-400">0%</span>
              <input
                type="range"
                min="0"
                max="100"
                value={comparisonPosition}
                onChange={(e) => setComparisonPosition(e.target.value)}
                className="flex-1"
              />
              <span className="text-xs text-gray-400">100%</span>
            </div>
            <p className="text-center text-sm text-gray-500 mt-2">
              Slide to compare images
            </p>
          </div>
        </div>

        {/* AI Analysis */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <Card className="bg-danger/5 border-danger/20">
            <h4 className="font-medium text-danger mb-3 flex items-center gap-2">
              <Icon name="AlertTriangle" size={16} />
              AI Anomaly Explanation
            </h4>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2 text-gray-600">
                <Icon name="X" size={14} className="text-danger" />
                Font mismatch on batch number
              </li>
              <li className="flex items-center gap-2 text-gray-600">
                <Icon name="X" size={14} className="text-danger" />
                Missing hologram on packaging
              </li>
              <li className="flex items-center gap-2 text-gray-600">
                <Icon name="X" size={14} className="text-danger" />
                Color variation in logo
              </li>
            </ul>
          </Card>

          <div>
            <Card className="mb-4">
              <h4 className="font-medium mb-3">Batch Information</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Batch Number:</span>
                  <span className="font-mono">B1-4022-XP</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Expiry:</span>
                  <span className="text-danger">Oct 2026</span>
                </div>
              </div>
            </Card>

            <Card>
              <h4 className="font-medium mb-3">Purchase Channel</h4>
              <div className="flex items-center gap-3">
                <Icon name="MapPin" size={16} className="text-gray-400" />
                <span className="text-sm">Roadside vendor, Lagos Market</span>
              </div>
              {/* Mini Map */}
              <div className="mt-3 h-24 bg-gray-100 rounded-lg flex items-center justify-center">
                <Icon name="Map" size={24} className="text-gray-300" />
              </div>
            </Card>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline">Export Report</Button>
          <Button variant="danger">Flag as Counterfeit</Button>
        </div>
      </div>
    </Card>
  );
};

export default ForensicDetail;