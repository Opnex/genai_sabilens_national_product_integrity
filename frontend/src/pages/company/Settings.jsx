import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CompanySidebar from '../../components/layout/CompanySidebar';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import MobileCompanyNav from '../../components/layout/MobileCompanyNav';

const CompanySettings = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('profile');
  const [companyData, setCompanyData] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0);
  const [showMobileTabs, setShowMobileTabs] = useState(false);
  
  const [formData, setFormData] = useState({
    companyName: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    website: '',
    notificationEmail: true,
    notificationAlerts: true,
    notificationReports: true,
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [touched, setTouched] = useState({});
  const [loading, setLoading] = useState(true);

  // Get current user
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  const users = JSON.parse(localStorage.getItem('users') || '[]');
  const companies = JSON.parse(localStorage.getItem('companies') || '[]');

  useEffect(() => {
    loadCompanyData();
    
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
      if (window.innerWidth >= 768) {
        setShowMobileTabs(false);
      }
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const loadCompanyData = () => {
    setLoading(true);
    
    // Find company
    const company = companies.find(c => c.id === currentUser.companyId);
    
    if (!company) {
      navigate('/company/dashboard');
      return;
    }
    
    setCompanyData(company);
    
    setFormData({
      companyName: company.name || '',
      email: company.email || '',
      phone: company.phone || '',
      address: company.address || '',
      city: company.city || '',
      state: company.state || '',
      website: company.website || '',
      notificationEmail: true,
      notificationAlerts: true,
      notificationReports: true,
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    
    setLoading(false);
  };

  const validateField = (name, value) => {
    switch(name) {
      case 'companyName':
        return value.trim() ? '' : 'Company name is required';
      case 'email':
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? '' : 'Valid email is required';
      case 'phone':
        return /^\+234[0-9]{10}$/.test(value) ? '' : 'Valid phone number required';
      case 'address':
        return value.trim() ? '' : 'Address is required';
      case 'city':
        return value.trim() ? '' : 'City is required';
      case 'state':
        return value ? '' : 'State is required';
      case 'newPassword':
        if (!value) return '';
        if (value.length < 8) return 'Password must be at least 8 characters';
        if (!/[A-Z]/.test(value)) return 'Include at least one uppercase letter';
        if (!/[0-9]/.test(value)) return 'Include at least one number';
        return '';
      case 'confirmPassword':
        return value === formData.newPassword ? '' : 'Passwords do not match';
      default:
        return '';
    }
  };

  const getFieldError = (name) => {
    if (!touched[name]) return '';
    return validateField(name, formData[name]);
  };

  const isProfileValid = () => {
    const requiredFields = ['companyName', 'email', 'phone', 'address', 'city', 'state'];
    return requiredFields.every(field => !validateField(field, formData[field]));
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleBlur = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
  };

  const handleSaveProfile = () => {
    const requiredFields = ['companyName', 'email', 'phone', 'address', 'city', 'state'];
    const touchedFields = requiredFields.reduce((acc, field) => ({ ...acc, [field]: true }), {});
    setTouched(touchedFields);

    if (!isProfileValid()) return;

    // Update company in companies array
    const updatedCompanies = companies.map(c => {
      if (c.id === currentUser.companyId) {
        return {
          ...c,
          name: formData.companyName,
          email: formData.email,
          phone: formData.phone,
          address: formData.address,
          city: formData.city,
          state: formData.state,
          website: formData.website
        };
      }
      return c;
    });

    localStorage.setItem('companies', JSON.stringify(updatedCompanies));

    // Update current user with new company name
    localStorage.setItem('currentUser', JSON.stringify({
      ...currentUser,
      companyName: formData.companyName
    }));

    setShowSuccessModal(true);
  };

  const handleChangePassword = () => {
    if (formData.newPassword !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    if (formData.newPassword && formData.newPassword.length < 8) {
      alert('Password must be at least 8 characters');
      return;
    }

    const updatedUsers = users.map(u => {
      if (u.id === currentUser.id) {
        return {
          ...u,
          password: formData.newPassword
        };
      }
      return u;
    });

    localStorage.setItem('users', JSON.stringify(updatedUsers));

    setFormData(prev => ({
      ...prev,
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }));

    setShowSuccessModal(true);
  };

  const handleDeleteAccount = () => {
    setShowConfirmModal(true);
  };

  const confirmDelete = () => {
    const updatedCompanies = companies.filter(c => c.id !== currentUser.companyId);
    localStorage.setItem('companies', JSON.stringify(updatedCompanies));

    const updatedUsers = users.filter(u => u.companyId !== currentUser.companyId);
    localStorage.setItem('users', JSON.stringify(updatedUsers));

    localStorage.removeItem('currentUser');

    setShowConfirmModal(false);
    navigate('/company/login');
  };

  const nigerianStates = [
    'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
    'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo',
    'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa',
    'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
  ];

  const tabs = [
    { id: 'profile', label: 'Company Profile', icon: 'Building', description: 'Manage your company information' },
    { id: 'notifications', label: 'Notifications', icon: 'Bell', description: 'Configure alert preferences' },
    { id: 'security', label: 'Security', icon: 'Lock', description: 'Password and account security' },
    { id: 'billing', label: 'Billing', icon: 'CreditCard', description: 'Subscription and invoices' },
    { id: 'team', label: 'Team Members', icon: 'Users', description: 'Manage team access' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        {windowWidth < 768 ? (
          <div className="flex flex-col items-center justify-center h-screen">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-gray-500">Loading settings...</p>
          </div>
        ) : (
          <>
            <CompanySidebar />
            <div className="lg:ml-64 p-8 flex justify-center items-center h-screen">
              <div className="text-center">
                <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-gray-500">Loading settings...</p>
              </div>
            </div>
          </>
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Header */}
      {windowWidth < 768 && (
        <div className="fixed top-0 left-0 right-0 bg-white shadow-soft z-40 px-4 py-3">
          <div className="flex items-center justify-between">
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <Icon name="Menu" size={24} className="text-gray-600" library="fi" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                <Icon name="Settings" size={16} className="text-primary" library="fi" />
              </div>
              <span className="font-bold text-lg">Settings</span>
            </div>
            <button 
              onClick={() => setShowMobileTabs(!showMobileTabs)}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <Icon name={showMobileTabs ? 'X' : 'ChevronDown'} size={20} className="text-gray-600" library="fi" />
            </button>
          </div>
          
          {/* Mobile Tab Selector */}
          {showMobileTabs && (
            <div className="mt-3 space-y-2 border-t border-gray-100 pt-3">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    setShowMobileTabs(false);
                  }}
                  className={`w-full flex items-center gap-3 p-3 rounded-xl transition-colors ${
                    activeTab === tab.id ? 'bg-primary/10 text-primary' : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon name={tab.icon} size={18} />
                  <div className="text-left">
                    <p className="font-medium">{tab.label}</p>
                    <p className="text-xs text-gray-400">{tab.description}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Mobile Menu */}
      <MobileCompanyNav 
        isOpen={isMobileMenuOpen} 
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* Desktop Sidebar */}
      {windowWidth >= 768 && <CompanySidebar />}
      
      {/* Main Content */}
      <div className={`${windowWidth >= 768 ? 'lg:ml-64' : ''} ${windowWidth < 768 ? 'pt-16' : 'pt-8'} px-4 md:px-6 lg:px-8 pb-8`}>
        {/* Desktop Header */}
        {windowWidth >= 768 && (
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900">Company Settings</h1>
            <p className="text-gray-500 mt-1">Manage your company profile and preferences</p>
          </div>
        )}

        {/* Desktop Tabs */}
        {windowWidth >= 768 && (
          <div className="flex gap-2 mb-6 border-b border-gray-200 overflow-x-auto pb-1">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon name={tab.icon} size={18} />
                {tab.label}
              </button>
            ))}
          </div>
        )}

        {/* Tab Content */}
        <Card className="overflow-hidden">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="p-4 md:p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Company Information</h2>
                <p className="text-sm text-gray-500 mt-1">Update your company details and contact information</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                <div>
                  <label className="text-sm text-gray-500 mb-1 block">Company Name *</label>
                  <input
                    type="text"
                    name="companyName"
                    value={formData.companyName}
                    onChange={handleChange}
                    onBlur={() => handleBlur('companyName')}
                    className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                      getFieldError('companyName') 
                        ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                        : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                  />
                  {getFieldError('companyName') && (
                    <p className="text-danger text-xs mt-1">{getFieldError('companyName')}</p>
                  )}
                </div>

                <div>
                  <label className="text-sm text-gray-500 mb-1 block">Business Email *</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    onBlur={() => handleBlur('email')}
                    className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                      getFieldError('email') 
                        ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                        : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                  />
                  {getFieldError('email') && (
                    <p className="text-danger text-xs mt-1">{getFieldError('email')}</p>
                  )}
                </div>

                <div>
                  <label className="text-sm text-gray-500 mb-1 block">Phone Number *</label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    onBlur={() => handleBlur('phone')}
                    className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                      getFieldError('phone') 
                        ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                        : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                    placeholder="+2348012345678"
                  />
                  {getFieldError('phone') && (
                    <p className="text-danger text-xs mt-1">{getFieldError('phone')}</p>
                  )}
                </div>

                <div>
                  <label className="text-sm text-gray-500 mb-1 block">Website</label>
                  <input
                    type="url"
                    name="website"
                    value={formData.website}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
                    placeholder="https://www.yourcompany.com"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="text-sm text-gray-500 mb-1 block">Business Address *</label>
                  <input
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    onBlur={() => handleBlur('address')}
                    className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                      getFieldError('address') 
                        ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                        : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                    placeholder="Street address"
                  />
                  {getFieldError('address') && (
                    <p className="text-danger text-xs mt-1">{getFieldError('address')}</p>
                  )}
                </div>

                <div>
                  <label className="text-sm text-gray-500 mb-1 block">City *</label>
                  <input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    onBlur={() => handleBlur('city')}
                    className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                      getFieldError('city') 
                        ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                        : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                    placeholder="Lagos"
                  />
                  {getFieldError('city') && (
                    <p className="text-danger text-xs mt-1">{getFieldError('city')}</p>
                  )}
                </div>

                <div>
                  <label className="text-sm text-gray-500 mb-1 block">State *</label>
                  <select
                    name="state"
                    value={formData.state}
                    onChange={handleChange}
                    onBlur={() => handleBlur('state')}
                    className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                      getFieldError('state') 
                        ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                        : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                  >
                    <option value="">Select State</option>
                    {nigerianStates.map(state => (
                      <option key={state} value={state}>{state}</option>
                    ))}
                  </select>
                  {getFieldError('state') && (
                    <p className="text-danger text-xs mt-1">{getFieldError('state')}</p>
                  )}
                </div>
              </div>

              <div className="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-gray-100">
                <Button variant="outline" onClick={() => navigate('/company/dashboard')} fullWidth={windowWidth < 640}>
                  Cancel
                </Button>
                <Button variant="primary" onClick={handleSaveProfile} fullWidth={windowWidth < 640}>
                  Save Changes
                </Button>
              </div>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="p-4 md:p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Notification Preferences</h2>
                <p className="text-sm text-gray-500 mt-1">Choose how you want to receive alerts</p>
              </div>
              
              <div className="space-y-4">
                <label className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg gap-3">
                  <div>
                    <p className="font-medium">Email Notifications</p>
                    <p className="text-sm text-gray-500">Receive reports and alerts via email</p>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="notificationEmail"
                      checked={formData.notificationEmail}
                      onChange={handleChange}
                      className="w-5 h-5 text-primary rounded focus:ring-primary"
                    />
                  </div>
                </label>

                <label className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg gap-3">
                  <div>
                    <p className="font-medium">Push Notifications</p>
                    <p className="text-sm text-gray-500">Get instant alerts for new counterfeits</p>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="notificationAlerts"
                      checked={formData.notificationAlerts}
                      onChange={handleChange}
                      className="w-5 h-5 text-primary rounded focus:ring-primary"
                    />
                  </div>
                </label>

                <label className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg gap-3">
                  <div>
                    <p className="font-medium">Weekly Reports</p>
                    <p className="text-sm text-gray-500">Receive weekly summary of all activities</p>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="notificationReports"
                      checked={formData.notificationReports}
                      onChange={handleChange}
                      className="w-5 h-5 text-primary rounded focus:ring-primary"
                    />
                  </div>
                </label>
              </div>

              <div className="flex justify-end pt-4 border-t border-gray-100">
                <Button variant="primary" onClick={() => setShowSuccessModal(true)} fullWidth={windowWidth < 640}>
                  Save Preferences
                </Button>
              </div>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <div className="p-4 md:p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Change Password</h2>
                <p className="text-sm text-gray-500 mt-1">Update your password regularly for security</p>
              </div>
              
              <div className="space-y-4 max-w-md">
                <div>
                  <label className="text-sm text-gray-500 mb-1 block">Current Password</label>
                  <input
                    type="password"
                    name="currentPassword"
                    value={formData.currentPassword}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
                    placeholder="Enter current password"
                  />
                </div>

                <div>
                  <label className="text-sm text-gray-500 mb-1 block">New Password</label>
                  <input
                    type="password"
                    name="newPassword"
                    value={formData.newPassword}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
                    placeholder="Enter new password"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Minimum 8 characters with uppercase and number
                  </p>
                </div>

                <div>
                  <label className="text-sm text-gray-500 mb-1 block">Confirm New Password</label>
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
                    placeholder="Confirm new password"
                  />
                </div>
              </div>

              <div className="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-gray-100">
                <Button variant="outline" onClick={() => {
                  setFormData(prev => ({
                    ...prev,
                    currentPassword: '',
                    newPassword: '',
                    confirmPassword: ''
                  }));
                }} fullWidth={windowWidth < 640}>
                  Clear
                </Button>
                <Button variant="primary" onClick={handleChangePassword} fullWidth={windowWidth < 640}>
                  Update Password
                </Button>
              </div>

              {/* Danger Zone */}
              <div className="mt-8 pt-6 border-t-2 border-danger/20">
                <h3 className="text-lg font-semibold text-danger mb-4">Danger Zone</h3>
                <div className="bg-danger/5 p-4 md:p-6 rounded-lg">
                  <p className="text-sm text-gray-600 mb-4">
                    Once you delete your company account, there is no going back. All your data will be permanently removed.
                  </p>
                  <Button variant="danger" onClick={handleDeleteAccount} fullWidth={windowWidth < 640}>
                    Delete Company Account
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Billing Tab */}
          {activeTab === 'billing' && (
            <div className="p-4 md:p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Billing Information</h2>
                <p className="text-sm text-gray-500 mt-1">Manage your subscription and invoices</p>
              </div>
              
              <div className="bg-gradient-to-r from-primary/10 to-primary/5 p-6 md:p-8 rounded-lg text-center">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Icon name="CreditCard" size={32} className="text-primary" library="fi" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Free Plan</h3>
                <p className="text-gray-500 mb-6">You are currently on the free trial with full access</p>
                <Button variant="primary" fullWidth={windowWidth < 640}>
                  Upgrade to Premium
                </Button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Card className="p-4">
                  <p className="text-sm text-gray-400 mb-1">Current Plan</p>
                  <p className="text-lg font-semibold">Basic - Free</p>
                  <p className="text-xs text-gray-400 mt-2">Includes basic features</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-gray-400 mb-1">Next Billing</p>
                  <p className="text-lg font-semibold">N/A</p>
                  <p className="text-xs text-gray-400 mt-2">No upcoming charges</p>
                </Card>
              </div>

              <div className="pt-4 border-t border-gray-100">
                <h4 className="font-medium mb-3">Payment Methods</h4>
                <p className="text-sm text-gray-400 text-center py-4">
                  No payment methods added yet
                </p>
              </div>
            </div>
          )}

          {/* Team Tab */}
          {activeTab === 'team' && (
            <div className="p-4 md:p-6 space-y-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">Team Members</h2>
                  <p className="text-sm text-gray-500 mt-1">Manage who has access to your company dashboard</p>
                </div>
                <Button variant="primary" size="sm" fullWidth={windowWidth < 640}>
                  Invite Member
                </Button>
              </div>

              <div className="space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-primary font-medium">A</span>
                    </div>
                    <div>
                      <p className="font-medium">Admin User</p>
                      <p className="text-sm text-gray-400 break-all">{currentUser.email}</p>
                    </div>
                  </div>
                  <span className="text-xs bg-primary/10 text-primary px-3 py-1.5 rounded-full self-start sm:self-center">
                    Admin
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-100">
                <p className="text-sm text-gray-400 text-center">
                  More team management features coming soon
                </p>
              </div>
            </div>
          )}
        </Card>
      </div>

      {/* Success Modal */}
      <Modal
        isOpen={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        type="success"
        title="Settings Updated"
        message="Your changes have been saved successfully."
      />

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        type="warning"
        title="Delete Company Account"
        message={
          <div>
            <p className="text-gray-600 mb-4">
              Are you absolutely sure you want to delete your company account? This action cannot be undone and all your data will be permanently lost.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <Button variant="outline" onClick={() => setShowConfirmModal(false)} fullWidth={windowWidth < 640}>
                Cancel
              </Button>
              <Button variant="danger" onClick={confirmDelete} fullWidth={windowWidth < 640}>
                Yes, Delete Account
              </Button>
            </div>
          </div>
        }
      />
    </div>
  );
};

export default CompanySettings;