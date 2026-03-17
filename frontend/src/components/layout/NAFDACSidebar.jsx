import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Icon from '../common/Icon';
import Modal from '../common/Modal';
import Button from '../common/Button';

const NAFDACSidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const menuItems = [
    { path: '/nafdac/dashboard', icon: 'Map', label: 'National Heat Map' },
    { path: '/nafdac/alerts', icon: 'AlertTriangle', label: 'High-Risk Alerts' },
    { path: '/nafdac/cases', icon: 'Folder', label: 'Evidence Cases' },
    { path: '/nafdac/vendors', icon: 'Users', label: 'Vendor Recurrence' },
    { path: '/nafdac/analytics', icon: 'PieChart', label: 'Category Analytics' },
    { path: '/nafdac/export', icon: 'Download', label: 'Export Data' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    setShowLogoutModal(false);
    navigate('/nafdac/login');
  };

  // Get current user
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  const userInitials = currentUser.firstName?.[0] || 'N';

  return (
    <>
      <div className="hidden lg:flex lg:flex-col w-64 bg-white h-screen fixed left-0 top-0 shadow-soft border-r border-gray-100">
        {/* NAFDAC Logo */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
              <Icon name="Shield" size={20} className="text-primary" library="fi" />
            </div>
            <div>
              <span className="font-bold text-lg">NAFDAC</span>
              <p className="text-xs text-gray-400">Regulatory Portal</p>
            </div>
          </div>
        </div>

        {/* Alert Badge */}
        <div className="px-4 py-3">
          <div className="bg-danger/10 text-danger rounded-xl p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icon name="Bell" size={16} library="fi" />
              <span className="text-sm font-medium">Critical Alerts</span>
            </div>
            <span className="bg-danger text-white text-xs px-2 py-1 rounded-full">12</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 overflow-y-auto">
          <ul className="space-y-2">
            {menuItems.map((item) => (
              <li key={item.path}>
                <button
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    location.pathname === item.path
                      ? 'bg-primary/10 text-primary'
                      : 'text-gray-500 hover:bg-gray-50'
                  }`}
                >
                  <Icon name={item.icon} size={20} />
                  <span className="font-medium">{item.label}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* User Profile - Bottom */}
        <div className="p-4 border-t border-gray-100 bg-white">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-primary font-medium text-sm">{userInitials}</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">NAFDAC Admin</p>
              <p className="text-xs text-gray-400 truncate">admin@nafdac.gov.ng</p>
            </div>
            <button 
              onClick={() => setShowLogoutModal(true)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors flex-shrink-0 group"
              title="Logout"
            >
              <Icon name="LogOut" size={18} className="text-gray-400 group-hover:text-danger transition-colors" library="fi" />
            </button>
          </div>

          {/* Footer */}
          <div className="mt-3 pt-3 border-t border-gray-50">
            <p className="text-xs text-gray-400 text-center">
              © 2026 NAFDAC • v1.0.0
            </p>
          </div>
        </div>
      </div>

      {/* Logout Confirmation Modal */}
      <Modal
        isOpen={showLogoutModal}
        onClose={() => setShowLogoutModal(false)}
        type="warning"
        title="Confirm Logout"
        message={
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to log out of the NAFDAC portal?
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
    </>
  );
};

export default NAFDACSidebar;