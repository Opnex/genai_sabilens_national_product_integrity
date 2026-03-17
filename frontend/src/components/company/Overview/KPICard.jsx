import React from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';

const KPICard = ({ title, value, change, icon, color = 'primary' }) => {
  const colorClasses = {
    primary: 'text-primary bg-primary/10',
    success: 'text-success bg-success/10',
    warning: 'text-warning bg-warning/10',
    danger: 'text-danger bg-danger/10'
  };

  return (
    <Card className="hover:shadow-card transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-400 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change && (
            <p className={`text-xs mt-2 ${change > 0 ? 'text-success' : 'text-danger'}`}>
              {change > 0 ? '↑' : '↓'} {Math.abs(change)}% from last month
            </p>
          )}
        </div>
        <div className={`w-12 h-12 rounded-xl ${colorClasses[color]} flex items-center justify-center`}>
          <Icon name={icon} size={24} className={colorClasses[color].split(' ')[0]} />
        </div>
      </div>
    </Card>
  );
};

export default KPICard;