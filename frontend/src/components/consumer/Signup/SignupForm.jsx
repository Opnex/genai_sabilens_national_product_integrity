import React, { useState, useEffect } from 'react';
import Icon from '../../common/Icon';
import Button from '../../common/Button';
import Card from '../../common/Card';
import Modal from '../../common/Modal';

// Nigeria states data
const NIGERIA_STATES = [
  'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
  'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo',
  'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa',
  'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
];

// City data mapping (for suggestions)
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

const SignupForm = ({ onSubmit }) => {
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

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [touched, setTouched] = useState({});
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [citySuggestions, setCitySuggestions] = useState([]);
  const [showCitySuggestions, setShowCitySuggestions] = useState(false);
  const [showGoogleModal, setShowGoogleModal] = useState(false);

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

  // Validation functions
  const validateField = (name, value) => {
    switch(name) {
      case 'firstName':
        return value.trim() ? '' : 'First name is required';
      case 'lastName':
        return value.trim() ? '' : 'Last name is required';
      case 'phone':
        return /^[0-9]{10}$/.test(value) ? '' : 'Enter a valid 10-digit Nigerian number';
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
      setFormData(prev => ({
        ...prev,
        [name]: numbersOnly
      }));
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
    const allFields = ['firstName', 'lastName', 'phone', 'state', 'city', 'password', 'confirmPassword'];
    const touchedFields = allFields.reduce((acc, field) => ({ ...acc, [field]: true }), {});
    setTouched(touchedFields);
    
    if (isFormValid()) {
      onSubmit(formData);
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
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* First Name & Last Name Row */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm text-gray-500 mb-1 block">First Name</label>
          <input
            type="text"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            onBlur={() => handleBlur('firstName')}
            className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
              getFieldError('firstName') 
                ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                : touched.firstName && formData.firstName
                ? 'border-primary bg-primary/5 focus:ring-primary/20'
                : 'border-gray-200 focus:border-primary focus:ring-primary/20'
            }`}
            placeholder="Enter first name"
          />
          {getFieldError('firstName') && (
            <p className="text-danger text-xs mt-1">{getFieldError('firstName')}</p>
          )}
        </div>

        <div>
          <label className="text-sm text-gray-500 mb-1 block">Last Name</label>
          <input
            type="text"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            onBlur={() => handleBlur('lastName')}
            className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
              getFieldError('lastName') 
                ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                : touched.lastName && formData.lastName
                ? 'border-primary bg-primary/5 focus:ring-primary/20'
                : 'border-gray-200 focus:border-primary focus:ring-primary/20'
            }`}
            placeholder="Enter last name"
          />
          {getFieldError('lastName') && (
            <p className="text-danger text-xs mt-1">{getFieldError('lastName')}</p>
          )}
        </div>
      </div>

      {/* Phone Number with +234 prefix */}
      <div>
        <label className="text-sm text-gray-500 mb-1 block">Phone Number</label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-medium">+234</span>
          <input
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            onBlur={() => handleBlur('phone')}
            placeholder="801 234 5678"
            maxLength="10"
            className={`w-full pl-16 pr-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
              getFieldError('phone') 
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

      {/* State and City Row - Now side by side on mobile */}
      <div className="grid grid-cols-2 gap-4">
        {/* State Selection */}
        <div>
          <label className="text-sm text-gray-500 mb-1 block">State</label>
          <select
            name="state"
            value={formData.state}
            onChange={handleChange}
            onBlur={() => handleBlur('state')}
            className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
              getFieldError('state') 
                ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                : touched.state && formData.state
                ? 'border-primary bg-primary/5 focus:ring-primary/20'
                : 'border-gray-200 focus:border-primary focus:ring-primary/20'
            }`}
          >
            <option value="">Select</option>
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
          <label className="text-sm text-gray-500 mb-1 block">City</label>
          <input
            type="text"
            name="city"
            value={formData.city}
            onChange={handleChange}
            onFocus={() => setShowCitySuggestions(true)}
            onBlur={() => handleBlur('city')}
            disabled={!formData.state}
            className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
              getFieldError('city') 
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
        <label className="text-sm text-gray-500 mb-1 block">Password</label>
        <div className="relative">
          <input
            type={showPassword ? 'text' : 'password'}
            name="password"
            value={formData.password}
            onChange={handleChange}
            onBlur={() => handleBlur('password')}
            onFocus={() => setPasswordFocused(true)}
            className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors pr-12 ${
              getFieldError('password') 
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
                  <div className={`w-4 h-4 rounded-full flex items-center justify-center ${
                    req.test(formData.password) ? 'bg-primary/20' : 'bg-gray-200'
                  }`}>
                    {req.test(formData.password) && (
                      <Icon name="Check" size={12} library="fi" className="text-primary" />
                    )}
                  </div>
                  <span className={`text-xs ${
                    req.test(formData.password) ? 'text-primary font-medium' : 'text-gray-500'
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
        <label className="text-sm text-gray-500 mb-1 block">Confirm Password</label>
        <div className="relative">
          <input
            type={showConfirmPassword ? 'text' : 'password'}
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            onBlur={() => handleBlur('confirmPassword')}
            className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors pr-12 ${
              getFieldError('confirmPassword') 
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
            <span>
              I agree to the{' '}
              <button type="button" className="text-primary hover:underline">Terms of Service</button>
              {' '}and{' '}
              <button type="button" className="text-primary hover:underline">Privacy Policy</button>
            </span>
          }
        />
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        variant="primary"
        fullWidth
        disabled={!isFormValid()}
      >
        Create Account
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
    </form>
  );
};

export default SignupForm;