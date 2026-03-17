import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SabiLensLogo from '../../assets/SabiLens_MainLogo.png';

const MobileSplash = () => {
  const navigate = useNavigate();
  const [activeDot, setActiveDot] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    // Cycle through dots every 1 second
    const dotInterval = setInterval(() => {
      setActiveDot((prev) => (prev + 1) % 3);
    }, 700);

    // Start fade out animation before navigation
    const fadeTimer = setTimeout(() => {
      setFadeOut(true);
    }, 4800);

    // Navigate to onboarding after 5 seconds
    const navTimer = setTimeout(() => {
      navigate('/onboarding');
    }, 5000);

    return () => {
      clearTimeout(navTimer);
      clearTimeout(fadeTimer);
      clearInterval(dotInterval);
    };
  }, [navigate]);

  return (
    <div className={`min-h-screen bg-white flex flex-col items-center justify-center px-6 transition-opacity duration-500 ${fadeOut ? 'opacity-0' : 'opacity-100'}`}>
      {/* Logo Only - Bigger, no text */}
      <div className="flex items-center justify-center animate-fade-up">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/20 rounded-full blur-3xl animate-pulse" />
          <img 
            src={SabiLensLogo} 
            alt="SabiLens" 
            className="w-48 h-48 object-contain relative z-10 animate-float"
          />
        </div>
      </div>

      {/* 3 Dots Loading Indicator - Smaller with sequential highlighting */}
      <div className="absolute bottom-20 left-0 right-0 flex justify-center space-x-2">
        <div 
          className="w-2 h-2 rounded-full transition-all duration-300"
          style={{
            backgroundColor: activeDot === 0 ? '#008753' : '#E5EAE8',
          }}
        />
        <div 
          className="w-2 h-2 rounded-full transition-all duration-300"
          style={{
            backgroundColor: activeDot === 1 ? '#008753' : '#E5EAE8',
          }}
        />
        <div 
          className="w-2 h-2 rounded-full transition-all duration-300"
          style={{
            backgroundColor: activeDot === 2 ? '#008753' : '#E5EAE8',
          }}
        />
      </div>

      {/* Version Number */}
      <p className="absolute bottom-8 text-xs text-muted/30 font-sans">
        Version 1.0.0
      </p>
    </div>
  );
};

export default MobileSplash;