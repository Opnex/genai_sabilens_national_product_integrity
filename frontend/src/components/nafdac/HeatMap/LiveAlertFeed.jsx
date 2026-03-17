import React from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';

const LiveAlertFeed = () => {
  const alerts = [
    {
      id: 1,
      type: 'Critical',
      location: 'Lagos Market',
      product: 'Malaria Tablets',
      time: '2 min ago',
      reports: 12
    },
    {
      id: 2,
      type: 'High',
      location: 'Kano Central',
      product: 'Antibiotics',
      time: '15 min ago',
      reports: 8
    },
    {
      id: 3,
      type: 'Medium',
      location: 'Abuja Mall',
      product: 'Pain Reliever',
      time: '32 min ago',
      reports: 5
    },
    {
      id: 4,
      type: 'Critical',
      location: 'Port Harcourt',
      product: 'Vaccines',
      time: '45 min ago',
      reports: 15
    },
  ];

  const getTypeColor = (type) => {
    switch(type) {
      case 'Critical': return 'text-danger bg-danger/10';
      case 'High': return 'text-warning bg-warning/10';
      case 'Medium': return 'text-primary bg-primary/10';
      default: return 'text-gray-500 bg-gray-100';
    }
  };

  return (
    <Card>
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold">Live Alert Feed</h3>
        <span className="text-xs bg-danger/10 text-danger px-2 py-1 rounded-full">
          {alerts.length} active
        </span>
      </div>

      <div className="space-y-4">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className="flex items-start gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 cursor-pointer transition-colors"
          >
            <div className={`w-2 h-2 mt-2 rounded-full ${
              alert.type === 'Critical' ? 'bg-danger' :
              alert.type === 'High' ? 'bg-warning' : 'bg-primary'
            }`} />
            
            <div className="flex-1">
              <div className="flex justify-between items-start mb-1">
                <span className={`text-xs px-2 py-0.5 rounded-full ${getTypeColor(alert.type)}`}>
                  {alert.type}
                </span>
                <span className="text-xs text-gray-400">{alert.time}</span>
              </div>
              
              <p className="font-medium text-sm">{alert.product}</p>
              <p className="text-xs text-gray-500 mb-2">{alert.location}</p>
              
              <div className="flex items-center gap-2 text-xs">
                <Icon name="Users" size={12} className="text-gray-400" />
                <span className="text-gray-500">{alert.reports} reports</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <button className="w-full text-center text-primary text-sm font-medium mt-4">
        View All Alerts
      </button>
    </Card>
  );
};

export default LiveAlertFeed;