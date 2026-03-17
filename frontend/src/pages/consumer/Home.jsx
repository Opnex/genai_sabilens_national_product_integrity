import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ConsumerBottomNav from '../../components/layout/ConsumerBottomNav';
import HomeScreen from '../../components/consumer/Home/HomeScreen';
import { getRecentScans } from '../../services/scanHistory';

const Home = () => {
  const navigate = useNavigate();
  const [isFirstTimeUser, setIsFirstTimeUser] = useState(false);
  const [recentScans, setRecentScans] = useState([]);
  const [profileImage, setProfileImage] = useState(null);

  // Get current user from localStorage
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  const firstName = currentUser.firstName || 'Guest';
  
  // Get full user data from users array
  const users = JSON.parse(localStorage.getItem('users') || '[]');
  const userData = users.find(u => u.phone === currentUser.phone) || {};
  
  // Get profile image from user data
  useEffect(() => {
    if (userData.profileImage) {
      setProfileImage(userData.profileImage);
    }
  }, [userData.profileImage]);
  
  // Generate initials from first and last name
  const getInitials = () => {
    const first = currentUser.firstName?.[0] || '';
    const last = currentUser.lastName?.[0] || '';
    return (first + last).toUpperCase() || 'U';
  };

  // Load recent scans
  useEffect(() => {
    loadRecentScans();
  }, []);

  const loadRecentScans = () => {
    const scans = getRecentScans(5);
    console.log('Loaded scans:', scans);
    setRecentScans(scans);
  };

  // Check if this is first time user
  useEffect(() => {
    const hasScanned = localStorage.getItem('hasScanned') === 'true';
    const hasSeenWelcome = localStorage.getItem('hasSeenWelcome') === 'true';
    
    if (!hasSeenWelcome && !hasScanned) {
      setIsFirstTimeUser(true);
      localStorage.setItem('hasSeenWelcome', 'true');
    }
  }, []);

  const handleScanPress = () => {
    navigate('/scan');
  };

  const handleViewAll = () => {
    navigate('/scan-history');
  };

  const handleScanItemPress = (scan) => {
    if (scan.status === 'authentic') {
      navigate('/scan/safe');
    } else if (scan.status === 'fake') {
      navigate('/scan/fake');
    } else {
      navigate('/scan/caution');
    }
  };

  const handleProfilePress = () => {
    navigate('/profile');
  };

  // Refresh scans when returning to home
  useEffect(() => {
    const handleFocus = () => {
      loadRecentScans();
      
      // Refresh profile image when returning to home
      const updatedUsers = JSON.parse(localStorage.getItem('users') || '[]');
      const updatedUserData = updatedUsers.find(u => u.phone === currentUser.phone) || {};
      if (updatedUserData.profileImage) {
        setProfileImage(updatedUserData.profileImage);
      }
    };
    
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [currentUser.phone]);

  return (
    <div className="min-h-screen bg-background pb-20">
      <HomeScreen
        firstName={firstName}
        userInitials={getInitials()}
        profileImage={profileImage}
        recentScans={recentScans}
        onScanPress={handleScanPress}
        onViewAllPress={handleViewAll}
        onScanItemPress={handleScanItemPress}
        onProfilePress={handleProfilePress}
        isFirstTimeUser={isFirstTimeUser}
      />
      <ConsumerBottomNav />
    </div>
  );
};

export default Home;