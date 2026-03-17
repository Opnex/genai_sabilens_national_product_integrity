import React from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';

const AlertList = ({ onSelectAlert }) => {
  const alerts = [
    {
      id: 1,
      severity: 'Critical',
      product: 'Malaria Tablets',
      location: 'Lagos Mainland Market',
      reports: 24,
      recurrence: 12,
      timeRange: 'Last 7 days',
      score: 95
    },
    {
      id: 2,
      severity: 'High',
      product: 'Antibiotics',
      location: 'Kano Central',
      reports: 18,
      recurrence: 8,
      timeRange: 'Last 7 days',
      score: 87
    },
    {
      id: 3,
      severity: 'High',
      product: 'Pain Relievers',
      location: 'Abuja Shopping Complex',
      reports: 15,
      recurrence: 6,
      timeRange: 'Last 7 days',
      score: 82
    },
    {
      id: 4,
      severity: 'Critical',
      product: 'Children\'s Vaccines',
      location: 'Port Harcourt',
      reports: 21,
      recurrence: 15,
      timeRange: 'Last 7 days',
      score: 98
    },
  ];

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'Critical': return 'text-danger bg-danger/10';
      case 'High': return 'text-warning bg-warning/10';
      default: return 'text-gray-500 bg-gray-100';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-danger';
    if (score >= 80) return 'text-warning';
    return 'text-primary';
  };

  return (
    <div className="space-y-4">
      {alerts.map((alert) => (
        <Card
          key={alert.id}
          className="cursor-pointer hover:shadow-card transition-shadow"
          onClick={() => onSelectAlert(alert)}
        >
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(alert.severity)}`}>
                  {alert.severity}
                </span>
                <span className="text-xs text-gray-400">{alert.timeRange}</span>
              </div>
              <h3 className="font-semibold text-lg mb-1">{alert.product}</h3>
              <p className="text-sm text-gray-500">{alert.location}</p>
            </div>
            
            <div className="text-right">
              <div className={`text-2xl font-bold ${getScoreColor(alert.score)}`}>
                {alert.score}%
              </div>
              <p className="text-xs text-gray-400">Severity Score</p>
            </div>
          </div>

          <div className="flex gap-4 pt-3 border-t border-gray-100">
            <div className="flex items-center gap-2">
              <Icon name="Users" size={14} className="text-gray-400" />
              <span className="text-sm">{alert.reports} reports</span>
            </div>
            <div className="flex items-center gap-2">
              <Icon name="Repeat" size={14} className="text-gray-400" />
              <span className="text-sm">{alert.recurrence} recurring</span>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};

export default AlertList;