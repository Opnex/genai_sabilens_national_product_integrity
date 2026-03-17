import React from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';

const ReportsTable = ({ onRowClick }) => {
  const reports = [
    {
      id: 1,
      product: 'Malaria Tablets',
      location: 'Lagos Market',
      severity: 'High',
      score: 87,
      date: '2024-01-15',
      status: 'pending'
    },
    {
      id: 2,
      product: 'Antibiotics',
      location: 'Kano Central',
      severity: 'Critical',
      score: 95,
      date: '2024-01-14',
      status: 'verified'
    },
    {
      id: 3,
      product: 'Pain Reliever',
      location: 'Abuja Mall',
      severity: 'Medium',
      score: 62,
      date: '2024-01-13',
      status: 'investigating'
    },
  ];

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'Critical': return 'text-danger bg-danger/10';
      case 'High': return 'text-warning bg-warning/10';
      case 'Medium': return 'text-primary bg-primary/10';
      default: return 'text-gray-500 bg-gray-100';
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'verified': return 'text-success bg-success/10';
      case 'pending': return 'text-warning bg-warning/10';
      case 'investigating': return 'text-primary bg-primary/10';
      default: return 'text-gray-500 bg-gray-100';
    }
  };

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Product</th>
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Location</th>
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Severity</th>
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Score</th>
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Date</th>
              <th className="text-left py-4 px-4 text-sm font-medium text-gray-400">Status</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((report) => (
              <tr
                key={report.id}
                onClick={() => onRowClick(report)}
                className="border-b border-gray-50 hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <td className="py-4 px-4 font-medium">{report.product}</td>
                <td className="py-4 px-4 text-gray-600">{report.location}</td>
                <td className="py-4 px-4">
                  <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(report.severity)}`}>
                    {report.severity}
                  </span>
                </td>
                <td className="py-4 px-4">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{report.score}%</span>
                    <div className="w-16 h-1.5 bg-gray-200 rounded-full">
                      <div 
                        className={`h-1.5 rounded-full ${
                          report.score > 80 ? 'bg-danger' : 
                          report.score > 60 ? 'bg-warning' : 'bg-success'
                        }`}
                        style={{ width: `${report.score}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td className="py-4 px-4 text-gray-600">{report.date}</td>
                <td className="py-4 px-4">
                  <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(report.status)}`}>
                    {report.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

export default ReportsTable;