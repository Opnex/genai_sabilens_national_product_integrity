import React from 'react';
import { motion } from 'framer-motion';
import { Camera, ShieldCheck, Zap, Globe, MessageSquare } from 'lucide-react';
import OnboardingLayout from './OnboardingLayout';

const OnboardingScreen = ({ screen, onNext, onBack, onSkip }) => {
  const screens = [
    {
      title: 'Real Products. Real Safety.',
      description: 'Verify food and drugs in seconds with AI. No more guesswork.',
      illustration: (
        <div className="relative scale-90">
          <motion.div
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            className="w-28 h-36 bg-accent rounded-2xl flex flex-col p-3 shadow-2xl relative z-10"
          >
            <div className="w-full h-20 bg-primary/10 rounded-lg mb-2 flex items-center justify-center">
              <ShieldCheck className="text-primary w-10 h-10" />
            </div>
            <div className="space-y-1">
              <div className="h-1.5 w-full bg-white/20 rounded-full" />
              <div className="h-1.5 w-3/4 bg-white/20 rounded-full" />
            </div>
          </motion.div>
          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute -top-3 -right-3 w-10 h-10 bg-primary rounded-full flex items-center justify-center shadow-lg shadow-primary/30 z-20"
          >
            <Camera className="text-white w-5 h-5" />
          </motion.div>
        </div>
      )
    },
    {
      title: '2-Point Forensic Scan',
      description: 'Scan front and back. AI verifies NAFDAC codes & packaging instantly.',
      illustration: (
        <div className="relative flex items-center justify-center scale-90">
          <motion.div
            className="absolute inset-0 bg-primary/10 rounded-full"
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.2, 0.5] }}
            transition={{ duration: 4, repeat: Infinity }}
          />
          <div className="flex gap-3 relative z-10">
            <motion.div
              animate={{ rotate: [0, 180, 180, 0] }}
              transition={{ duration: 6, repeat: Infinity, times: [0, 0.4, 0.6, 1] }}
              className="w-20 h-28 bg-white border-2 border-primary/20 rounded-xl flex items-center justify-center shadow-lg"
            >
              <Zap className="text-primary w-8 h-8" />
            </motion.div>
            <motion.div
              animate={{ rotate: [0, -180, -180, 0] }}
              transition={{ duration: 6, repeat: Infinity, times: [0, 0.4, 0.6, 1], delay: 0.5 }}
              className="w-20 h-28 bg-white border-2 border-primary/20 rounded-xl flex items-center justify-center shadow-lg"
            >
              <Camera className="text-primary w-8 h-8" />
            </motion.div>
          </div>
          <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-primary/40 shadow-[0_0_10px_rgba(0,135,83,0.5)] z-20" />
        </div>
      )
    },
    {
      title: 'In Your Language',
      description: 'Voice results in Yorùbá, Hausa, Igbo, or English. Sabi is for everyone.',
      illustration: (
        <div className="relative scale-90">
          <div className="flex flex-wrap justify-center gap-2 max-w-[220px]">
            {['English', 'Yorùbá', 'Hausa', 'Igbo'].map((lang, i) => (
              <motion.div
                key={lang}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.15 + 0.5 }}
                className="px-3 py-1.5 bg-white border border-border rounded-full shadow-sm text-xs font-heading font-bold text-accent"
              >
                {lang}
              </motion.div>
            ))}
          </div>
          <motion.div
            animate={{ y: [0, -5, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute -bottom-12 left-1/2 -translate-x-1/2 w-14 h-14 bg-primary-light rounded-2xl flex items-center justify-center"
          >
            <MessageSquare className="text-primary w-6 h-6" />
          </motion.div>
        </div>
      )
    }
  ];

  return (
    <OnboardingLayout
      currentScreen={screen}
      totalScreens={screens.length}
      title={screens[screen].title}
      description={screens[screen].description}
      illustration={screens[screen].illustration}
      onNext={onNext}
      onBack={onBack}
      onSkip={onSkip}
      showBack={screen > 0}
    />
  );
};

export default OnboardingScreen;