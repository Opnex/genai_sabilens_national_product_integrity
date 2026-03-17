import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import Button from '../../ui/Button';

const OnboardingLayout = ({
  currentScreen,
  totalScreens,
  title,
  description,
  illustration,
  onNext,
  onBack,
  onSkip,
  showBack = false
}) => {
  return (
    <div className="h-screen bg-white flex flex-col font-sans overflow-hidden">
      {/* Header - Compact */}
      <div className="flex justify-between items-center px-5 pt-5 pb-2 relative z-10">
        {showBack ? (
          <button
            onClick={onBack}
            className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-50 border border-gray-100 active:scale-95 transition-transform"
          >
            <ArrowLeft size={16} className="text-accent" />
          </button>
        ) : (
          <div className="w-9" />
        )}

        <button
          onClick={onSkip}
          className="text-primary text-xs font-bold font-heading tracking-tight px-3 py-1.5 rounded-lg bg-primary-light/30 active:scale-95 transition-transform"
        >
          Skip
        </button>
      </div>

      {/* Content Area - Fits perfectly on screen */}
      <div className="flex-1 flex flex-col relative px-6 pt-2 pb-6">
        {/* Animated Background Element */}
        <div className="absolute top-[5%] left-1/2 -translate-x-1/2 w-[140%] aspect-square bg-primary/5 rounded-full blur-[80px] pointer-events-none" />

        <AnimatePresence mode="wait">
          <motion.div
            key={currentScreen}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="flex-1 flex flex-col items-center justify-center text-center relative z-10"
          >
            {/* Illustration - Fixed size */}
            <motion.div
              initial={{ scale: 0.9, rotate: -3 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.1, type: "spring", stiffness: 100 }}
              className="w-64 h-64 rounded-[32px] bg-white border-2 border-primary/10 shadow-xl shadow-primary/5 flex items-center justify-center mb-6 relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-50" />
              {illustration}
            </motion.div>

            {/* Text - Compact */}
            <h1 className="text-2xl font-heading font-extrabold text-accent leading-tight mb-2 tracking-tight px-4">
              {title}
            </h1>
            <p className="text-muted text-sm leading-relaxed max-w-[260px] px-4">
              {description}
            </p>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Bottom Controls - Compact */}
      <div className="px-6 pb-8 relative z-10">
        {/* Progress Dots */}
        <div className="flex justify-center gap-2 mb-6">
          {Array.from({ length: totalScreens }).map((_, i) => (
            <motion.div
              key={i}
              initial={false}
              animate={{
                width: i === currentScreen ? 20 : 6,
                backgroundColor: i === currentScreen ? '#008753' : '#E5E7EB'
              }}
              className="h-1.5 rounded-full transition-colors"
            />
          ))}
        </div>

        {/* Button */}
        <Button
          variant="primary"
          size="lg"
          fullWidth
          onClick={onNext}
          className="shadow-lg shadow-primary/20 h-12 text-base font-heading font-bold"
        >
          {currentScreen === totalScreens - 1 ? 'Get Started' : 'Continue'}
          {currentScreen !== totalScreens - 1 && <ArrowRight size={16} className="ml-2" />}
        </Button>
      </div>
    </div>
  );
};

export default OnboardingLayout;