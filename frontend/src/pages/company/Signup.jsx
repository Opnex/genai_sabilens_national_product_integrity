import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';

// Nigeria states data
const NIGERIA_STATES = [
  'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
  'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo',
  'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa',
  'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
];

// City data mapping
const STATE_CITIES = {
  'Lagos': ['Ikeja', 'Victoria Island', 'Lekki', 'Surulere', 'Ajah', 'Yaba', 'Ikoyi', 'Badagry', 'Epe', 'Ikorodu'],
  'Abia': ['Umuahia', 'Aba', 'Ohafia', 'Arochukwu', 'Bende', 'Isuikwuato'],
  'FCT': ['Abuja', 'Gwagwalada', 'Kuje', 'Bwari', 'Kwali'],
  'Rivers': ['Port Harcourt', 'Obio-Akpor', 'Eleme', 'Okrika', 'Oyigbo', 'Bonny'],
  'Kano': ['Kano', 'Fagge', 'Dala', 'Gwale', 'Tarauni', 'Nassarawa'],
  'Oyo': ['Ibadan', 'Ogbomosho', 'Oyo', 'Iseyin', 'Saki', 'Kisi'],
  'Kaduna': ['Kaduna', 'Zaria', 'Kafanchan', 'Saminaka', 'Birnin Gwari'],
  'Abuja': ['Garki', 'Wuse', 'Maitama', 'Asokoro', 'Jabi', 'Gwarinpa', 'Kubwa', 'Bwari'],
  'Anambra': ['Awka', 'Onitsha', 'Nnewi', 'Ekwulobia', 'Agulu'],
  'Bauchi': ['Bauchi', 'Azare', 'Misau', 'Jama\'are'],
  'Bayelsa': ['Yenagoa', 'Brass', 'Ogbia', 'Sagbama'],
  'Benue': ['Makurdi', 'Gboko', 'Otukpo', 'Katsina-Ala'],
  'Borno': ['Maiduguri', 'Bama', 'Biu', 'Monguno'],
  'Cross River': ['Calabar', 'Ikom', 'Obudu', 'Ogoja'],
  'Delta': ['Asaba', 'Warri', 'Ughelli', 'Sapele'],
  'Ebonyi': ['Abakaliki', 'Afikpo', 'Onueke', 'Ishieke'],
  'Edo': ['Benin City', 'Auchi', 'Ekpoma', 'Uromi'],
  'Ekiti': ['Ado Ekiti', 'Ikere', 'Omuo', 'Efon Alaaye'],
  'Enugu': ['Enugu', 'Nsukka', 'Agbani', 'Oji River'],
  'Gombe': ['Gombe', 'Kaltungo', 'Billiri', 'Dukku'],
  'Imo': ['Owerri', 'Orlu', 'Okigwe', 'Mbaise'],
  'Jigawa': ['Dutse', 'Hadejia', 'Gumel', 'Birnin Kudu'],
  'Katsina': ['Katsina', 'Funtua', 'Daura', 'Malumfashi'],
  'Kebbi': ['Birnin Kebbi', 'Argungu', 'Yauri', 'Zuru'],
  'Kogi': ['Lokoja', 'Okene', 'Idah', 'Kabba'],
  'Kwara': ['Ilorin', 'Offa', 'Omu Aran', 'Patigi'],
  'Nasarawa': ['Lafia', 'Keffi', 'Akwanga', 'Nasarawa'],
  'Niger': ['Minna', 'Bida', 'Kontagora', 'Suleja'],
  'Ogun': ['Abeokuta', 'Ijebu Ode', 'Sagamu', 'Ota'],
  'Osun': ['Osogbo', 'Ile-Ife', 'Ilesa', 'Ede'],
  'Plateau': ['Jos', 'Bukuru', 'Pankshin', 'Shendam'],
  'Sokoto': ['Sokoto', 'Gwadabawa', 'Wurno', 'Rabah'],
  'Taraba': ['Jalingo', 'Wukari', 'Bali', 'Takum'],
  'Yobe': ['Damaturu', 'Potiskum', 'Gashua', 'Nguru'],
  'Zamfara': ['Gusau', 'Kaura Namoda', 'Talata Mafara', 'Anka']
};

