import React from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';

const TermsOfService = () => {
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
          <h1 className="text-2xl font-bold text-gray-900">Terms of Service</h1>
        </div>
      </div>

      <div className="p-6 space-y-6">
        <Card>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-500 text-sm mb-4">Last Updated: February 2026</p>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-3">1. Acceptance of Terms</h3>
            <p className="text-gray-600 text-sm mb-4">
              By accessing or using SabiLens, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our service.
            </p>

            <h3 className="text-lg font-semibold text-gray-900 mb-3">2. Description of Service</h3>
            <p className="text-gray-600 text-sm mb-4">
              SabiLens provides AI-powered product verification services to help consumers identify counterfeit products. The service includes:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600 mb-4">
              <li>Product scanning and authentication</li>
              <li>Counterfeit reporting to authorities</li>
              <li>Scan history and analytics</li>
              <li>Safety alerts in multiple languages</li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-900 mb-3">3. User Responsibilities</h3>
            <p className="text-gray-600 text-sm mb-4">As a user, you agree to:</p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600 mb-4">
              <li>Provide accurate information when reporting counterfeits</li>
              <li>Use the service only for lawful purposes</li>
              <li>Not attempt to manipulate or falsify scan results</li>
              <li>Keep your account credentials secure</li>
            </ul>

            <h3 className="text-lg font-semibold text-gray-900 mb-3">4. Intellectual Property</h3>
            <p className="text-gray-600 text-sm mb-4">
              All content, features, and functionality of SabiLens are owned by SabiLens and protected by international copyright, trademark, and other intellectual property laws.
            </p>

            <h3 className="text-lg font-semibold text-gray-900 mb-3">5. Limitation of Liability</h3>
            <p className="text-gray-600 text-sm mb-4">
              SabiLens provides verification results based on AI analysis. While we strive for accuracy, we cannot guarantee 100% detection rate. Users should exercise their own judgment when purchasing products.
            </p>

            <h3 className="text-lg font-semibold text-gray-900 mb-3">6. Termination</h3>
            <p className="text-gray-600 text-sm mb-4">
              We reserve the right to terminate or suspend access to our service immediately, without prior notice, for any reason, including breach of these Terms.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default TermsOfService;