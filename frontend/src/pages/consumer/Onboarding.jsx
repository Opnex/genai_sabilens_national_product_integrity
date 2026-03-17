import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import OnboardingScreen from '../../components/consumer/Onboarding/OnboardingScreen';

const Onboarding = () => {
  const [screen, setScreen] = useState(0);
  const navigate = useNavigate();

  const handleNext = () => {
    if (screen === 2) {
      // Mark that user has seen onboarding
      localStorage.setItem('hasSeenOnboarding', 'true');
      navigate('/role-select');
    } else {
      setScreen(screen + 1);
    }
  };

  const handleBack = () => {
    if (screen > 0) {
      setScreen(screen - 1);
    }
  };

  const handleSkip = () => {
    localStorage.setItem('hasSeenOnboarding', 'true');
    navigate('/role-select');
  };

  return (
    <OnboardingScreen
      screen={screen}
      onNext={handleNext}
      onBack={handleBack}
      onSkip={handleSkip}
    />
  );
};

export default Onboarding;