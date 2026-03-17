import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../common/Icon';

const SplashScreen = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user has seen onboarding before
    const hasSeenOnboarding = localStorage.getItem('hasSeenOnboarding');
    
    // Auto navigate after 2.5 seconds
    const timer = setTimeout(() => {
      if (hasSeenOnboarding) {
        // If already seen onboarding, go to login/signup
        navigate('/signup');
      } else {
        // First time - go to onboarding
        navigate('/onboarding');
      }
    }, 2500);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center">
      {/* Logo/Icon */}
      <div className="w-24 h-24 bg-primary/10 rounded-3xl flex items-center justify-center mb-6">
        <Icon name="Shield" size={48} className="text-primary" />
      </div>
      
      {/* App Name */}
      <h1 className="text-3xl font-bold text-gray-900 mb-2">SabiLens</h1>
      <p className="text-gray-500 text-sm mb-8">AUTHENTICITY GUARD</p>
      
      {/* Loading Bar */}
      <div className="w-48 h-1 bg-gray-100 rounded-full overflow-hidden">
        <div 
          className="h-full bg-primary rounded-full animate-loading"
          style={{ width: '85%' }}
        />
      </div>
      
      {/* AI Tagline */}
      <p className="text-xs text-gray-400 mt-8">
        Powered by Multimodal Sabi AI
      </p>

      <style jsx>{`
        @keyframes loading {
          0% { width: 0%; }
          50% { width: 85%; }
          100% { width: 100%; }
        }
        .animate-loading {
          animation: loading 2s ease-in-out forwards;
        }
      `}</style>
    </div>
  );
};

export default SplashScreen;