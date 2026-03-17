import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import Card from '../../common/Card';

const TrendChart = ({ companyId }) => {
  // Generate company-specific data based on companyId
  const getCompanyData = () => {
    // In a real app, this would come from an API
    // For demo, generate different data for different companies
    const companies = {
      'comp_1': [65, 85, 95, 70, 110, 130], // Pharma
      'comp_2': [45, 55, 75, 60, 85, 95],   // Food
      'comp_3': [25, 35, 45, 40, 55, 65],   // Beverages
    };
    
    const defaultData = [65, 85, 95, 70, 110, 130];
    const companyData = companies[companyId] || defaultData;
    
    return [
      { month: 'Jan', reports: companyData[0], verified: Math.round(companyData[0] * 0.7) },
      { month: 'Feb', reports: companyData[1], verified: Math.round(companyData[1] * 0.7) },
      { month: 'Mar', reports: companyData[2], verified: Math.round(companyData[2] * 0.7) },
      { month: 'Apr', reports: companyData[3], verified: Math.round(companyData[3] * 0.7) },
      { month: 'May', reports: companyData[4], verified: Math.round(companyData[4] * 0.75) },
      { month: 'Jun', reports: companyData[5], verified: Math.round(companyData[5] * 0.8) },
    ];
  };

  const data = getCompanyData();

  return (
    <Card className="h-80">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Counterfeit Trend - Your Products</h3>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="month" stroke="#9ca3af" />
          <YAxis stroke="#9ca3af" />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="reports"
            stroke="#A020F0"
            strokeWidth={2}
            dot={{ fill: '#A020F0' }}
            name="Total Reports"
          />
          <Line
            type="monotone"
            dataKey="verified"
            stroke="#10B981"
            strokeWidth={2}
            dot={{ fill: '#10B981' }}
            name="Verified Authentic"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default TrendChart;