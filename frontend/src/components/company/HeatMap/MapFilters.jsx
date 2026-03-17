import React from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';

const MapFilters = () => {
  return (
    <Card>
      <h3 className="font-semibold mb-4">Filters</h3>
      
      <div className="space-y-4">
        {/* Product Filter */}
        <div>
          <label className="text-sm text-gray-500 mb-2 block">Product</label>
          <select className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20">
            <option>All Products</option>
            <option>Pharmaceuticals</option>
            <option>Food & Beverages</option>
            <option>Cosmetics</option>
          </select>
        </div>

        {/* Time Range Filter */}
        <div>
          <label className="text-sm text-gray-500 mb-2 block">Time Range</label>
          <div className="grid grid-cols-2 gap-2">
            {['Last 7 days', 'Last 30 days', 'Last 3 months', 'Last year'].map((range) => (
              <button
                key={range}
                className="px-3 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                {range}
              </button>
            ))}
          </div>
        </div>

        {/* Severity Filter */}
        <div>
          <label className="text-sm text-gray-500 mb-2 block">Severity</label>
          <div className="space-y-2">
            {['Critical', 'High', 'Medium', 'Low'].map((severity) => (
              <label key={severity} className="flex items-center gap-2">
                <input type="checkbox" className="rounded text-primary" />
                <span className="text-sm">{severity}</span>
              </label>
            ))}
          </div>
        </div>

        <button className="w-full bg-primary text-white py-2 rounded-lg mt-4">
          Apply Filters
        </button>
      </div>
    </Card>
  );
};

export default MapFilters;