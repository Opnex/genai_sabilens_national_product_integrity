import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, X, User, ShieldCheck, MapPin, Mic } from 'lucide-react';
import Icon from '../../components/common/Icon';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import Modal from '../../components/common/Modal';
import Toast from '../../components/ui/Toast';
import SabiLensLogo from '../../assets/SabiLens_Logo.png';

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

const BrandSidebar = () => (
  <div className="hidden lg:flex w-[40%] bg-gradient-to-br from-[#0A0E1A] to-[#0d1a12] p-12 flex-col relative overflow-hidden">
    <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4=')] opacity-[0.02]" />
    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full aspect-square bg-primary/20 rounded-full blur-[100px] pointer-events-none" />
    <div className="relative z-10 flex-1 flex flex-col">
      <Link to="/" className="flex items-center gap-2 mb-20 group inline-flex max-w-max">
        <img src={SabiLensLogo} alt="SabiLens" className="h-8 w-auto" />
        <span className="font-syne font-bold text-2xl tracking-tight text-white">
          Sabi<span className="text-primary">Lens</span>
        </span>
      </Link>
      <div className="mt-0">
        <h2 className="text-4xl font-syne font-bold text-white mb-4 leading-tight">Join as Consumer</h2>
        <p className="text-white/60 font-sans text-lg mb-12">Create your free account and start verifying products instantly.</p>
        <ul className="space-y-6 mb-16 font-sans text-white/80">
          <li className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <span>Free AI-powered product scanning</span>
          </li>
          <li className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
              <Mic className="w-5 h-5" />
            </div>
            <span>Voice results in your language</span>
          </li>
          <li className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
              <MapPin className="w-5 h-5" />
            </div>
            <span>Report fakes directly to NAFDAC</span>
          </li>
        </ul>
        <div className="bg-accent-2/50 backdrop-blur-sm border border-white/10 rounded-2xl p-6 border-l-4 border-l-primary">
          <p className="font-sans text-white/90 italic mb-4 leading-relaxed">
            "Over 50,000 Nigerians are already using SabiLens to stay safe."
          </p>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center font-syne font-bold text-primary text-sm">✓</div>
            <span className="font-syne font-bold text-white text-sm">Trusted by NAFDAC</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const ConsumerSignup = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    phone: '',
    state: '',
    city: '',
    password: '',
    confirmPassword: '',
    agreeLocation: false,
    agreeTerms: false
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [toast, setToast] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [citySuggestions, setCitySuggestions] = useState([]);
  const [showCitySuggestions, setShowCitySuggestions] = useState(false);
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [showGoogleModal, setShowGoogleModal] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalConfig, setModalConfig] = useState({
    type: 'success',
    title: '',
    message: ''
  });

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
      case 'firstName':
        return value.trim() ? '' : 'First name is required';
      case 'lastName':
        return value.trim() ? '' : 'Last name is required';
      case 'phone':
        return /^[0-9]{10}$/.test(value) ? '' : 'Valid 10-digit phone number required';
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
    const requiredFields = ['firstName', 'lastName', 'phone', 'state', 'city', 'password', 'confirmPassword'];
    const allFieldsFilled = requiredFields.every(field => {
      const value = formData[field];
      return value && value.toString().trim();
    });
    const noErrors = requiredFields.every(field => !validateField(field, formData[field]));
    return allFieldsFilled && noErrors && formData.agreeLocation && formData.agreeTerms;
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
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
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

  const handleSubmit = async (e) => {
    e.preventDefault();

    const requiredFields = ['firstName', 'lastName', 'phone', 'state', 'city', 'password', 'confirmPassword'];
    const touchedFields = requiredFields.reduce((acc, field) => ({ ...acc, [field]: true }), {});
    setTouched(touchedFields);

    if (!isFormValid()) return;

    setIsSubmitting(true);

    try {
      const users = JSON.parse(localStorage.getItem('users') || '[]');

      // Check if phone exists
      if (users.some(u => u.phone === formData.phone)) {
        setErrors({ phone: 'This phone number is already registered' });
        setIsSubmitting(false);
        return;
      }

      const newUser = {
        id: `user_${Date.now()}`,
        firstName: formData.firstName,
        lastName: formData.lastName,
        phone: formData.phone,
        state: formData.state,
        city: formData.city,
        password: formData.password,
        role: 'consumer',
        createdAt: new Date().toISOString()
      };

      users.push(newUser);
      localStorage.setItem('users', JSON.stringify(users));
      localStorage.setItem('currentUser', JSON.stringify(newUser));
      localStorage.setItem('hasSeenOnboarding', 'true');

      setModalConfig({
        type: 'success',
        title: 'Welcome to SabiLens!',
        message: `Your account has been created successfully. You'll be redirected to the home page.`
      });
      setModalOpen(true);

      setTimeout(() => {
        navigate('/home');
      }, 2000);

    } catch (error) {
      setToast({
        type: 'error',
        message: 'Something went wrong. Please try again.'
      });
      setIsSubmitting(false);
    }
  };

  const handleModalClose = () => {
    setModalOpen(false);
    if (modalConfig.type === 'success') {
      navigate('/home');
    }
  };

  // Custom Checkbox Component — fixed alignment and spacing on mobile
  const CustomCheckbox = ({ name, checked, onChange, label }) => (
    <label className="flex items-start gap-2 cursor-pointer">
      <div className="relative flex-shrink-0" style={{ marginTop: '2px' }}>
        <input
          type="checkbox"
          name={name}
          checked={checked}
          onChange={onChange}
          className="sr-only"
        />
        <div
          className={`w-4 h-4 border-2 rounded transition-all duration-200 flex items-center justify-center
            ${checked
              ? 'border-primary bg-primary'
              : 'border-gray-300 bg-white hover:border-primary'
            }`}
        >
          {checked && (
            <Icon name="Check" size={10} library="fi" className="text-white" />
          )}
        </div>
      </div>
      <span className="text-sm text-gray-600 leading-snug">{label}</span>
    </label>
  );

  // Custom Modal Component for Policy Pages
  const PolicyModal = ({ isOpen, onClose, title, children }) => {
    if (!isOpen) return null;

    return (
      <div 
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      >
        <div 
          className="relative w-full max-w-2xl max-h-[80vh] bg-white rounded-2xl shadow-2xl overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-border px-6 py-4 flex items-center justify-between">
            <h2 className="text-xl font-heading font-bold text-accent">{title}</h2>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
            >
              <X size={18} className="text-accent" />
            </button>
          </div>
          
          {/* Scrollable Content */}
          <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(80vh - 80px)' }}>
            {children}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background flex">
      {toast && <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />}
      
      {/* Left Sidebar (Desktop only) */}
      <BrandSidebar />

      {/* Right Content Area */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        {/* Mobile Header */}
        <div className="lg:hidden p-6 flex justify-between items-center border-b border-border bg-white sticky top-0 z-20">
          <button
            onClick={() => navigate('/role-select')}
            className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-50 border border-gray-100 hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft size={18} className="text-accent" />
          </button>
          <Link to="/" className="flex items-center gap-2">
            <img src={SabiLensLogo} alt="SabiLens" className="h-6 w-auto" />
            <span className="font-heading font-bold text-xl text-accent">
              Sabi<span className="text-primary">Lens</span>
            </span>
          </Link>
          <Link to="/login" className="text-sm font-medium text-primary bg-primary-light px-4 py-2 rounded-lg">
            Log In
          </Link>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
          <div className="w-full max-w-2xl animate-fade-up">
            {/* Header Area - Desktop */}
            <div className="hidden lg:flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-heading font-bold text-accent mb-2">Create Consumer Account</h1>
                <p className="text-muted font-sans">
                  Already have an account?{' '}
                  <Link to="/login" className="text-primary font-medium hover:underline">
                    Log In
                  </Link>
                </p>
              </div>
            </div>

            {/* Header Area - Mobile */}
            <div className="lg:hidden text-center mb-8">
              <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Icon name="User" size={32} library="fi" className="text-primary" />
              </div>
              <h1 className="text-2xl font-heading font-bold text-accent mb-2">
                Create Consumer Account
              </h1>
              <p className="text-muted font-sans text-sm">
                Join thousands of Nigerians verifying products before they buy
              </p>
            </div>

            {/* Signup Form */}
            <Card>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* First Name & Last Name Row */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-500 mb-1 block">First Name *</label>
                    <input
                      type="text"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleChange}
                      onBlur={() => handleBlur('firstName')}
                      className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${getFieldError('firstName')
                        ? 'border-danger bg-danger/5 focus:ring-danger/20'
                        : touched.firstName && formData.firstName
                          ? 'border-primary bg-primary/5 focus:ring-primary/20'
                          : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                        }`}
                      placeholder="Chukwudi"
                    />
                    {getFieldError('firstName') && (
                      <p className="text-danger text-xs mt-1">{getFieldError('firstName')}</p>
                    )}
                  </div>

                  <div>
                    <label className="text-sm text-gray-500 mb-1 block">Last Name *</label>
                    <input
                      type="text"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleChange}
                      onBlur={() => handleBlur('lastName')}
                      className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${getFieldError('lastName')
                        ? 'border-danger bg-danger/5 focus:ring-danger/20'
                        : touched.lastName && formData.lastName
                          ? 'border-primary bg-primary/5 focus:ring-primary/20'
                          : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                        }`}
                      placeholder="Okafor"
                    />
                    {getFieldError('lastName') && (
                      <p className="text-danger text-xs mt-1">{getFieldError('lastName')}</p>
                    )}
                  </div>
                </div>

                {/* Phone Number */}
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

                {/* Custom Checkboxes */}
                <div className="space-y-3">
                  <CustomCheckbox
                    name="agreeLocation"
                    checked={formData.agreeLocation}
                    onChange={handleChange}
                    label="Allow SabiLens to use my device location for accurate counterfeit reporting"
                  />

                  <CustomCheckbox
                    name="agreeTerms"
                    checked={formData.agreeTerms}
                    onChange={handleChange}
                    label={
                      <>
                        I agree to the{' '}
                        <span
                          onClick={(e) => { e.preventDefault(); setShowTermsModal(true); }}
                          className="text-primary underline font-medium cursor-pointer"
                        >
                          Terms of Service
                        </span>{' '}
                        and{' '}
                        <span
                          onClick={(e) => { e.preventDefault(); setShowPrivacyModal(true); }}
                          className="text-primary underline font-medium cursor-pointer"
                        >
                          Privacy Policy
                        </span>
                      </>
                    }
                  />
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  variant="primary"
                  fullWidth
                  disabled={!isFormValid() || isSubmitting}
                >
                  {isSubmitting ? 'Creating Account...' : 'Create Free Account'}
                </Button>

                {/* Social Sign Up */}
                <div className="text-center">
                  <p className="text-sm text-gray-400 mb-4">OR CONTINUE WITH</p>
                  <div className="flex justify-center gap-4">
                    <button
                      type="button"
                      onClick={() => setShowGoogleModal(true)}
                      className="w-12 h-12 bg-white rounded-xl shadow-soft flex items-center justify-center hover:shadow-card transition-all hover:scale-110"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="28" height="28">
                        <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z" />
                        <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z" />
                        <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z" />
                        <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </form>
            </Card>

            {/* Mobile Login Link */}
            <p className="text-center lg:hidden text-gray-500 mt-6">
              Already have an account?{' '}
              <Link to="/login" className="text-primary font-medium hover:underline">
                Log In
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Success Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={handleModalClose}
        type={modalConfig.type}
        title={modalConfig.title}
        message={modalConfig.message}
      />

      {/* Google Coming Soon Modal */}
      <Modal
        isOpen={showGoogleModal}
        onClose={() => setShowGoogleModal(false)}
        type="info"
        title="Google Sign-In"
        message={
          <div className="text-center">
            <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Icon name="Clock" size={32} className="text-primary" library="fi" />
            </div>
            <p className="text-gray-600 mb-2">
              Google Sign-In is coming soon!
            </p>
            <p className="text-sm text-gray-500">
              You can still create an account using your phone number.
            </p>
          </div>
        }
      />

      {/* Terms of Service Modal */}
      <PolicyModal
        isOpen={showTermsModal}
        onClose={() => setShowTermsModal(false)}
        title="Terms of Service"
      >
        <div className="space-y-6">
          <p className="text-gray-500 text-sm mb-4">Last Updated: February 2026</p>
          
          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">1. Acceptance of Terms</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              By accessing or using SabiLens, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our service.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">2. Description of Service</h3>
            <p className="text-gray-600 text-sm leading-relaxed mb-3">
              SabiLens provides AI-powered product verification services to help consumers identify counterfeit products. The service includes:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600">
              <li>Product scanning and authentication</li>
              <li>Counterfeit reporting to NAFDAC authorities</li>
              <li>Scan history and analytics</li>
              <li>Safety alerts in Yorùbá, Hausa, Igbo, and English</li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">3. User Responsibilities</h3>
            <p className="text-gray-600 text-sm mb-3">As a user, you agree to:</p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600">
              <li>Provide accurate information when reporting counterfeits</li>
              <li>Use the service only for lawful purposes</li>
              <li>Not attempt to manipulate or falsify scan results</li>
              <li>Keep your account credentials secure</li>
              <li>Only scan products you intend to purchase or verify</li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">4. Intellectual Property</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              All content, features, and functionality of SabiLens are owned by SabiLens and protected by international copyright, trademark, and other intellectual property laws.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">5. Limitation of Liability</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              SabiLens provides verification results based on AI analysis. While we strive for 98%+ accuracy, we cannot guarantee 100% detection rate. Users should exercise their own judgment when purchasing products.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">6. Termination</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              We reserve the right to terminate or suspend access to our service immediately, without prior notice, for any reason, including breach of these Terms.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">7. Governing Law</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              These Terms shall be governed by the laws of the Federal Republic of Nigeria.
            </p>
          </div>
        </div>
      </PolicyModal>

      {/* Privacy Policy Modal */}
      <PolicyModal
        isOpen={showPrivacyModal}
        onClose={() => setShowPrivacyModal(false)}
        title="Privacy Policy"
      >
        <div className="space-y-6">
          <p className="text-gray-500 text-sm mb-4">Last Updated: February 2026</p>
          
          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">1. Information We Collect</h3>
            <p className="text-gray-600 text-sm mb-3">
              SabiLens collects information to provide better services to all our users. We collect:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600">
              <li><span className="font-medium">Account information:</span> Name, phone number (for account recovery)</li>
              <li><span className="font-medium">Location data:</span> GPS coordinates when you scan products (for counterfeit mapping)</li>
              <li><span className="font-medium">Scan history:</span> Images and verification results of products you scan</li>
              <li><span className="font-medium">Device information:</span> Camera access for scanning (never stored)</li>
              <li><span className="font-medium">State of residence:</span> For regional counterfeit hotspot analysis</li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">2. How We Use Your Information</h3>
            <p className="text-gray-600 text-sm mb-3">We use the information we collect to:</p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600">
              <li>Verify product authenticity instantly</li>
              <li>Generate counterfeit heatmaps for NAFDAC enforcement</li>
              <li>Improve our AI detection algorithms</li>
              <li>Send important safety alerts in your preferred language</li>
              <li>Build anonymous statistical data about counterfeit trends</li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">3. Data Sharing & Protection</h3>
            <p className="text-gray-600 text-sm mb-3">We do NOT sell your personal information. We may share anonymized scan data with:</p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600">
              <li><span className="font-medium">NAFDAC:</span> For regulatory enforcement against counterfeiters</li>
              <li><span className="font-medium">Brand owners:</span> To help them protect their products</li>
              <li><span className="font-medium">Research partners:</span> For academic studies on counterfeiting in Nigeria</li>
            </ul>
            <p className="text-gray-600 text-sm mt-3">
              All shared data is anonymized and stripped of personally identifiable information.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">4. Your Privacy Rights</h3>
            <p className="text-gray-600 text-sm mb-3">You have the right to:</p>
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600">
              <li>Access your personal data</li>
              <li>Delete your account and all associated data</li>
              <li>Opt out of non-essential data collection</li>
              <li>Request a copy of your scan history</li>
              <li>Disable location tracking at any time</li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">5. Data Security</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              We use bank-grade encryption to protect your data. Your phone number and scan history are stored securely and never shared with unauthorized third parties.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-heading font-semibold text-accent mb-3">6. Contact Us</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              For privacy-related questions, contact our Data Protection Officer at privacy@sabilens.ng
            </p>
          </div>
        </div>
      </PolicyModal>
    </div>
  );
};

export default ConsumerSignup;