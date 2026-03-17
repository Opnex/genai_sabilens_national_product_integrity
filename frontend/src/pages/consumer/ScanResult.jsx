import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import ConsumerBottomNav from '../../components/layout/ConsumerBottomNav';
import ScanResultSafe from '../../components/consumer/Scan/ScanResultSafe';
import ScanResultFake from '../../components/consumer/Scan/ScanResultFake';

const ScanResult = () => {
  const navigate = useNavigate();
  const { result } = useParams();
  const isSafe = result === 'safe';

  const handleBack = () => {
    navigate('/home');
  };

  const handleReportIssue = () => {
    navigate('/report');
  };

  const handleScanAnother = () => {
    navigate('/home');
  };

  const handleReportToAuthority = () => {
    navigate('/report');
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      {isSafe ? (
        <ScanResultSafe
          onBack={handleBack}
          onReportIssue={handleReportIssue}
          onScanAnother={handleScanAnother}
        />
      ) : (
        <ScanResultFake
          onBack={handleBack}
          onReportToAuthority={handleReportToAuthority}
        />
      )}
      <ConsumerBottomNav />
    </div>
  );
};

export default ScanResult;