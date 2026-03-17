import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';

const NAFDACLogin = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [touched, setTouched] = useState({});

  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);

  // Pre-create NAFDAC admin if not exists
  React.useEffect(() => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const nafdacExists = users.some(u => u.role === 'nafdac_admin');

    if (!nafdacExists) {
      users.push({
        id: 'nafdac_1',
        email: 'admin@nafdac.gov.ng',
        password: 'Nafdac@2024',
        firstName: 'NAFDAC',
        lastName: 'Admin',
        role: 'nafdac_admin',
        status: 'active',
        createdAt: new Date().toISOString()
      });
      localStorage.setItem('users', JSON.stringify(users));
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleBlur = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
  };

  const validateField = (name, value) => {
    switch (name) {
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

    if (!isFormValid()) return;

    // Get users from localStorage
    const users = JSON.parse(localStorage.getItem('users') || '[]');

    // Find NAFDAC user
    const user = users.find(u =>
      u.email === formData.email &&
      u.password === formData.password &&
      (u.role === 'nafdac_admin' || u.role === 'nafdac_officer')
    );

    if (user) {
      // Store current user session
      localStorage.setItem('currentUser', JSON.stringify({
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role
      }));

      // Redirect to NAFDAC dashboard
      navigate('/nafdac/dashboard');
    } else {
      setError('Invalid credentials. Use admin@nafdac.gov.ng / Nafdac@2024');
    }
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
            <Icon name="Shield" size={32} library="fi" className="text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">NAFDAC Portal</h1>
          <p className="text-gray-500 mt-2">National Regulatory Dashboard</p>
        </div>

        {/* Login Form */}
        <Card className="mb-6">
          <form onSubmit={handleLogin} className="space-y-4">
            {/* Error Message */}
            {error && (
              <div className="bg-danger/10 text-danger p-3 rounded-xl text-sm flex items-center gap-2">
                <Icon name="AlertCircle" size={16} library="fi" />
                {error}
              </div>
            )}

            {/* Email */}
            <div>
              <label className="text-sm text-gray-500 mb-1 block">Official Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                onBlur={() => handleBlur('email')}
                className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 ${getFieldError('email') ? 'border-danger bg-danger/5' : 'border-gray-200'
                  }`}
                placeholder="officer@nafdac.gov.ng"
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
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 pr-12 ${getFieldError('password') ? 'border-danger bg-danger/5' : 'border-gray-200'
                    }`}
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                >
                  <Icon name={showPassword ? 'EyeOff' : 'Eye'} size={20} library="fi" />
                </button>
              </div>
              {getFieldError('password') && (
                <p className="text-danger text-xs mt-1">{getFieldError('password')}</p>
              )}
            </div>

            {/* Login Button */}
            <Button
              type="submit"
              variant="primary"
              fullWidth
              disabled={!isFormValid()}
            >
              Access NAFDAC Dashboard
            </Button>

            <p className="text-center text-sm text-gray-500 mt-4">
              Authorized officer without access?{' '}
              <Link to="/nafdac/signup" className="text-primary font-bold hover:underline">Request access here</Link>
            </p>
          </form>

          {/* Regulatory Links */}
          <div className="mt-8 pt-6 border-t border-gray-100 flex justify-center gap-4">
            <button
              type="button"
              onClick={() => setShowTermsModal(true)}
              className="text-xs text-gray-400 hover:text-primary transition-colors font-medium"
            >
              Regulatory Terms
            </button>
            <span className="text-gray-200">|</span>
            <button
              type="button"
              onClick={() => setShowPrivacyModal(true)}
              className="text-xs text-gray-400 hover:text-primary transition-colors font-medium"
            >
              Data Privacy
            </button>
          </div>
        </Card>

        {/* Demo Credentials */}
        <Card className="bg-primary/5 border border-primary/20">
          <p className="text-xs text-gray-600 font-medium mb-2">Demo Credentials:</p>
          <p className="text-xs text-gray-500">Email: admin@nafdac.gov.ng</p>
          <p className="text-xs text-gray-500">Password: Nafdac@2024</p>
        </Card>
      </div>

      {/* Terms of Service Modal */}
      <Modal
        isOpen={showTermsModal}
        onClose={() => setShowTermsModal(false)}
        type="info"
        title="Regulatory Access Terms"
      >
        <div className="space-y-6 font-sans text-accent overflow-y-auto max-h-[60vh] pr-2 custom-scrollbar">
          <section>
            <h3 className="font-syne font-bold text-lg mb-2">1. Official Use Only</h3>
            <p className="text-muted leading-relaxed">
              Access to the NAFDAC Portal via SabiLens is strictly reserved for authorized officers and personnel. Unauthorized access attempts are monitored and will be reported to the appropriate legal authorities within the Nigerian Federal Government.
            </p>
          </section>

          <section>
            <h3 className="font-syne font-bold text-lg mb-2">2. Data Integrity & Case Management</h3>
            <p className="text-muted leading-relaxed">
              Information submitted or reviewed within this portal must be handled with the highest level of integrity. Officers are responsible for all actions taken under their unique credentials.
            </p>
          </section>

          <section>
            <h3 className="font-syne font-bold text-lg mb-2">3. Transparency & Sovereignty</h3>
            <p className="text-muted leading-relaxed">
              SabiLens acts as a technology provider. All regulatory decisions and enforcement actions derived from this data remain the absolute sovereign right of NAFDAC in accordance with the NAFDAC Act.
            </p>
          </section>

          <div className="pt-4 text-center">
            <Button variant="primary" size="lg" fullWidth onClick={() => setShowTermsModal(false)}>
              Acknowledge
            </Button>
          </div>
        </div>
      </Modal>

      {/* Privacy Policy Modal */}
      <Modal
        isOpen={showPrivacyModal}
        onClose={() => setShowPrivacyModal(false)}
        type="info"
        title="Regulatory Data Privacy"
      >
        <div className="space-y-6 font-sans text-accent overflow-y-auto max-h-[60vh] pr-2 custom-scrollbar">
          <section>
            <h3 className="font-syne font-bold text-lg mb-2">Protocol & Encryption</h3>
            <p className="text-muted leading-relaxed">
              All regulatory communications and officer activities are protected using end-to-end encryption. SabiLens adheres to the Nigeria Data Protection Regulation (NDPR) regarding the handling of sensitive consumer evidence and brand registries.
            </p>
          </section>

          <section>
            <h3 className="font-syne font-bold text-lg mb-2">Audit Logs</h3>
            <p className="text-muted leading-relaxed">
              To ensure the integrity of the national verification system, all access to product registries and evidence vaults by NAFDAC personnel is logged and subject to periodic audit by system administrators.
            </p>
          </section>

          <div className="pt-4 text-center">
            <Button variant="primary" size="lg" fullWidth onClick={() => setShowPrivacyModal(false)}>
              Confirm Policy
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default NAFDACLogin;