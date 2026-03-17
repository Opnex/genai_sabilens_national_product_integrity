import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/common/Icon';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import { mockUploadImage } from '../../services/cloudinary';

const EditProfile = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  // Get current user data
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  const users = JSON.parse(localStorage.getItem('users') || '[]');
  const userData = users.find(u => u.phone === currentUser.phone) || {};
  
  const [formData, setFormData] = useState({
    firstName: userData.firstName || '',
    lastName: userData.lastName || '',
    phone: userData.phone || '',
    email: userData.email || '',
    city: userData.city || '',
    state: userData.state || '',
    language: userData.language || 'English',
    profileImage: userData.profileImage || null
  });

  const [isUploading, setIsUploading] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [touched, setTouched] = useState({});
  const [previewImage, setPreviewImage] = useState(userData.profileImage || null);

  const nigerianStates = [
    'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
    'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo',
    'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa',
    'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
  ];

  const languages = ['English', 'Yoruba', 'Hausa', 'Igbo', 'Pidgin'];

  const validateField = (name, value) => {
    switch(name) {
      case 'firstName':
        return value.trim() ? '' : 'First name is required';
      case 'lastName':
        return value.trim() ? '' : 'Last name is required';
      case 'email':
        if (!value) return ''; // Email is optional
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? '' : 'Invalid email format';
      case 'phone':
        return /^[0-9]{10}$/.test(value) ? '' : 'Valid 10-digit number required';
      case 'city':
        return value.trim() ? '' : 'City is required';
      case 'state':
        return value ? '' : 'State is required';
      default:
        return '';
    }
  };

  const getFieldError = (name) => {
    if (!touched[name]) return '';
    return validateField(name, formData[name]);
  };

  const isFormValid = () => {
    const requiredFields = ['firstName', 'lastName', 'phone', 'city', 'state'];
    return requiredFields.every(field => !validateField(field, formData[field]));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'phone') {
      const numbersOnly = value.replace(/\D/g, '');
      setFormData(prev => ({ ...prev, [name]: numbersOnly }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleBlur = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    
    try {
      // Create local preview immediately
      const previewUrl = URL.createObjectURL(file);
      setPreviewImage(previewUrl);
      
      // Simulate upload to Cloudinary
      const result = await mockUploadImage(file);
      
      if (result.success) {
        setFormData(prev => ({ ...prev, profileImage: result.url }));
        setPreviewImage(result.url);
      }
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveImage = () => {
    setPreviewImage(null);
    setFormData(prev => ({ ...prev, profileImage: null }));
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSave = () => {
    // Mark all fields as touched
    const allFields = ['firstName', 'lastName', 'phone', 'city', 'state'];
    const touchedFields = allFields.reduce((acc, field) => ({ ...acc, [field]: true }), {});
    setTouched(touchedFields);

    if (!isFormValid()) return;

    // Update user data in users array
    const updatedUsers = users.map(u => {
      if (u.phone === currentUser.phone) {
        return {
          ...u,
          firstName: formData.firstName,
          lastName: formData.lastName,
          city: formData.city,
          state: formData.state,
          language: formData.language,
          email: formData.email,
          profileImage: formData.profileImage
        };
      }
      return u;
    });

    localStorage.setItem('users', JSON.stringify(updatedUsers));

    // Update current user
    localStorage.setItem('currentUser', JSON.stringify({
      ...currentUser,
      firstName: formData.firstName,
      lastName: formData.lastName,
      profileImage: formData.profileImage
    }));

    // Force refresh of home page data
    window.dispatchEvent(new Event('focus'));

    setShowSuccessModal(true);
  };

  const handleCancel = () => {
    setShowCancelModal(true);
  };

  const getInitials = () => {
    const first = formData.firstName?.[0] || '';
    const last = formData.lastName?.[0] || '';
    return (first + last).toUpperCase() || 'U';
  };

  // Cleanup preview URL on unmount
  useEffect(() => {
    return () => {
      if (previewImage && previewImage.startsWith('blob:')) {
        URL.revokeObjectURL(previewImage);
      }
    };
  }, [previewImage]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-white px-6 pt-12 pb-4 sticky top-0 z-10 shadow-soft">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={handleCancel}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Icon name="ArrowLeft" size={20} className="text-gray-600" library="fi" />
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Edit Profile</h1>
          </div>
          <button
            onClick={handleSave}
            disabled={!isFormValid()}
            className={`px-6 py-2 rounded-xl font-medium transition-all ${
              isFormValid() 
                ? 'bg-primary text-white hover:bg-primary-dark shadow-md hover:shadow-lg' 
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            Save
          </button>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Profile Image Section */}
        <Card>
          <div className="flex flex-col items-center">
            <div className="relative mb-4 group">
              {/* Profile Image */}
              <div className="w-28 h-28 rounded-full overflow-hidden bg-primary/10 flex items-center justify-center border-4 border-white shadow-lg">
                {previewImage ? (
                  <img 
                    src={previewImage} 
                    alt="Profile" 
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.onerror = null;
                      setPreviewImage(null);
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-primary">
                    <span className="text-white text-3xl font-bold">{getInitials()}</span>
                  </div>
                )}
              </div>

              {/* Upload Overlay */}
              <div className="absolute inset-0 rounded-full bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="w-10 h-10 bg-white rounded-full flex items-center justify-center hover:bg-gray-100 transition-colors"
                >
                  {isUploading ? (
                    <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Icon name="Camera" size={18} className="text-primary" library="fi" />
                  )}
                </button>
              </div>

              {/* Remove Image Button (only shown if image exists) */}
              {previewImage && (
                <button
                  onClick={handleRemoveImage}
                  className="absolute -bottom-2 -right-2 w-8 h-8 bg-danger text-white rounded-full flex items-center justify-center border-2 border-white shadow-md hover:bg-danger-dark transition-colors"
                  title="Remove image"
                >
                  <Icon name="X" size={14} className="text-white" library="fi" />
                </button>
              )}

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
            </div>

            <p className="text-sm text-gray-400">
              {isUploading ? 'Uploading...' : 'Tap to change profile picture'}
            </p>
            <p className="text-xs text-gray-300 mt-1">
              Recommended: Square image, at least 400x400px
            </p>
          </div>
        </Card>

        {/* Personal Information */}
        <Card>
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Icon name="User" size={18} className="text-primary" library="fi" />
            Personal Information
          </h3>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-500 mb-1 block">
                  First Name <span className="text-danger">*</span>
                </label>
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
                <label className="text-sm text-gray-500 mb-1 block">
                  Last Name <span className="text-danger">*</span>
                </label>
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

            <div>
              <label className="text-sm text-gray-500 mb-1 block">
                Phone Number <span className="text-danger">*</span>
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-medium">+234</span>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  onBlur={() => handleBlur('phone')}
                  disabled
                  className="w-full pl-16 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-100 text-gray-500 cursor-not-allowed"
                  placeholder="8012345678"
                />
              </div>
              <p className="text-xs text-gray-400 mt-1 flex items-center gap-1">
                <Icon name="Info" size={12} className="text-gray-400" library="fi" />
                Phone number cannot be changed
              </p>
            </div>

            <div>
              <label className="text-sm text-gray-500 mb-1 block">Email (Optional)</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                onBlur={() => handleBlur('email')}
                className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                  getFieldError('email') 
                    ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                    : formData.email && !getFieldError('email')
                    ? 'border-primary bg-primary/5 focus:ring-primary/20'
                    : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                }`}
                placeholder="Enter your email"
              />
              {getFieldError('email') && (
                <p className="text-danger text-xs mt-1">{getFieldError('email')}</p>
              )}
            </div>
          </div>
        </Card>

        {/* Location Information */}
        <Card>
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Icon name="MapPin" size={18} className="text-primary" library="fi" />
            Location <span className="text-danger text-xs">*Required</span>
          </h3>

          <div className="space-y-4">
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
                <option value="">Select State</option>
                {nigerianStates.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
              {getFieldError('state') && (
                <p className="text-danger text-xs mt-1">{getFieldError('state')}</p>
              )}
            </div>

            <div>
              <label className="text-sm text-gray-500 mb-1 block">City</label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleChange}
                onBlur={() => handleBlur('city')}
                className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                  getFieldError('city') 
                    ? 'border-danger bg-danger/5 focus:ring-danger/20' 
                    : touched.city && formData.city
                    ? 'border-primary bg-primary/5 focus:ring-primary/20'
                    : 'border-gray-200 focus:border-primary focus:ring-primary/20'
                }`}
                placeholder="Enter your city"
              />
              {getFieldError('city') && (
                <p className="text-danger text-xs mt-1">{getFieldError('city')}</p>
              )}
            </div>
          </div>
        </Card>

        {/* Preferences */}
        <Card>
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Icon name="Settings" size={18} className="text-primary" library="fi" />
            Preferences
          </h3>

          <div>
            <label className="text-sm text-gray-500 mb-1 block">Preferred Language</label>
            <select
              name="language"
              value={formData.language}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              {languages.map(lang => (
                <option key={lang} value={lang}>{lang}</option>
              ))}
            </select>
            <p className="text-xs text-gray-400 mt-1">
              Choose your preferred language for voice alerts
            </p>
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="space-y-3 pt-4">
          <Button
            variant="primary"
            fullWidth
            onClick={handleSave}
            disabled={!isFormValid()}
            icon="Check"
          >
            Save Changes
          </Button>

          <button
            onClick={handleCancel}
            className="w-full py-3 text-gray-500 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
          >
            <Icon name="X" size={18} className="text-gray-400" library="fi" />
            Cancel
          </button>
        </div>
      </div>

      {/* Success Modal */}
      <Modal
        isOpen={showSuccessModal}
        onClose={() => {
          setShowSuccessModal(false);
          navigate('/profile');
        }}
        type="success"
        title="Profile Updated!"
        message={
          <div className="text-center">
            <p className="text-gray-600 mb-2">
              Your profile has been successfully updated.
            </p>
            <p className="text-xs text-gray-400">
              Changes will be reflected across the app.
            </p>
          </div>
        }
      />

      {/* Cancel Confirmation Modal */}
      <Modal
        isOpen={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        type="warning"
        title="Discard Changes?"
        message={
          <div>
            <p className="text-gray-600 mb-4">You have unsaved changes. Are you sure you want to leave?</p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setShowCancelModal(false)}
              >
                Stay
              </Button>
              <Button
                variant="danger"
                onClick={() => {
                  setShowCancelModal(false);
                  navigate('/profile');
                }}
              >
                Discard
              </Button>
            </div>
          </div>
        }
      />
    </div>
  );
};

export default EditProfile;