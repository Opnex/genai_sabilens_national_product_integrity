import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Building, ArrowRight, ShieldCheck } from 'lucide-react';
import SabiLensLogo from '../../assets/SabiLens_Logo.png';
import Button from '../../components/ui/Button';

const RoleSelect = () => {
  const navigate = useNavigate();

  const handleRoleSelect = (role) => {
    if (role === 'consumer') {
      navigate('/signup');
    } else if (role === 'company') {
      navigate('/company/signup');
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
          <h2 className="text-4xl font-syne font-bold text-white mb-4 leading-tight">Join SabiLens</h2>
          <p className="text-white/60 font-sans text-lg mb-12">Choose how you want to use the platform.</p>
          <ul className="space-y-6 mb-16 font-sans text-white/80">
            <li className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <span>AI-powered product verification</span>
            </li>
            <li className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
                <User className="w-5 h-5" />
              </div>
              <span>Free for all Nigerians</span>
            </li>
            <li className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
                <Building className="w-5 h-5" />
              </div>
              <span>Brand protection tools</span>
            </li>
          </ul>
          <div className="bg-accent-2/50 backdrop-blur-sm border border-white/10 rounded-2xl p-6 border-l-4 border-l-primary">
            <p className="font-sans text-white/90 italic mb-4 leading-relaxed">
              "Over 50,000 Nigerians are already verifying products before they buy."
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

  return (
    <div className="min-h-screen bg-background flex">
      <BrandSidebar />
      <div className="flex-1 flex flex-col overflow-y-auto">
        {/* Mobile Header */}
        <div className="lg:hidden p-6 flex justify-between items-center border-b border-border bg-white sticky top-0 z-20">
          <Link to="/" className="flex items-center gap-2">
            <img src={SabiLensLogo} alt="SabiLens" className="h-6 w-auto" />
            <span className="font-syne font-bold text-xl text-accent tracking-tight">
              Sabi<span className="text-primary">Lens</span>
            </span>
          </Link>
          <Link to="/login" className="text-sm font-sans font-medium text-primary bg-primary-light px-4 py-2 rounded-lg">
            Log In
          </Link>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
          <div className="w-full max-w-md animate-fade-up">
            {/* Header Area */}
            <div className="mb-10 text-center lg:text-left">
              <h1 className="text-3xl font-syne font-bold text-accent mb-2">Create your account</h1>
              <p className="text-muted font-sans hidden lg:block">
                Already have an account? <Link to="/login" className="text-primary font-medium hover:underline transition-all">Log In</Link>
              </p>
            </div>

            {/* Role Selection Cards */}
            <div className="space-y-4">
              {/* Consumer Card */}
              <button
                onClick={() => handleRoleSelect('consumer')}
                className="w-full group bg-white border border-border hover:border-primary rounded-2xl p-6 text-left transition-all duration-300 hover:shadow-card flex items-center gap-4"
              >
                <div className="w-14 h-14 rounded-xl bg-primary-light flex items-center justify-center group-hover:scale-110 transition-transform">
                  <User className="text-primary w-7 h-7" />
                </div>
                <div className="flex-1">
                  <h3 className="font-heading font-bold text-lg text-accent mb-1">
                    Individual Consumer
                  </h3>
                  <p className="font-sans text-muted text-sm">
                    Scan products before buying
                  </p>
                </div>
                <ArrowRight className="text-primary w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>

              {/* Company Card */}
              <button
                onClick={() => handleRoleSelect('company')}
                className="w-full group bg-white border border-border hover:border-primary rounded-2xl p-6 text-left transition-all duration-300 hover:shadow-card flex items-center gap-4"
              >
                <div className="w-14 h-14 rounded-xl bg-primary-light flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Building className="text-primary w-7 h-7" />
                </div>
                <div className="flex-1">
                  <h3 className="font-heading font-bold text-lg text-accent mb-1">
                    Brand / Company
                  </h3>
                  <p className="font-sans text-muted text-sm">
                    Protect your products & brand
                  </p>
                </div>
                <ArrowRight className="text-primary w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            </div>

            {/* Mobile Login Link */}
            <p className="text-center lg:hidden text-muted font-sans text-sm mt-8">
              Already have an account?{' '}
              <Link to="/login" className="text-primary font-medium hover:underline">
                Log In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoleSelect;