import React from 'react';
import ConsumerBottomNav from '../../components/layout/ConsumerBottomNav';
import ReportConfirmation from '../../components/consumer/Scan/ReportConfirmation';

const Report = () => {
  return (
    <div className="min-h-screen bg-background pb-20">
      <ReportConfirmation />
      <ConsumerBottomNav />
    </div>
  );
};

export default Report;