import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../common/Icon';
import Card from '../../common/Card';
import RecentScanCard from './RecentScanCard';
import Modal from '../../common/Modal';
import AppHeader from '../../layout/AppHeader';

const HomeScreen = ({
  firstName = 'Guest',
  userInitials = 'U',
  profileImage = null,
  recentScans = [],
  onScanPress,
  onViewAllPress,
  onScanItemPress,
  onProfilePress,
  isFirstTimeUser = false
}) => {
  const navigate = useNavigate();
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [showNotificationModal, setShowNotificationModal] = useState(isFirstTimeUser);
  const [isScrolled, setIsScrolled] = useState(false);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      setIsScrolled(scrollPosition > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Get current time greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const languages = [
    { code: 'en', name: 'English', status: 'active' },
    { code: 'yo', name: 'Yorùbá', status: 'coming soon' },
    { code: 'ha', name: 'Hausa', status: 'coming soon' },
    { code: 'ig', name: 'Igbo', status: 'coming soon' },
    { code: 'pcm', name: 'Pidgin', status: 'coming soon' }
  ];

  return (
    <>
      <AppHeader
        title={`${getGreeting()}, ${firstName}`}
      />

      {/* Main Content - Updated to use same padding as header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Scan Button */}
        <Card
          className="mb-8 text-center py-8 cursor-pointer hover:shadow-card transition-shadow group"
          onClick={onScanPress}
        >
          <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-primary/20 transition-colors">
            <Icon name="Camera" size={32} className="text-primary" library="fi" />
          </div>
          <h2 className="text-lg font-semibold text-gray-900">Scan Product</h2>
          <p className="text-sm text-gray-400 mt-1">
            Position the product tag within the camera frame
          </p>
        </Card>

        {/* Recent Scan History */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Scan History</h2>
          <button
            className="text-primary text-sm font-medium hover:underline"
            onClick={onViewAllPress}
          >
            View All
          </button>
        </div>

        <div>
          {recentScans.length > 0 ? (
            recentScans.map((scan, index) => (
              <div key={index} onClick={() => onScanItemPress(scan)}>
                <RecentScanCard {...scan} />
              </div>
            ))
          ) : (
            <Card className="text-center py-8">
              <Icon name="Clock" size={32} className="text-gray-300 mx-auto mb-3" library="fi" />
              <p className="text-gray-400">No scans yet</p>
              <p className="text-sm text-gray-300 mt-1">Scan a product to get started</p>
            </Card>
          )}
        </div>
      </div>

      {/* Language Modal */}
      <Modal
        isOpen={showLanguageModal}
        onClose={() => setShowLanguageModal(false)}
        type="info"
        title="Select Language"
        message={
          <div className="space-y-3">
            {languages.map((lang) => (
              <div
                key={lang.code}
                className={`flex items-center justify-between p-3 rounded-lg ${lang.status === 'active'
                  ? 'bg-primary/10 border border-primary/20'
                  : 'bg-gray-50'
                  }`}
              >
                <span className="font-medium">{lang.name}</span>
                {lang.status === 'active' ? (
                  <span className="text-xs bg-primary text-white px-2 py-1 rounded-full">Active</span>
                ) : (
                  <span className="text-xs text-gray-400">Coming soon</span>
                )}
              </div>
            ))}
            <div className="flex items-center justify-center gap-2 text-xs text-gray-400 mt-4">
              <Icon name="Globe" size={14} className="text-gray-400" library="fi" />
              <p>More languages coming soon!</p>
            </div>
          </div>
        }
      />

      {/* Welcome Notification Modal */}
      <Modal
        isOpen={showNotificationModal}
        onClose={() => setShowNotificationModal(false)}
        type="success"
        title={
          <div className="flex items-center justify-center gap-2">
            <Icon name="Bell" size={24} className="text-primary" library="fi" />
            <span>Welcome to SabiLens!</span>
          </div>
        }
        message={
          <div className="space-y-4">
            <div className="flex justify-center">
              <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
                <Icon name="Shield" size={40} className="text-primary" library="fi" />
              </div>
            </div>
            <p className="text-gray-600">
              Hi {firstName}! We're excited to have you on board. Here's what you can do:
            </p>
            <ul className="text-left space-y-2 text-sm text-gray-500">
              <li className="flex items-center gap-2">
                <Icon name="CheckCircle" size={16} className="text-primary" library="fi" />
                <span>Scan products to verify authenticity</span>
              </li>
              <li className="flex items-center gap-2">
                <Icon name="Cpu" size={16} className="text-primary" library="fi" />
                <span>Get instant AI-powered results</span>
              </li>
              <li className="flex items-center gap-2">
                <Icon name="AlertTriangle" size={16} className="text-primary" library="fi" />
                <span>Report counterfeits to protect others</span>
              </li>
              <li className="flex items-center gap-2">
                <Icon name="Clock" size={16} className="text-primary" library="fi" />
                <span>Track your scan history</span>
              </li>
            </ul>
            <div className="bg-primary/5 p-4 rounded-xl mt-4">
              <p className="text-sm text-primary font-medium flex items-center justify-center gap-2">
                <Icon name="Camera" size={18} className="text-primary" library="fi" />
                Tap the camera button to start your first scan!
              </p>
            </div>
          </div>
        }
      />
    </>
  );
};

export default HomeScreen;