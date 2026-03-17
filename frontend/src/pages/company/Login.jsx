import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';

const CompanyLogin = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [touched, setTouched] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [modalConfig, setModalConfig] = useState({
    type: 'error',
    title: '',
    message: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleBlur = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
  };

  const validateField = (name, value) => {
    switch(name) {
      case 'email':
        return value ? '' : 'Email is required';
      case 'password':
        return value ? '' : 'Password is required';
      default:
        return '';
    }
  };

  const getFieldError = (name) => {
    if (!touched[name]) return '';
    return validateField(name, formData[name]);
  };

  const isFormValid = () => {
    return formData.email && formData.password;
  };

  const handleLogin = (e) => {
    e.preventDefault();
    
    setTouched({ email: true, password: true });
    
    if (!isFormValid()) {
      setModalConfig({
        type: 'error',
        title: 'Validation Error',
        message: 'Please fill in all required fields.'
      });
      setModalOpen(true);
      return;
    }

    // Get users from localStorage
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const companies = JSON.parse(localStorage.getItem('companies') || '[]');
    
    console.log('Login attempt with:', formData.email);
    console.log('All users:', users);
    console.log('All companies:', companies);
    
    // Find user with matching email and password (case insensitive)
    const user = users.find(u => 
      u.email?.toLowerCase() === formData.email.toLowerCase() && 
      u.password === formData.password
    );
    
    console.log('Found user:', user);
    
    if (!user) {
      setModalConfig({
        type: 'error',
        title: 'Login Failed',
        message: 'Invalid email or password. Please try again.'
      });
      setModalOpen(true);
      return;
    }

    // Check if user has company_admin role
    if (user.role !== 'company_admin') {
      setModalConfig({
        type: 'error',
        title: 'Access Denied',
        message: 'This account does not have company access. Please use the consumer login.'
      });
      setModalOpen(true);
      return;
    }

    // Get company details
    const company = companies.find(c => c.id === user.companyId);
    
    console.log('Found company:', company);
    
    if (!company) {
      setModalConfig({
        type: 'error',
        title: 'Login Failed',
        message: 'Company record not found. Please contact support.'
      });
      setModalOpen(true);
      return;
    }
    
    // Store current user session with company details
    localStorage.setItem('currentUser', JSON.stringify({
      id: user.id,
      email: user.email,
      firstName: user.firstName || 'Admin',
      lastName: user.lastName || company.name,
      role: user.role,
      companyId: user.companyId,
      companyName: company.name
    }));
    
    console.log('Stored currentUser:', JSON.parse(localStorage.getItem('currentUser')));
    
    // Show success modal before redirect
    setModalConfig({
      type: 'success',
      title: 'Login Successful!',
      message: `Welcome back, ${company.name}! Redirecting to dashboard...`
    });
    setModalOpen(true);
    
    // Redirect after a brief delay
    setTimeout(() => {
      setModalOpen(false);
      navigate('/company/dashboard');
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-md mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          className="mb-4"
        >
          <Icon name="ArrowLeft" size={20} library="fi" className="text-gray-500" />
        </button>

        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Icon name="Building" size={32} library="fi" className="text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Company Login</h1>
          <p className="text-gray-500 mt-2">Access your brand intelligence dashboard</p>
        </div>

        {/* Login Form */}
        <Card className="mb-6">
          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email */}
            <div>
              <label className="text-sm text-gray-500 mb-1 block">Business Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                onBlur={() => handleBlur('email')}
                className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                  getFieldError('email') 
                    ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                    : touched.email && formData.email
                    ? 'border-primary bg-primary/5 focus:ring-primary/20'
                    : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                }`}
                placeholder="contact@yourcompany.com"
              />
              {getFieldError('email') && (
                <p className="text-danger text-xs mt-1">{getFieldError('email')}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="text-sm text-gray-500 mb-1 block">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  onBlur={() => handleBlur('password')}
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors pr-12 ${
                    getFieldError('password') 
                      ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                      : touched.password && formData.password
                      ? 'border-primary bg-primary/5 focus:ring-primary/20'
                      : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                  }`}
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                >
                  <Icon 
                    name={showPassword ? 'Eye' : 'EyeOff'} 
                    size={20} 
                    library="fi" 
                    className="text-gray-400 hover:text-primary transition-colors" 
                  />
                </button>
              </div>
              {getFieldError('password') && (
                <p className="text-danger text-xs mt-1">{getFieldError('password')}</p>
              )}
            </div>

            {/* Forgot Password */}
            <div className="text-right">
              <button 
                type="button"
                className="text-sm text-primary hover:underline"
                onClick={() => {
                  setModalConfig({
                    type: 'info',
                    title: 'Password Reset',
                    message: 'Please contact your system administrator to reset your password.'
                  });
                  setModalOpen(true);
                }}
              >
                Forgot password?
              </button>
            </div>

            {/* Login Button */}
            <Button
              type="submit"
              variant="primary"
              fullWidth
              disabled={!isFormValid()}
            >
              Login to Dashboard
            </Button>
          </form>
        </Card>

        {/* Sign Up Link */}
        <p className="text-center text-gray-500">
          New to SabiLens?{' '}
          <button
            onClick={() => navigate('/company/signup')}
            className="text-primary font-medium hover:underline"
          >
            Register Your Company
          </button>
        </p>
      </div>

      {/* Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        type={modalConfig.type}
        title={modalConfig.title}
        message={modalConfig.message}
      />
    </div>
  );
};

export default CompanyLogin;