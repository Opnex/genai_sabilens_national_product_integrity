import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Home, Camera, User } from 'lucide-react';

const ConsumerBottomNav = () => {
  const location = useLocation();

  const navItems = [
    { path: '/home', icon: Home, label: 'Home' },
    { path: '/profile', icon: User, label: 'Profile' }
  ];

  const isActive = (path) => {
    if (path === '/home') {
      return location.pathname === '/home' || location.pathname === '/';
    }
    return location.pathname === path;
  };

  const LeftIcon = navItems[0].icon;
  const RightIcon = navItems[1].icon;

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-border pb-safe">
      <div className="flex justify-around items-center h-16 px-6">
        {/* Left Item */}
        <Link
          to={navItems[0].path}
          className={`flex flex-col items-center gap-1 w-16 transition-colors duration-200 ${isActive(navItems[0].path) ? 'text-primary' : 'text-muted hover:text-accent'
            }`}
        >
          <LeftIcon className={`w-6 h-6 ${isActive(navItems[0].path) ? 'fill-current' : ''}`} strokeWidth={isActive(navItems[0].path) ? 2 : 1.5} />
          <span className="text-[10px] font-medium font-sans">{navItems[0].label}</span>
          {/* Active indicator dot */}
          {isActive(navItems[0].path) && <div className="w-1 h-1 rounded-full bg-primary mt-0.5 animate-fadeIn" />}
        </Link>

        {/* Center Item (Raised Scan Button) */}
        <Link
          to="/scan"
          className="relative -top-5 flex flex-col items-center group"
          aria-label="Scan Product"
        >
          <div className={`flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br from-primary to-primary-dark shadow-glow transition-transform duration-300 group-hover:scale-105 active:scale-95 border-4 border-white ${location.pathname === '/scan' ? 'ring-2 ring-primary ring-offset-2' : ''
            }`}>
            <Camera className="w-6 h-6 text-white" strokeWidth={2} />
          </div>
          <span className={`text-[10px] font-bold font-syne mt-1 ${location.pathname === '/scan' ? 'text-primary' : 'text-accent'}`}>
            Scan
          </span>
        </Link>

        {/* Right Item */}
        <Link
          to={navItems[1].path}
          className={`flex flex-col items-center gap-1 w-16 transition-colors duration-200 ${isActive(navItems[1].path) ? 'text-primary' : 'text-muted hover:text-accent'
            }`}
        >
          <RightIcon className={`w-6 h-6 ${isActive(navItems[1].path) ? 'fill-current' : ''}`} strokeWidth={isActive(navItems[1].path) ? 2 : 1.5} />
          <span className="text-[10px] font-medium font-sans">{navItems[1].label}</span>
          {/* Active indicator dot */}
          {isActive(navItems[1].path) && <div className="w-1 h-1 rounded-full bg-primary mt-0.5 animate-fadeIn" />}
        </Link>
      </div>
    </div>
  );
};

export default ConsumerBottomNav;