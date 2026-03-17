import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Icon from '../common/Icon';
import Modal from '../common/Modal';
import Button from '../common/Button';

const MobileNAFDACNav = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();
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
    onClose();
    navigate('/nafdac/login');
  };

  const handleNavigation = (path) => {
    navigate(path);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 z-50 lg:hidden"
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className="fixed top-0 left-0 bottom-0 w-64 bg-white z-50 lg:hidden shadow-soft animate-slideIn">
        {/* Header */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                <Icon name="Shield" size={20} className="text-primary" library="fi" />
              </div>
              <div>
                <span className="font-bold text-lg">NAFDAC</span>
                <p className="text-xs text-gray-400">Regulatory Portal</p>
              </div>
            </div>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <Icon name="X" size={20} className="text-gray-500" library="fi" />
            </button>
          </div>
        </div>

        {/* Alert Badge */}
        <div className="px-4 py-2">
          <div className="bg-danger/10 text-danger rounded-xl p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icon name="Bell" size={16} library="fi" />
              <span className="text-sm font-medium">Critical Alerts</span>
            </div>
            <span className="bg-danger text-white text-xs px-2 py-1 rounded-full">12</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 flex-1 overflow-y-auto">
          <ul className="space-y-2">
            {menuItems.map((item) => (
              <li key={item.path}>
                <button
                  onClick={() => handleNavigation(item.path)}
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

        {/* User Profile */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-100 bg-white">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
              <Icon name="User" size={18} className="text-primary" library="fi" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">NAFDAC Admin</p>
              <p className="text-xs text-gray-400 truncate">admin@nafdac.gov.ng</p>
            </div>
            <button 
              onClick={() => setShowLogoutModal(true)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Logout"
            >
              <Icon name="LogOut" size={18} className="text-gray-400" library="fi" />
            </button>
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

      <style jsx>{`
        @keyframes slideIn {
          from {
            transform: translateX(-100%);
          }
          to {
            transform: translateX(0);
          }
        }
        .animate-slideIn {
          animation: slideIn 0.3s ease-out;
        }
      `}</style>
    </>
  );
};

export default MobileNAFDACNav;