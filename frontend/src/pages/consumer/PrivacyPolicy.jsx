import React from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';

const PrivacyPolicy = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      <div className="bg-white px-6 pt-12 pb-4 sticky top-0 z-10 shadow-soft">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate('/profile')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Icon name="ArrowLeft" size={20} className="text-gray-600" library="fi" />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Privacy Policy</h1>
        </div>
      </div>

      <div className="p-6 space-y-6">
        <Card>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-500 text-sm mb-4">Last Updated: February 2026</p>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-3">1. Information We Collect</h3>
            <p className="text-gray-600 text-sm mb-4">
              SabiLens collects information to provide better services to all our users. We collect:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600 mb-4">
              <li>Account information (name, phone number, email)</li>
              <li>Location data when you scan products</li>
              <li>Scan history and product verification data</li>
              <li>Device information and camera access for scanning</li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-900 mb-3">2. How We Use Information</h3>
            <p className="text-gray-600 text-sm mb-4">
              We use the information we collect to:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600 mb-4">
              <li>Verify product authenticity</li>
              <li>Generate counterfeit reports for NAFDAC</li>
              <li>Improve our AI detection algorithms</li>
              <li>Send important safety alerts</li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-900 mb-3">3. Data Sharing</h3>
            <p className="text-gray-600 text-sm mb-4">
              We do not sell your personal information. We may share anonymized scan data with:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600 mb-4">
              <li>NAFDAC for regulatory enforcement</li>
              <li>Manufacturers to protect their brands</li>
              <li>Research partners to combat counterfeiting</li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-900 mb-3">4. Your Rights</h3>
            <p className="text-gray-600 text-sm mb-4">
              You have the right to:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600">
              <li>Access your personal data</li>
              <li>Delete your account and data</li>
              <li>Opt out of non-essential data collection</li>
              <li>Request data portability</li>
            </ul>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default PrivacyPolicy;