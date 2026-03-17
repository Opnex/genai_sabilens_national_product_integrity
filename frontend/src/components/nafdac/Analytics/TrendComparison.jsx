import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Card from '../../common/Card';

const data = [
  { quarter: 'Q1 2023', drugs: 120, dairy: 80, beverages: 60 },
  { quarter: 'Q2 2023', drugs: 150, dairy: 95, beverages: 75 },
  { quarter: 'Q3 2023', drugs: 180, dairy: 110, beverages: 85 },
  { quarter: 'Q4 2023', drugs: 210, dairy: 130, beverages: 100 },
  { quarter: 'Q1 2024', drugs: 195, dairy: 125, beverages: 95 },
];

const TrendComparison = () => {
  return (
    <Card className="h-96">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quarterly Trend Comparison</h3>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="quarter" stroke="#9ca3af" />
          <YAxis stroke="#9ca3af" />
          <Tooltip />
          <Legend />
          <Bar dataKey="drugs" fill="#EF4444" name="Fake Drugs" />
          <Bar dataKey="dairy" fill="#F59E0B" name="Fake Dairy" />
          <Bar dataKey="beverages" fill="#A020F0" name="Fake Beverages" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default TrendComparison;