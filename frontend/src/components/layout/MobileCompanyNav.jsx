import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Icon from '../common/Icon';

const MobileCompanyNav = ({ isOpen, onClose, companyName }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { path: '/company/dashboard', icon: 'Grid', label: 'Overview' },
    { path: '/company/reports', icon: 'AlertTriangle', label: 'Counterfeit Reports' },
    { path: '/company/heatmap', icon: 'Map', label: 'Heat Map' },
    { path: '/company/registry', icon: 'Package', label: 'Product Registry' },
    { path: '/company/evidence', icon: 'Folder', label: 'Evidence Vault' },
    { path: '/company/settings', icon: 'Settings', label: 'Settings' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    onClose();
    navigate('/company/login');
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
                <span className="font-bold text-lg block truncate max-w-[120px]">{companyName || 'Company'}</span>
                <p className="text-xs text-gray-400">Brand Protection</p>
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

        {/* Navigation */}
        <nav className="p-4">
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
              <p className="font-medium text-sm truncate">Admin User</p>
              <p className="text-xs text-gray-400 truncate">admin@company.com</p>
            </div>
            <button 
              onClick={handleLogout}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Logout"
            >
              <Icon name="LogOut" size={18} className="text-gray-400" library="fi" />
            </button>
          </div>
        </div>
      </div>

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

export default MobileCompanyNav;