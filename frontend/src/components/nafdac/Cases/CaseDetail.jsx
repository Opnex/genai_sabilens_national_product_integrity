import React, { useState } from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';
import Button from '../../common/Button';

const CaseDetail = ({ caseId }) => {
  const [activeTab, setActiveTab] = useState('reports');

  const tabs = [
    { id: 'reports', label: 'Reports', icon: 'FileText' },
    { id: 'images', label: 'Forensic Images', icon: 'Image' },
    { id: 'vendors', label: 'Vendor Recurrence', icon: 'Users' },
  ];

  return (
    <div>
      {/* Case Header */}
      <Card className="mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-bold mb-2">Case #{caseId}</h2>
            <div className="flex gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <Icon name="Calendar" size={14} />
                Opened Jan 15, 2024
              </span>
              <span className="flex items-center gap-1">
                <Icon name="AlertTriangle" size={14} className="text-danger" />
                Critical
              </span>
            </div>
          </div>
          
          <Button variant="primary" icon="Download">
            Export Case Bundle
          </Button>
        </div>
      </Card>

      {/* Tabs */}
      <Card className="mb-6">
        <div className="flex gap-2 border-b border-gray-100">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon name={tab.icon} size={16} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="p-4">
          {activeTab === 'reports' && (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between mb-2">
                    <span className="font-medium">Report #{i}</span>
                    <span className="text-sm text-gray-400">2 hours ago</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    Counterfeit product detected at Lagos Market...
                  </p>
                  <div className="flex gap-4 text-xs text-gray-400">
                    <span>Similarity: 87%</span>
                    <span>Batch: B1-4022-XP</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'images' && (
            <div className="grid grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center">
                  <Icon name="Image" size={32} className="text-gray-300" />
                </div>
              ))}
            </div>
          )}

          {activeTab === 'vendors' && (
            <div>
              <table className="w-full">
                <thead>
                  <tr className="text-left text-sm text-gray-400">
                    <th className="pb-3">Vendor</th>
                    <th className="pb-3">Reports</th>
                    <th className="pb-3">Risk Level</th>
                    <th className="pb-3">Last Reported</th>
                  </tr>
                </thead>
                <tbody>
                  {[1, 2, 3].map((i) => (
                    <tr key={i} className="border-t border-gray-100">
                      <td className="py-3">Market Stall #{i}</td>
                      <td className="py-3">12 reports</td>
                      <td className="py-3">
                        <span className="text-danger bg-danger/10 px-2 py-1 rounded-full text-xs">
                          High
                        </span>
                      </td>
                      <td className="py-3 text-gray-400">Today</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>

      {/* Download Options */}
      <Card>
        <h3 className="font-semibold mb-4">Export Options</h3>
        <div className="grid grid-cols-2 gap-4">
          <Button variant="outline" icon="FileText" fullWidth>
            Export as PDF
          </Button>
          <Button variant="outline" icon="Download" fullWidth>
            Download Images
          </Button>
          <Button variant="outline" icon="Table" fullWidth>
            Export CSV
          </Button>
          <Button variant="primary" icon="Archive" fullWidth>
            Download All (ZIP)
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default CaseDetail;