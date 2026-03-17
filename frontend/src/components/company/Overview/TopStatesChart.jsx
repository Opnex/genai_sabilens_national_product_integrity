import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import Card from '../../common/Card';

const TopStatesChart = ({ companyId }) => {
  // Generate company-specific data based on companyId
  const getCompanyData = () => {
    // Different companies have different regional distributions
    const companies = {
      'comp_1': [245, 180, 145, 120, 95],   // Pharma - Lagos heavy
      'comp_2': [120, 210, 95, 85, 65],     // Food - Kano heavy  
      'comp_3': [85, 95, 180, 75, 55],      // Beverages - Abuja heavy
    };
    
    const defaultData = [245, 180, 145, 120, 95];
    const companyData = companies[companyId] || defaultData;
    
    return [
      { state: 'Lagos', reports: companyData[0] },
      { state: 'Kano', reports: companyData[1] },
      { state: 'Abuja', reports: companyData[2] },
      { state: 'Rivers', reports: companyData[3] },
      { state: 'Ogun', reports: companyData[4] },
    ];
  };

  const data = getCompanyData();

  return (
    <Card className="h-80">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Affected States - Your Products</h3>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis type="number" stroke="#9ca3af" />
          <YAxis dataKey="state" type="category" stroke="#9ca3af" />
          <Tooltip />
          <Bar dataKey="reports" fill="#A020F0" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default TopStatesChart;