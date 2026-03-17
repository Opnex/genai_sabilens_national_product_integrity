import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';

const HelpSupport = () => {
  const navigate = useNavigate();
  const [showContactModal, setShowContactModal] = useState(false);
  const [activeFaq, setActiveFaq] = useState(null);

  const faqs = [
    {
      question: 'How does SabiLens verify products?',
      answer: 'SabiLens uses advanced AI to analyze product packaging, NAFDAC numbers, barcodes, and other visual features. We compare your scan against our database of authentic products to detect counterfeits.'
    },
    {
      question: 'What should I do if I find a counterfeit?',
      answer: 'If you find a counterfeit, use the "Report to NAFDAC" feature in the scan result. This sends an automated report with GPS location and product details to help authorities take action.'
    },
    {
      question: 'Is my location data shared?',
      answer: 'Location data is only used to map counterfeit hotspots and is anonymized when shared with authorities and manufacturers. You can disable location access in your device settings.'
    },
    {
      question: 'How accurate is the AI detection?',
      answer: 'Our AI achieves over 95% accuracy in controlled tests. However, results should be used as a guide. Always exercise caution and report suspicious products.'
    },
    {
      question: 'Can I use SabiLens offline?',
      answer: 'An internet connection is required for verification as we need to check against our database. However, you can view your scan history offline.'
    },
    {
      question: 'How do I delete my account?',
      answer: 'Go to Profile → Settings → Delete Account. Please note this action is permanent and will erase all your scan history.'
    }
  ];

  const supportTopics = [
    {
      icon: 'Camera',
      title: 'Scanning Issues',
      description: 'Camera not working, blurry scans, product not recognized'
    },
    {
      icon: 'Shield',
      title: 'Account & Security',
      description: 'Login problems, password reset, account settings'
    },
    {
      icon: 'Bell',
      title: 'Notifications',
      description: 'Alert settings, language preferences, voice reports'
    },
    {
      icon: 'MapPin',
      title: 'Location & Reports',
      description: 'GPS issues, reporting problems, evidence upload'
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-white px-6 pt-12 pb-4 sticky top-0 z-10 shadow-soft">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate('/profile')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Icon name="ArrowLeft" size={20} className="text-gray-600" library="fi" />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Help & Support</h1>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Contact Card */}
        <Card className="bg-primary/5 border border-primary/20">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
              <Icon name="Headphones" size={24} className="text-primary" library="fi" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">Need immediate help?</h3>
              <p className="text-sm text-gray-500 mb-3">Our support team is available 24/7</p>
              <Button
                variant="primary"
                size="sm"
                onClick={() => setShowContactModal(true)}
              >
                Contact Support
              </Button>
            </div>
          </div>
        </Card>

        {/* Quick Support Topics */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Help Topics</h2>
          <div className="grid grid-cols-2 gap-3">
            {supportTopics.map((topic, index) => (
              <Card key={index} className="p-4 cursor-pointer hover:shadow-card transition-all hover:scale-[1.02]">
                <div className="text-center">
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Icon name={topic.icon} size={20} className="text-primary" library="fi" />
                  </div>
                  <h3 className="font-medium text-sm text-gray-900 mb-1">{topic.title}</h3>
                  <p className="text-xs text-gray-400">{topic.description}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* FAQs */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Frequently Asked Questions</h2>
          <div className="space-y-3">
            {faqs.map((faq, index) => (
              <Card key={index} className="overflow-hidden">
                <button
                  onClick={() => setActiveFaq(activeFaq === index ? null : index)}
                  className="w-full p-4 text-left flex justify-between items-center"
                >
                  <span className="font-medium text-gray-900">{faq.question}</span>
                  <Icon 
                    name={activeFaq === index ? 'ChevronUp' : 'ChevronDown'} 
                    size={18} 
                    className="text-primary" 
                    library="fi" 
                  />
                </button>
                {activeFaq === index && (
                  <div className="px-4 pb-4 text-sm text-gray-500 border-t border-gray-100 pt-3">
                    {faq.answer}
                  </div>
                )}
              </Card>
            ))}
          </div>
        </div>

        {/* Contact Methods */}
        <Card>
          <h3 className="font-semibold text-gray-900 mb-4">Other Ways to Reach Us</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Icon name="Mail" size={18} className="text-primary" library="fi" />
              <div>
                <p className="text-sm font-medium">Email</p>
                <p className="text-xs text-gray-400">support@sabilens.com</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Icon name="Phone" size={18} className="text-primary" library="fi" />
              <div>
                <p className="text-sm font-medium">Phone</p>
                <p className="text-xs text-gray-400">+234 800 123 4567</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Icon name="MessageCircle" size={18} className="text-primary" library="fi" />
              <div>
                <p className="text-sm font-medium">Live Chat</p>
                <p className="text-xs text-gray-400">Available 24/7</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Contact Modal */}
      <Modal
        isOpen={showContactModal}
        onClose={() => setShowContactModal(false)}
        type="info"
        title="Contact Support"
        message={
          <div className="space-y-4">
            <p className="text-gray-600">How would you like to contact us?</p>
            <div className="space-y-3">
              <button className="w-full p-3 border border-gray-200 rounded-lg flex items-center gap-3 hover:bg-gray-50">
                <Icon name="MessageCircle" size={20} className="text-primary" library="fi" />
                <span className="text-sm font-medium">Start Live Chat</span>
              </button>
              <button className="w-full p-3 border border-gray-200 rounded-lg flex items-center gap-3 hover:bg-gray-50">
                <Icon name="Mail" size={20} className="text-primary" library="fi" />
                <span className="text-sm font-medium">Send Email</span>
              </button>
              <button className="w-full p-3 border border-gray-200 rounded-lg flex items-center gap-3 hover:bg-gray-50">
                <Icon name="Phone" size={20} className="text-primary" library="fi" />
                <span className="text-sm font-medium">Request Call Back</span>
              </button>
            </div>
            <p className="text-xs text-gray-400 text-center mt-4">
              Average response time: 2-4 hours
            </p>
          </div>
        }
      />
    </div>
  );
};

export default HelpSupport;