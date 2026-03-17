import React from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';
import Button from '../../common/Button';

const EvidenceList = () => {
  const evidenceItems = [
    {
      id: 1,
      caseId: 'CASE-2024-001',
      product: 'Malaria Tablets',
      images: 4,
      reports: 2,
      date: '2024-01-15',
      size: '24 MB'
    },
    {
      id: 2,
      caseId: 'CASE-2024-002',
      product: 'Antibiotics',
      images: 6,
      reports: 3,
      date: '2024-01-14',
      size: '36 MB'
    },
    {
      id: 3,
      caseId: 'CASE-2024-003',
      product: 'Pain Reliever',
      images: 2,
      reports: 1,
      date: '2024-01-13',
      size: '12 MB'
    },
  ];

  return (
    <div className="space-y-4">
      {evidenceItems.map((item) => (
        <Card key={item.id} className="hover:shadow-card transition-shadow">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h3 className="font-semibold">{item.caseId}</h3>
                <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                  {item.product}
                </span>
              </div>
              
              <div className="flex gap-4 text-sm text-gray-500 mb-4">
                <span className="flex items-center gap-1">
                  <Icon name="Image" size={14} />
                  {item.images} images
                </span>
                <span className="flex items-center gap-1">
                  <Icon name="File" size={14} />
                  {item.reports} reports
                </span>
                <span className="flex items-center gap-1">
                  <Icon name="Calendar" size={14} />
                  {item.date}
                </span>
              </div>
            </div>
            
            <div className="text-right">
              <p className="text-sm text-gray-400 mb-2">{item.size}</p>
              <Button variant="outline" size="sm" icon="Download">
                Download
              </Button>
            </div>
          </div>

          {/* Image Previews */}
          <div className="grid grid-cols-4 gap-2 mt-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center">
                <Icon name="Image" size={20} className="text-gray-300" />
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
};

export default EvidenceList;