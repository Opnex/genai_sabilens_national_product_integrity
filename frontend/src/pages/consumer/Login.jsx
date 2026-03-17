import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Shield, Mic, MapPin, User } from 'lucide-react';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import Toast from '../../components/ui/Toast';
import SabiLensLogo from '../../assets/SabiLens_Logo.png';

const Login = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    phone: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [toast, setToast] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name === 'phone') {
      const numbersOnly = value.replace(/\D/g, '');
      setFormData(prev => ({ ...prev, [name]: numbersOnly }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.phone) newErrors.phone = 'Phone number is required';
    if (!formData.password) newErrors.password = 'Password is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setIsSubmitting(true);
    try {
      const users = JSON.parse(localStorage.getItem('users') || '[]');
      const user = users.find(u => u.phone === formData.phone);
      if (!user) {
        setToast({ type: 'error', message: 'No account found with this phone number' });
        setIsSubmitting(false);
        return;
      }
      if (user.password !== formData.password) {
        setToast({ type: 'error', message: 'Incorrect password. Please try again.' });
        setIsSubmitting(false);
        return;
      }
      localStorage.setItem('currentUser', JSON.stringify({
        id: user.id || crypto.randomUUID(),
        phone: user.phone,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role || 'consumer'
      }));
      navigate('/home');
    } catch (error) {
      setToast({ type: 'error', message: 'An error occurred. Please try again.' });
      setIsSubmitting(false);
    }
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
        <div className="mt-auto">
          <h2 className="text-4xl font-syne font-bold text-white mb-4 leading-tight">Welcome Back</h2>
          <p className="text-white/60 font-sans text-lg mb-12">Log in to continue securing your purchases.</p>
          <ul className="space-y-6 mb-16 font-sans text-white/80">
            <li className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
                <Shield className="w-5 h-5" />
              </div>
              <span>Free forensic product scanning</span>
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
              "I avoided buying fake drugs at Ikeja market because of SabiLens."
            </p>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-primary" />
              </div>
              <span className="font-syne font-bold text-white text-sm">Fatima B., <span className="text-white/50 font-sans font-normal">Kano</span></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background flex">
      {toast && <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />}
      <BrandSidebar />
      <div className="flex-1 flex flex-col overflow-y-auto">
        <div className="lg:hidden p-6 flex justify-between items-center border-b border-border bg-white sticky top-0 z-20">
          <Link to="/" className="flex items-center gap-2">
            <img src={SabiLensLogo} alt="SabiLens" className="h-6 w-auto" />
            <span className="font-syne font-bold text-xl text-accent tracking-tight">
              Sabi<span className="text-primary">Lens</span>
            </span>
          </Link>
          <Link to="/signup" className="text-sm font-sans font-medium text-primary bg-primary-light px-4 py-2 rounded-lg">
            Sign Up
          </Link>
        </div>
        <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
          <div className="w-full max-w-md animate-fade-up">
            <div className="mb-10 text-center lg:text-left">
              <h1 className="text-3xl font-syne font-bold text-accent mb-2">Welcome back</h1>
              <p className="text-muted font-sans hidden lg:block">
                Don't have an account? <Link to="/signup" className="text-primary font-medium hover:underline transition-all">Sign Up</Link>
              </p>
            </div>
            <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 sm:p-8 rounded-3xl border border-border shadow-soft">
              {/* Phone Input - Fixed label by removing it to eliminate floating line above placeholder */}
              <Input
                name="phone"
                type="tel"
                placeholder=" 801 234 5678"
                value={formData.phone}
                onChange={handleInputChange}
                error={errors.phone}
                prefix={<span className="font-mono text-accent">🇳🇬 +234</span>}
                maxLength={10}
              />
              
              {/* Password Input - Custom styled input to avoid double eye icon */}
              <div className="space-y-1">
                <label className="text-sm text-gray-500 mb-1 block">Password</label>
                <div className="relative">
                  <div className="relative flex items-center border border-border rounded-xl bg-white focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all">
                    <input
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      value={formData.password}
                      onChange={handleInputChange}
                      className="flex-1 w-full px-4 py-3 bg-transparent outline-none font-sans text-accent placeholder:text-muted/50 rounded-xl pr-12"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 text-gray-400 hover:text-primary transition-colors"
                    >
                      {showPassword ? <Eye size={20} /> : <EyeOff size={20} />}
                    </button>
                  </div>
                  {errors.password && (
                    <p className="text-danger text-xs mt-1 font-sans">{errors.password}</p>
                  )}
                </div>
                <div className="flex justify-end pt-1">
                  <button
                    type="button"
                    onClick={() => setToast({ type: 'info', message: 'Password reset feature coming soon.' })}
                    className="font-sans text-sm text-primary hover:underline font-medium"
                  >
                    Forgot password?
                  </button>
                </div>
              </div>

              <div className="pt-4">
                <Button type="submit" variant="primary" size="lg" fullWidth isLoading={isSubmitting}>
                  Log In →
                </Button>
              </div>
              <div className="relative py-4 flex items-center">
                <div className="flex-grow border-t border-border" />
                <span className="flex-shrink-0 mx-4 text-muted text-sm font-sans">or continue with</span>
                <div className="flex-grow border-t border-border" />
              </div>
              <button
                type="button"
                onClick={() => setToast({ type: 'info', message: 'Google authentication coming soon.' })}
                className="w-full relative flex items-center justify-center gap-3 bg-white border border-border px-6 py-3.5 rounded-xl hover:bg-surface-2 transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-border shadow-soft text-accent font-sans font-medium"
              >
                <svg className="w-5 h-5 absolute left-6" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                </svg>
                Continue with Google
              </button>
            </form>
            <p className="text-center lg:hidden text-muted font-sans text-sm mt-6">
              Don't have an account?{' '}
              <Link to="/signup" className="text-primary font-medium hover:underline">
                Sign Up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;