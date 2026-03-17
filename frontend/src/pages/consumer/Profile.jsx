import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ConsumerBottomNav from '../../components/layout/ConsumerBottomNav';
import ProfileScreen from '../../components/consumer/Profile/ProfileScreen';
import Modal from '../../components/common/Modal';
import Button from '../../components/common/Button';

const Profile = () => {
  const navigate = useNavigate();
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  // Get current user from localStorage
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  
  // Get full user data from users array
  const users = JSON.parse(localStorage.getItem('users') || '[]');
  const userData = users.find(u => u.phone === currentUser.phone) || {};

  // Get scan history for stats
  const historyKey = `scanHistory_${currentUser.phone}`;
  const scans = JSON.parse(localStorage.getItem(historyKey) || '[]');
  
  // Calculate real stats from actual scan data
  const stats = {
    reports: scans.length,
    verified: scans.filter(s => s.status === 'authentic').length,
    pending: scans.filter(s => s.status === 'caution' || s.status === 'pending').length,
    fake: scans.filter(s => s.status === 'fake').length
  };

  // Get member since date from user creation
  const getMemberSince = () => {
    if (userData.createdAt) {
      const date = new Date(userData.createdAt);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long',
        day: 'numeric'
      });
    }
    return 'January 2026';
  };

  // Calculate account age in days
  const getAccountAge = () => {
    if (userData.createdAt) {
      const created = new Date(userData.createdAt);
      const now = new Date();
      const diffTime = Math.abs(now - created);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays;
    }
    return 30;
  };

  // Get last active date
  const getLastActive = () => {
    if (scans.length > 0) {
      const lastScan = new Date(scans[0].timestamp);
      return lastScan.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      });
    }
    return 'Never';
  };

  // Calculate scan frequency
  const getScanFrequency = () => {
    const days = getAccountAge();
    if (days > 0 && stats.reports > 0) {
      const avg = (stats.reports / days).toFixed(1);
      return `${avg} per day`;
    }
    return 'No scans yet';
  };

  const menuItems = [
    { 
      icon: 'Phone', 
      label: 'Phone Number', 
      value: `+234 ${userData.phone || 'Not set'}` 
    },
    { 
      icon: 'Mail', 
      label: 'Email', 
      value: userData.email || 'Not set' 
    },
    { 
      icon: 'Globe', 
      label: 'Language', 
      value: userData.language || 'English' 
    },
    { 
      icon: 'Star', 
      label: 'Reputation Score', 
      value: stats.verified > 0 ? '98%' : 'New User' 
    },
    { 
      icon: 'CheckCircle', 
      label: 'Verified Reports', 
      value: stats.verified.toString() 
    },
    { 
      icon: 'AlertTriangle', 
      label: 'Fake Detected', 
      value: stats.fake.toString() 
    },
  ];

  // Add dynamic activity summary items
  const activityItems = [
    {
      icon: 'Calendar',
      label: 'Member Since',
      value: getMemberSince()
    },
    {
      icon: 'Clock',
      label: 'Last Active',
      value: getLastActive()
    },
    {
      icon: 'Activity',
      label: 'Scan Frequency',
      value: getScanFrequency()
    },
    {
      icon: 'Award',
      label: 'Total Scans',
      value: stats.reports.toString()
    }
  ];

  const handleSettingClick = (setting) => {
    switch(setting) {
      case 'privacy':
        navigate('/privacy-policy');
        break;
      case 'terms':
        navigate('/terms-of-service');
        break;
      case 'help':
        navigate('/help-support');
        break;
      default:
        break;
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    setShowLogoutModal(false);
    navigate('/login');
  };

  const handleEditProfile = () => {
    navigate('/edit-profile');
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      <ProfileScreen
        userData={userData}
        stats={stats}
        menuItems={menuItems}
        activityItems={activityItems}
        onSettingClick={handleSettingClick}
        onLogout={() => setShowLogoutModal(true)}
        onEditProfile={handleEditProfile}
      />
      <ConsumerBottomNav />

      {/* Logout Confirmation Modal */}
      <Modal
        isOpen={showLogoutModal}
        onClose={() => setShowLogoutModal(false)}
        type="warning"
        title="Confirm Logout"
        message={
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to log out of your account?
            </p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setShowLogoutModal(false)}
                fullWidth
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleLogout}
                fullWidth
              >
                Yes, Logout
              </Button>
            </div>
          </div>
        }
      />
    </div>
  );
};

export default Profile;