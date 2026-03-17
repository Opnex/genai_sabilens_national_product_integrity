import React from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';

const ProductList = () => {
  const products = [
    {
      id: 1,
      name: 'Malaria Tablets',
      nafdac: 'B1-4022-XP',
      category: 'Pharmaceuticals',
      status: 'active',
      lastUpdated: '2024-01-15'
    },
    {
      id: 2,
      name: 'Antibiotics',
      nafdac: 'B1-4023-XP',
      category: 'Pharmaceuticals',
      status: 'active',
      lastUpdated: '2024-01-14'
    },
    {
      id: 3,
      name: 'Pain Reliever',
      nafdac: 'B1-4024-XP',
      category: 'Pharmaceuticals',
      status: 'pending',
      lastUpdated: '2024-01-13'
    },
  ];

  return (
    <Card>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Product Registry</h3>
        <button className="text-primary text-sm font-medium">View All</button>
      </div>

      <div className="space-y-3">
        {products.map((product) => (
          <div
            key={product.id}
            className="flex items-center justify-between p-3 border border-gray-100 rounded-lg hover:bg-gray-50 cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <Icon name="Package" size={20} className="text-primary" />
              </div>
              <div>
                <h4 className="font-medium">{product.name}</h4>
                <p className="text-xs text-gray-400">{product.nafdac}</p>
              </div>
            </div>
            <div className="text-right">
              <span className={`text-xs px-2 py-1 rounded-full ${
                product.status === 'active' ? 'bg-success/10 text-success' : 'bg-warning/10 text-warning'
              }`}>
                {product.status}
              </span>
              <p className="text-xs text-gray-400 mt-1">Updated {product.lastUpdated}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default ProductList;