import React from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';

const RecentScanCard = ({ product, status, time, verified, productImage }) => {
  const statusColors = {
    authentic: 'text-success',
    caution: 'text-warning',
    fake: 'text-danger'
  };

  const statusBgColors = {
    authentic: 'bg-success/10',
    caution: 'bg-warning/10',
    fake: 'bg-danger/10'
  };

  const getStatusIcon = () => {
    switch(status) {
      case 'authentic':
        return <Icon name="CheckCircle" size={14} className="text-success" library="fi" />;
      case 'caution':
        return <Icon name="AlertTriangle" size={14} className="text-warning" library="fi" />;
      case 'fake':
        return <Icon name="XCircle" size={14} className="text-danger" library="fi" />;
      default:
        return null;
    }
  };

  return (
    <Card className="flex items-center gap-3 mb-3 hover:shadow-card transition-shadow p-2">
      {/* Product Image */}
      <div className="w-16 h-16 rounded-xl overflow-hidden bg-gray-100 flex-shrink-0">
        {productImage ? (
          <img 
            src={productImage} 
            alt={product}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Icon name="Package" size={24} className="text-gray-300" library="fi" />
          </div>
        )}
      </div>

      {/* Product Details */}
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-gray-900 truncate">{product}</h3>
        <div className="flex items-center gap-2 mt-1">
          <span className={`text-xs px-2 py-0.5 rounded-full ${statusBgColors[status]} ${statusColors[status]} flex items-center gap-1`}>
            {getStatusIcon()}
            {status === 'authentic' ? 'Authentic' : status === 'caution' ? 'Caution' : 'Fake'}
          </span>
          {verified && (
            <span className="text-xs text-success flex items-center gap-1">
              <Icon name="Check" size={12} className="text-success" library="fi" />
              Verified
            </span>
          )}
        </div>
      </div>

      {/* Time */}
      <div className="text-right flex-shrink-0">
        <p className="text-xs text-gray-400">{time}</p>
      </div>
    </Card>
  );
};

export default RecentScanCard;