import React from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../common/Icon';
import Card from '../../common/Card';

const ProfileScreen = ({ 
  userData = {},
  stats = { reports: 0, verified: 0, pending: 0, fake: 0 },
  menuItems = [],
  activityItems = [],
  onSettingClick, 
  onLogout,
  onEditProfile
}) => {
  const navigate = useNavigate();
  
  const fullName = `${userData.firstName || ''} ${userData.lastName || ''}`.trim() || 'User';
  const initials = `${(userData.firstName?.[0] || '')}${(userData.lastName?.[0] || '')}`.toUpperCase() || 'U';
  const profileImage = userData.profileImage;

  return (
    <div className="px-6 py-8">
      {/* Header with Edit Button */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <button 
          onClick={onEditProfile}
          className="px-4 py-2 bg-primary/10 text-primary rounded-xl flex items-center gap-2 hover:bg-primary/20 transition-colors"
        >
          <Icon name="Edit" size={16} className="text-primary" library="fi" />
          <span className="text-sm font-medium">Edit Profile</span>
        </button>
      </div>

      {/* Profile Header */}
      <Card className="mb-6 text-center relative overflow-hidden">
        {/* Background decoration with user's join year */}
        <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-r from-primary/20 to-primary/5">
          <div className="absolute top-2 right-2 bg-white/80 backdrop-blur px-3 py-1 rounded-full text-xs text-primary">
            <Icon name="Award" size={12} className="inline mr-1" library="fi" />
            {activityItems.find(a => a.label === 'Member Since')?.value.split(' ')[1] || '2026'}
          </div>
        </div>
        
        <div className="relative pt-8 pb-6">
          {/* Avatar with image or initials */}
          <div className="w-28 h-28 mx-auto mb-4 relative">
            <div className="w-full h-full rounded-full overflow-hidden border-4 border-white shadow-lg bg-primary/10">
              {profileImage ? (
                <img 
                  src={profileImage} 
                  alt={fullName}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-primary">
                  <span className="text-white text-3xl font-bold">{initials}</span>
                </div>
              )}
            </div>
            {/* Online status indicator */}
            <div className="absolute bottom-1 right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full" />
          </div>
          
          <h2 className="text-xl font-semibold mb-1">{fullName}</h2>
          <p className="text-gray-400 text-sm mb-4 flex items-center justify-center gap-1">
            <Icon name="Phone" size={12} className="text-gray-400" library="fi" />
            +234 {userData.phone || 'Not set'}
          </p>
          
          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-2 max-w-xs mx-auto">
            <div className="text-center">
              <p className="text-xl font-bold text-primary">{stats.reports}</p>
              <p className="text-[10px] text-gray-400">Total</p>
            </div>
            <div className="text-center">
              <p className="text-xl font-bold text-success">{stats.verified}</p>
              <p className="text-[10px] text-gray-400">Safe</p>
            </div>
            <div className="text-center">
              <p className="text-xl font-bold text-warning">{stats.pending}</p>
              <p className="text-[10px] text-gray-400">Caution</p>
            </div>
            <div className="text-center">
              <p className="text-xl font-bold text-danger">{stats.fake}</p>
              <p className="text-[10px] text-gray-400">Fake</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Personal Information */}
      <Card className="mb-6">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Icon name="User" size={18} className="text-primary" library="fi" />
          Personal Information
        </h3>
        <div className="space-y-3">
          {menuItems.slice(0, 3).map((item, index) => (
            <div
              key={item.label}
              className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
            >
              <div className="flex items-center gap-3">
                <Icon name={item.icon} size={18} className="text-gray-400" library="fi" />
                <span className="text-sm text-gray-600">{item.label}</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{item.value}</span>
            </div>
          ))}
          
          {/* Location if available */}
          {userData.city && userData.state && (
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center gap-3">
                <Icon name="MapPin" size={18} className="text-gray-400" library="fi" />
                <span className="text-sm text-gray-600">Location</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{userData.city}, {userData.state}</span>
            </div>
          )}
        </div>
      </Card>

      {/* Activity Summary - Now Fully Personalized */}
      <Card className="mb-6">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Icon name="Activity" size={18} className="text-primary" library="fi" />
          Activity Summary
        </h3>
        <div className="space-y-3">
          {activityItems.map((item, index) => (
            <div
              key={item.label}
              className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
            >
              <div className="flex items-center gap-3">
                <Icon name={item.icon} size={18} className="text-gray-400" library="fi" />
                <span className="text-sm text-gray-600">{item.label}</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{item.value}</span>
            </div>
          ))}
        </div>

        {/* Achievement Badges based on activity */}
        {stats.reports > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-xs font-medium text-gray-500 mb-2">Achievements</p>
            <div className="flex flex-wrap gap-2">
              {stats.reports >= 1 && (
                <span className="text-xs bg-primary/10 text-primary px-3 py-1 rounded-full flex items-center gap-1">
                  <Icon name="Award" size={12} library="fi" />
                  First Scan
                </span>
              )}
              {stats.verified >= 5 && (
                <span className="text-xs bg-success/10 text-success px-3 py-1 rounded-full flex items-center gap-1">
                  <Icon name="CheckCircle" size={12} library="fi" />
                  5 Verified
                </span>
              )}
              {stats.reports >= 10 && (
                <span className="text-xs bg-primary/10 text-primary px-3 py-1 rounded-full flex items-center gap-1">
                  <Icon name="Star" size={12} library="fi" />
                  10 Scans
                </span>
              )}
              {stats.fake >= 1 && (
                <span className="text-xs bg-danger/10 text-danger px-3 py-1 rounded-full flex items-center gap-1">
                  <Icon name="Shield" size={12} library="fi" />
                  Crime Fighter
                </span>
              )}
            </div>
          </div>
        )}
      </Card>

      {/* Settings */}
      <Card className="mb-6">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Icon name="Settings" size={18} className="text-primary" library="fi" />
          Settings
        </h3>
        <button 
          onClick={() => onSettingClick('privacy')}
          className="flex items-center justify-between w-full py-3 border-b border-gray-100 hover:bg-gray-50 px-3 rounded-lg transition-colors group"
        >
          <div className="flex items-center gap-3">
            <Icon name="Shield" size={18} className="text-gray-400 group-hover:text-primary transition-colors" library="fi" />
            <span className="text-gray-600 group-hover:text-primary transition-colors">Privacy Policy</span>
          </div>
          <Icon name="ChevronRight" size={16} className="text-gray-400 group-hover:text-primary transition-colors" library="fi" />
        </button>
        
        <button 
          onClick={() => onSettingClick('terms')}
          className="flex items-center justify-between w-full py-3 border-b border-gray-100 hover:bg-gray-50 px-3 rounded-lg transition-colors group"
        >
          <div className="flex items-center gap-3">
            <Icon name="FileText" size={18} className="text-gray-400 group-hover:text-primary transition-colors" library="fi" />
            <span className="text-gray-600 group-hover:text-primary transition-colors">Terms of Service</span>
          </div>
          <Icon name="ChevronRight" size={16} className="text-gray-400 group-hover:text-primary transition-colors" library="fi" />
        </button>
        
        <button 
          onClick={() => onSettingClick('help')}
          className="flex items-center justify-between w-full py-3 hover:bg-gray-50 px-3 rounded-lg transition-colors group"
        >
          <div className="flex items-center gap-3">
            <Icon name="HelpCircle" size={18} className="text-gray-400 group-hover:text-primary transition-colors" library="fi" />
            <span className="text-gray-600 group-hover:text-primary transition-colors">Help & Support</span>
          </div>
          <Icon name="ChevronRight" size={16} className="text-gray-400 group-hover:text-primary transition-colors" library="fi" />
        </button>
      </Card>

      {/* Version Info */}
      <div className="text-center mb-4">
        <p className="text-xs text-gray-400">Version 1.0.0</p>
        <p className="text-xs text-gray-300 mt-1">© 2026 SabiLens. All rights reserved.</p>
      </div>

      {/* Logout Button */}
      <button 
        onClick={onLogout}
        className="w-full text-center text-danger py-4 hover:bg-danger/5 rounded-xl transition-colors font-medium flex items-center justify-center gap-2"
      >
        <Icon name="LogOut" size={18} className="text-danger" library="fi" />
        Log Out
      </button>
    </div>
  );
};

export default ProfileScreen;