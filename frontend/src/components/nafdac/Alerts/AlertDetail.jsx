import React from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';
import Button from '../../common/Button';

const AlertDetail = ({ alert, onClose }) => {
  if (!alert) return null;

  return (
    <Card className="fixed inset-0 z-50 m-8 overflow-auto">
      <div className="sticky top-0 bg-white p-6 border-b border-gray-100 flex justify-between items-center">
        <h2 className="text-xl font-bold">Case Intelligence</h2>
        <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
          <Icon name="X" size={20} />
        </button>
      </div>

      <div className="p-6">
        {/* Header Info */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <div>
            <p className="text-sm text-gray-400 mb-1">Product</p>
            <p className="text-xl font-semibold">{alert.product}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Location</p>
            <p className="text-xl font-semibold">{alert.location}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Severity Score</p>
            <p className={`text-2xl font-bold ${
              alert.score >= 90 ? 'text-danger' : 'text-warning'
            }`}>
              {alert.score}%
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Time Range</p>
            <p className="text-xl font-semibold">{alert.timeRange}</p>
          </div>
        </div>

        {/* Clustered Reports */}
        <Card className="mb-8">
          <h3 className="font-semibold mb-4">Clustered Reports</h3>
          <div className="grid grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-3 bg-gray-50 rounded-lg">
                <p className="font-medium">Market {i}</p>
                <p className="text-sm text-gray-500">12 reports</p>
                <div className="flex items-center gap-1 mt-2">
                  <Icon name="MapPin" size={12} className="text-gray-400" />
                  <span className="text-xs text-gray-400">GPS locked</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* GPS Breakdown */}
        <Card className="mb-8">
          <h3 className="font-semibold mb-4">GPS Location Breakdown</h3>
          <div className="h-48 bg-gray-100 rounded-lg flex items-center justify-center">
            <Icon name="Map" size={48} className="text-gray-300" />
          </div>
          <div className="grid grid-cols-4 gap-4 mt-4">
            {['Lagos', 'Kano', 'Abuja', 'PH'].map((city) => (
              <div key={city} className="text-center">
                <p className="font-medium">{city}</p>
                <p className="text-sm text-danger">12 cases</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Product Overlap & Timeline */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <Card>
            <h3 className="font-semibold mb-4">Product Overlap</h3>
            <div className="space-y-3">
              {['Malaria Tablets', 'Antibiotics', 'Pain Relievers'].map((product) => (
                <div key={product} className="flex items-center justify-between">
                  <span className="text-sm">{product}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-gray-200 rounded-full">
                      <div className="w-3/4 h-2 bg-danger rounded-full" />
                    </div>
                    <span className="text-xs text-gray-500">75%</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h3 className="font-semibold mb-4">Timeline Chart</h3>
            <div className="h-32 flex items-end gap-2">
              {[65, 85, 70, 95, 80, 75, 90].map((height, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <div 
                    className="w-full bg-primary/20 rounded-t-lg"
                    style={{ height: `${height}%` }}
                  >
                    <div 
                      className="w-full bg-primary rounded-t-lg"
                      style={{ height: `${height * 0.7}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-400">D{i+1}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline">Export Case Bundle</Button>
          <Button variant="primary" icon="Download">
            Download ZIP
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default AlertDetail;