const CompanySignup = () => {
  const navigate = useNavigate();
  const [modalOpen, setModalOpen] = useState(false);
  const [modalConfig, setModalConfig] = useState({
    type: 'success',
    title: '',
    message: ''
  });

  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);

  const [formData, setFormData] = useState({
    companyName: '',
    registrationNumber: '',
    email: '',
    phone: '',
    address: '',
    state: '',
    city: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [touched, setTouched] = useState({});
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [citySuggestions, setCitySuggestions] = useState([]);
  const [showCitySuggestions, setShowCitySuggestions] = useState(false);

  // Password requirements
  const passwordRequirements = [
    { label: 'At least 8 characters', test: (pwd) => pwd.length >= 8 },
    { label: 'At least one uppercase letter', test: (pwd) => /[A-Z]/.test(pwd) },
    { label: 'At least one lowercase letter', test: (pwd) => /[a-z]/.test(pwd) },
    { label: 'At least one number', test: (pwd) => /\d/.test(pwd) },
    { label: 'At least one special character', test: (pwd) => /[!@#$%^&*]/.test(pwd) },
  ];

  // Update city suggestions when state changes or user types
  useEffect(() => {
    if (formData.state && formData.city) {
      const stateCities = STATE_CITIES[formData.state] || [];
      const filtered = stateCities.filter(city =>
        city.toLowerCase().includes(formData.city.toLowerCase())
      );
      setCitySuggestions(filtered);
    } else {
      setCitySuggestions([]);
    }
  }, [formData.state, formData.city]);

  const validateField = (name, value) => {
    switch (name) {
      case 'companyName':
        return value.trim() ? '' : 'Company name is required';
      case 'registrationNumber':
        return value.trim() ? '' : 'CAC registration number is required';
      case 'email':
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? '' : 'Valid email is required';
      case 'phone':
        return /^[0-9]{10}$/.test(value) ? '' : 'Valid 10-digit phone number required';
      case 'address':
        return value.trim() ? '' : 'Address is required';
      case 'state':
        return value ? '' : 'Please select a state';
      case 'city':
        return value.trim() ? '' : 'City is required';
      case 'password':
        if (!value) return 'Password is required';
        if (value.length < 8) return 'Password must be at least 8 characters';
        if (!/[A-Z]/.test(value)) return 'Include at least one uppercase letter';
        if (!/[a-z]/.test(value)) return 'Include at least one lowercase letter';
        if (!/\d/.test(value)) return 'Include at least one number';
        if (!/[!@#$%^&*]/.test(value)) return 'Include at least one special character';
        return '';
      case 'confirmPassword':
        return value === formData.password ? '' : 'Passwords do not match';
      default:
        return '';
    }
  };

  const getFieldError = (name) => {
    if (!touched[name]) return '';
    return validateField(name, formData[name]);
  };

  const isFormValid = () => {
    const requiredFields = ['companyName', 'registrationNumber', 'email', 'phone', 'address', 'state', 'city', 'password', 'confirmPassword'];
    const allFieldsFilled = requiredFields.every(field => formData[field]?.toString().trim());
    const noErrors = requiredFields.every(field => !validateField(field, formData[field]));
    return allFieldsFilled && noErrors && formData.agreeTerms;
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (name === 'phone') {
      const numbersOnly = value.replace(/\D/g, '');
      setFormData(prev => ({ ...prev, [name]: numbersOnly }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      }));
    }
  };

  const handleBlur = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    if (name === 'city') {
      setTimeout(() => setShowCitySuggestions(false), 200);
    }
  };

  const handleCitySelect = (city) => {
    setFormData(prev => ({ ...prev, city }));
    setShowCitySuggestions(false);
    setTouched(prev => ({ ...prev, city: true }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const requiredFields = ['companyName', 'registrationNumber', 'email', 'phone', 'address', 'state', 'city', 'password', 'confirmPassword'];
    const touchedFields = requiredFields.reduce((acc, field) => ({ ...acc, [field]: true }), {});
    setTouched(touchedFields);

    if (!isFormValid()) return;

    // Get existing companies and users
    const companies = JSON.parse(localStorage.getItem('companies') || '[]');
    const users = JSON.parse(localStorage.getItem('users') || '[]');

    // Check if email exists
    const existingUser = users.find(u => u.email === formData.email);
    if (existingUser) {
      setModalConfig({
        type: 'error',
        title: 'Email Exists',
        message: 'This email is already registered. Please use a different email or login.'
      });
      setModalOpen(true);
      return;
    }

    // Create company record
    const companyId = `comp_${Date.now()}`;
    const newCompany = {
      id: companyId,
      name: formData.companyName,
      registrationNumber: formData.registrationNumber,
      email: formData.email,
      phone: `+234${formData.phone}`,
      address: formData.address,
      city: formData.city,
      state: formData.state,
      status: 'active',
      createdAt: new Date().toISOString()
    };

    companies.push(newCompany);

    // Create admin user for company
    const newUser = {
      id: `user_${Date.now()}`,
      email: formData.email,
      password: formData.password,
      firstName: 'Admin',
      lastName: formData.companyName,
      role: 'company_admin',
      companyId: companyId,
      status: 'active',
      createdAt: new Date().toISOString()
    };

    users.push(newUser);

    localStorage.setItem('companies', JSON.stringify(companies));
    localStorage.setItem('users', JSON.stringify(users));

    setModalConfig({
      type: 'success',
      title: 'Registration Successful!',
      message: `Welcome ${formData.companyName}! Your company account has been created successfully. Please login to continue.`
    });
    setModalOpen(true);
  };

  const handleModalClose = () => {
    setModalOpen(false);
    if (modalConfig.type === 'success') {
      navigate('/company/login');
    }
  };

  // Custom Checkbox Component
  const CustomCheckbox = ({ name, checked, onChange, label }) => (
    <label className="flex items-start gap-3 cursor-pointer group">
      <div className="relative flex items-center justify-center">
        <input
          type="checkbox"
          name={name}
          checked={checked}
          onChange={onChange}
          className="sr-only"
        />
        <div className={`w-5 h-5 border-2 rounded transition-all duration-200 flex items-center justify-center
          ${checked
            ? 'border-primary bg-primary'
            : 'border-gray-300 bg-white group-hover:border-primary'
          }`}
        >
          {checked && (
            <Icon name="Check" size={14} library="fi" className="text-white" />
          )}
        </div>
      </div>
      <span className="text-sm text-gray-600 flex-1">{label}</span>
    </label>
  );

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-2xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-8">
          <button
            onClick={() => navigate('/')}
            className="absolute left-6 top-8"
          >
            <Icon name="ArrowLeft" size={20} library="fi" className="text-gray-500" />
          </button>

          <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Icon name="Building" size={32} library="fi" className="text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Register Your Company</h1>
          <p className="text-gray-500 mt-2">Join SabiLens to protect your brand from counterfeits</p>
        </div>

        {/* Signup Form */}
        <Card>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Company Name */}
            <div>
              <label className="text-sm text-gray-500 mb-1 block">Company Name *</label>
              <input
                type="text"
                name="companyName"
                value={formData.companyName}
                onChange={handleChange}
                onBlur={() => handleBlur('companyName')}
                className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${getFieldError('companyName')
                  ? 'border-danger bg-danger/5 focus:ring-danger/20'
                  : touched.companyName && formData.companyName
                    ? 'border-primary bg-primary/5 focus:ring-primary/20'
                    : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                  }`}
                placeholder="e.g., Lagos Pharma Ltd"
              />
              {getFieldError('companyName') && (
                <p className="text-danger text-xs mt-1">{getFieldError('companyName')}</p>
              )}
            </div>

            {/* CAC Registration Number */}
            <div>
              <label className="text-sm text-gray-500 mb-1 block">CAC Registration Number *</label>
              <input
                type="text"
                name="registrationNumber"
                value={formData.registrationNumber}
                onChange={handleChange}
                onBlur={() => handleBlur('registrationNumber')}
                className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${getFieldError('registrationNumber')
                  ? 'border-danger bg-danger/5 focus:ring-danger/20'
                  : touched.registrationNumber && formData.registrationNumber
                    ? 'border-primary bg-primary/5 focus:ring-primary/20'
                    : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                  }`}
                placeholder="RC 1234567"
              />
              {getFieldError('registrationNumber') && (
                <p className="text-danger text-xs mt-1">{getFieldError('registrationNumber')}</p>
              )}
            </div>

            {/* Email */}
            <div>
              <label className="text-sm text-gray-500 mb-1 block">Business Email *</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                onBlur={() => handleBlur('email')}
                className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${getFieldError('email')
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

            {/* Phone */}
            <div>
              <label className="text-sm text-gray-500 mb-1 block">Phone Number *</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-medium">+234</span>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  onBlur={() => handleBlur('phone')}
                  placeholder="8012345678"
                  maxLength="10"
                  className={`w-full pl-16 pr-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${getFieldError('phone')
                    ? 'border-danger bg-danger/5 focus:ring-danger/20'
                    : touched.phone && formData.phone && !getFieldError('phone')
                      ? 'border-primary bg-primary/5 focus:ring-primary/20'
                      : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                />
              </div>
              {getFieldError('phone') && (
                <p className="text-danger text-xs mt-1">{getFieldError('phone')}</p>
              )}
              {!getFieldError('phone') && touched.phone && formData.phone && (
                <p className="text-primary text-xs mt-1 flex items-center gap-1">
                  <Icon name="Check" size={12} library="fi" className="text-primary" />
                  Valid Nigerian number: +234{formData.phone}
                </p>
              )}
            </div>

            {/* Address */}
            <div>
              <label className="text-sm text-gray-500 mb-1 block">Business Address *</label>
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleChange}
                onBlur={() => handleBlur('address')}
                className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${getFieldError('address')
                  ? 'border-danger bg-danger/5 focus:ring-danger/20'
                  : touched.address && formData.address
                    ? 'border-primary bg-primary/5 focus:ring-primary/20'
                    : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                  }`}
                placeholder="Street address"
              />
              {getFieldError('address') && (
                <p className="text-danger text-xs mt-1">{getFieldError('address')}</p>
              )}
            </div>

            {/* State and City Row */}
            <div className="grid grid-cols-2 gap-4">
              {/* State Selection */}
              <div>
                <label className="text-sm text-gray-500 mb-1 block">State *</label>
                <select
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  onBlur={() => handleBlur('state')}
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${getFieldError('state')
                    ? 'border-danger bg-danger/5 focus:ring-danger/20'
                    : touched.state && formData.state
                      ? 'border-primary bg-primary/5 focus:ring-primary/20'
                      : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                >
                  <option value="">Select State</option>
                  {NIGERIA_STATES.map(state => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
                {getFieldError('state') && (
                  <p className="text-danger text-xs mt-1">{getFieldError('state')}</p>
                )}
              </div>

              {/* City Input with Suggestions */}
              <div className="relative">
                <label className="text-sm text-gray-500 mb-1 block">City *</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  onFocus={() => setShowCitySuggestions(true)}
                  onBlur={() => handleBlur('city')}
                  disabled={!formData.state}
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${getFieldError('city')
                    ? 'border-danger bg-danger/5 focus:ring-danger/20'
                    : touched.city && formData.city
                      ? 'border-primary bg-primary/5 focus:ring-primary/20'
                      : !formData.state
                        ? 'border-gray-200 bg-gray-100 cursor-not-allowed'
                        : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                  placeholder={!formData.state ? 'Select state first' : 'Enter city'}
                />

                {/* City Suggestions Dropdown */}
                {showCitySuggestions && citySuggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-48 overflow-y-auto">
                    {citySuggestions.map((city) => (
                      <button
                        key={city}
                        type="button"
                        onClick={() => handleCitySelect(city)}
                        className="w-full text-left px-4 py-2 hover:bg-primary/5 text-gray-700 hover:text-primary transition-colors"
                      >
                        {city}
                      </button>
                    ))}
                  </div>
                )}

                {getFieldError('city') && (
                  <p className="text-danger text-xs mt-1">{getFieldError('city')}</p>
                )}
                {!getFieldError('city') && touched.city && formData.city && (
                  <p className="text-primary text-xs mt-1 flex items-center gap-1">
                    <Icon name="Check" size={12} library="fi" className="text-primary" />
                    City entered
                  </p>
                )}
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="text-sm text-gray-500 mb-1 block">Password *</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  onBlur={() => handleBlur('password')}
                  onFocus={() => setPasswordFocused(true)}
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors pr-12 ${getFieldError('password')
                    ? 'border-danger bg-danger/5 focus:ring-danger/20'
                    : touched.password && formData.password && !getFieldError('password')
                      ? 'border-primary bg-primary/5 focus:ring-primary/20'
                      : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                  placeholder="Create a password"
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

              {/* Password Requirements Guide */}
              {(passwordFocused || touched.password) && (
                <Card className="mt-3 p-4 bg-gray-50">
                  <p className="text-xs font-medium text-gray-600 mb-2">Password must contain:</p>
                  <div className="space-y-2">
                    {passwordRequirements.map((req, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div className={`w-4 h-4 rounded-full flex items-center justify-center ${req.test(formData.password) ? 'bg-primary/20' : 'bg-gray-200'
                          }`}>
                          {req.test(formData.password) && (
                            <Icon name="Check" size={12} library="fi" className="text-primary" />
                          )}
                        </div>
                        <span className={`text-xs ${req.test(formData.password) ? 'text-primary font-medium' : 'text-gray-500'
                          }`}>
                          {req.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {getFieldError('password') && (
                <p className="text-danger text-xs mt-1">{getFieldError('password')}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="text-sm text-gray-500 mb-1 block">Confirm Password *</label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  onBlur={() => handleBlur('confirmPassword')}
                  className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors pr-12 ${getFieldError('confirmPassword')
                    ? 'border-danger bg-danger/5 focus:ring-danger/20'
                    : touched.confirmPassword && formData.confirmPassword && !getFieldError('confirmPassword')
                      ? 'border-primary bg-primary/5 focus:ring-primary/20'
                      : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                    }`}
                  placeholder="Confirm your password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                >
                  <Icon
                    name={showConfirmPassword ? 'Eye' : 'EyeOff'}
                    size={20}
                    library="fi"
                    className="text-gray-400 hover:text-primary transition-colors"
                  />
                </button>
              </div>
              {getFieldError('confirmPassword') && (
                <p className="text-danger text-xs mt-1">{getFieldError('confirmPassword')}</p>
              )}
            </div>

            {/* Custom Checkbox */}
            <CustomCheckbox
              name="agreeTerms"
              checked={formData.agreeTerms}
              onChange={handleChange}
              label={
                <span>
                  I confirm that the information provided is accurate and I agree to the{' '}
                  <button type="button" onClick={() => setShowTermsModal(true)} className="text-primary hover:underline font-medium">Terms of Service</button>
                  {' '}and{' '}
                  <button type="button" onClick={() => setShowPrivacyModal(true)} className="text-primary hover:underline font-medium">Privacy Policy</button>
                </span>
              }
            />

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              fullWidth
              disabled={!isFormValid()}
            >
              Register Company
            </Button>
          </form>
        </Card>

        {/* Login Link */}
        <p className="text-center text-gray-500 mt-6">
          Already registered?{' '}
          <button
            onClick={() => navigate('/company/login')}
            className="text-primary font-medium hover:underline"
          >
            Company Login
          </button>
        </p>
      </div>

      {/* Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={handleModalClose}
        type={modalConfig.type}
        title={modalConfig.title}
        message={modalConfig.message}
      />

      {/* Terms of Service Modal */}
      <Modal
        isOpen={showTermsModal}
        onClose={() => setShowTermsModal(false)}
        type="info"
        title="Brand Protection Terms"
      >
        <div className="space-y-6 font-sans text-accent overflow-y-auto max-h-[60vh] pr-2 custom-scrollbar">
          <section>
            <h3 className="font-syne font-bold text-lg mb-2">1. Authorized Representation</h3>
            <p className="text-muted leading-relaxed">
              By registering as a Brand on SabiLens, you represent and warrant that you are an authorized representative of the company and have the legal authority to act on its behalf regarding product authentication.
            </p>
          </section>

          <section>
            <h3 className="font-syne font-bold text-lg mb-2">2. Product Registry Integrity</h3>
            <p className="text-muted leading-relaxed">
              You agree to provide accurate and up-to-date product information for the SabiLens registry. SabiLens uses this data to calibrate its AI for authentication. Providing false data may compromise the safety of consumers and is strictly prohibited.
            </p>
          </section>

          <section>
            <h3 className="font-syne font-bold text-lg mb-2">3. Counterfeit Evidence</h3>
            <p className="text-muted leading-relaxed">
              SabiLens provides an Evidence Vault containing data on flagged counterfeits. This data is for your internal brand protection and legal enforcement use. Any submission of this evidence to NAFDAC must follow established regulatory protocols.
            </p>
          </section>

          <div className="pt-4 text-center">
            <Button variant="primary" size="lg" fullWidth onClick={() => setShowTermsModal(false)}>
              I Understand
            </Button>
          </div>
        </div>
      </Modal>

      {/* Privacy Policy Modal */}
      <Modal
        isOpen={showPrivacyModal}
        onClose={() => setShowPrivacyModal(false)}
        type="info"
        title="Corporate Privacy Policy"
      >
        <div className="space-y-6 font-sans text-accent overflow-y-auto max-h-[60vh] pr-2 custom-scrollbar">
          <section>
            <h3 className="font-syne font-bold text-lg mb-2">Business Data Security</h3>
            <p className="text-muted leading-relaxed">
              We understand the sensitivity of your product specifications and manufacturing data. SabiLens uses bank-grade encryption to secure all brand-related data. Your proprietary information is used solely to enhance the accuracy of our authentication AI.
            </p>
          </section>

          <section>
            <h3 className="font-syne font-bold text-lg mb-2">Data Sharing</h3>
            <p className="text-muted leading-relaxed">
              Counterfeit heatmaps and incident reports are shared with NAFDAC to assist in national enforcement. Personal information of company officers is kept strictly confidential and never shared with third parties without explicit consent.
            </p>
          </section>

          <div className="pt-4 text-center">
            <Button variant="primary" size="lg" fullWidth onClick={() => setShowPrivacyModal(false)}>
              Accept Policy
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default CompanySignup;