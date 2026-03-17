import React from 'react';
import Card from '../../common/Card';

const NationalMap = () => {
  return (
    <Card className="h-[500px]">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">National Risk Distribution</h2>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-danger" />
            <span className="text-xs">Critical</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-warning" />
            <span className="text-xs">High</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary" />
            <span className="text-xs">Medium</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-success" />
            <span className="text-xs">Low</span>
          </div>
        </div>
      </div>

      {/* Mock Nigeria Map with Risk Zones */}
      <div className="relative w-full h-[400px] bg-gray-50 rounded-lg overflow-hidden">
        <svg viewBox="0 0 600 400" className="w-full h-full">
          {/* State boundaries */}
          <path
            d="M300,50 L450,150 L500,250 L450,350 L300,380 L150,350 L100,250 L150,150 L300,50"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="1"
          />
          
          {/* Risk zones with varying opacity */}
          <circle cx="180" cy="280" r="60" fill="#EF4444" fillOpacity="0.3" stroke="#EF4444" />
          <circle cx="420" cy="150" r="50" fill="#F59E0B" fillOpacity="0.3" stroke="#F59E0B" />
          <circle cx="300" cy="200" r="40" fill="#A020F0" fillOpacity="0.3" stroke="#A020F0" />
          <circle cx="250" cy="320" r="30" fill="#10B981" fillOpacity="0.3" stroke="#10B981" />
          
          {/* City markers */}
          <circle cx="180" cy="280" r="8" fill="#EF4444" />
          <text x="150" y="260" className="text-xs fill-gray-700">Lagos</text>
          
          <circle cx="420" cy="150" r="6" fill="#F59E0B" />
          <text x="400" y="130" className="text-xs fill-gray-700">Kano</text>
          
          <circle cx="300" cy="200" r="5" fill="#A020F0" />
          <text x="280" cy="180" className="text-xs fill-gray-700">Abuja</text>
          
          <circle cx="250" cy="320" r="4" fill="#10B981" />
          <text x="220" y="300" className="text-xs fill-gray-700">P.Harcourt</text>
        </svg>
      </div>
    </Card>
  );
};

export default NationalMap;