import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import Card from '../../common/Card';

const data = [
  { name: 'Fake Drugs', value: 45, color: '#EF4444' },
  { name: 'Fake Dairy', value: 25, color: '#F59E0B' },
  { name: 'Fake Beverages', value: 20, color: '#A020F0' },
  { name: 'Fake Cosmetics', value: 10, color: '#10B981' },
];

const CategoryChart = () => {
  return (
    <Card className="h-96">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Counterfeit Categories</h3>
      <ResponsiveContainer width="100%" height="85%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default CategoryChart;