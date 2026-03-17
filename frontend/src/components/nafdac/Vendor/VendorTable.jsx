import React from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';

const VendorTable = () => {
  const vendors = [
    {
      location: 'Lagos Mainland Market',
      reportCount: 47,
      products: ['Malaria Tablets', 'Antibiotics'],
      riskLevel: 'Critical',
      lastReported: 'Today'
    },
    {
      location: 'Kano Central Market',
      reportCount: 32,
      products: ['Pain Relievers', 'Vitamins'],
      riskLevel: 'High',
      lastReported: 'Yesterday'
    },
    {
      location: 'Abuja Shopping Complex',
      reportCount: 28,
      products: ['Antibiotics', 'Vaccines'],
      riskLevel: 'High',
      lastReported: '2 days ago'
    },
    {
      location: 'Port Harcourt Market',
      reportCount: 21,
      products: ['Malaria Tablets'],
      riskLevel: 'Medium',
      lastReported: '3 days ago'
    },
    {
      location: 'Ibadan Central',
      reportCount: 15,
      products: ['Pain Relievers'],
      riskLevel: 'Medium',
      lastReported: '5 days ago'
    },
  ];

  const getRiskColor = (risk) => {
    switch(risk) {
      case 'Critical': return 'text-danger bg-danger/10';
      case 'High': return 'text-warning bg-warning/10';
      case 'Medium': return 'text-primary bg-primary/10';
      default: return 'text-gray-500 bg-gray-100';
    }
  };

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Location</th>
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Report Count</th>
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Products Involved</th>
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Risk Level</th>
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Last Reported</th>
            </tr>
          </thead>
          <tbody>
            {vendors.map((vendor, index) => (
              <tr key={index} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="py-4 px-4 font-medium">{vendor.location}</td>
                <td className="py-4 px-4">
                  <span className="font-semibold text-lg">{vendor.reportCount}</span>
                  <span className="text-xs text-gray-400 ml-1">reports</span>
                </td>
                <td className="py-4 px-4">
                  <div className="flex gap-1">
                    {vendor.products.map((product, i) => (
                      <span key={i} className="text-xs bg-gray-100 px-2 py-1 rounded-full">
                        {product}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="py-4 px-4">
                  <span className={`text-xs px-2 py-1 rounded-full ${getRiskColor(vendor.riskLevel)}`}>
                    {vendor.riskLevel}
                  </span>
                </td>
                <td className="py-4 px-4 text-gray-500">{vendor.lastReported}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

export default VendorTable;