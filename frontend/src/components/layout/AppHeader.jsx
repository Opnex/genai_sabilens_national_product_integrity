import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bell, ChevronLeft } from 'lucide-react';
import SabiLensLogo from '../../assets/SabiLens_Logo.png';

const AppHeader = ({ title, showBack = false, onBack }) => {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const initials = (user.firstName?.[0] || 'U') + (user.lastName?.[0] || '');

    return (
        <header className="sticky top-0 z-40 w-full bg-white/80 backdrop-blur-md border-b border-border">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex h-16 items-center justify-between gap-4">

                    {/* Left: Logo or Back */}
                    <div className="flex items-center gap-3 min-w-0">
                        {showBack ? (
                            <button
                                onClick={onBack || (() => navigate(-1))}
                                className="p-2 -ml-2 rounded-full hover:bg-surface-2 transition-colors text-accent"
                            >
                                <ChevronLeft size={24} />
                            </button>
                        ) : (
                            <Link to="/home" className="flex items-center gap-2 group shrink-0">
                                <img 
                                    src={SabiLensLogo} 
                                    alt="SabiLens" 
                                    className="h-7 w-auto group-hover:scale-105 transition-transform" 
                                />
                                <span className="font-syne font-bold text-lg text-accent tracking-tight hidden xs:block">
                                    Sabi<span className="text-primary">Lens</span>
                                </span>
                            </Link>
                        )}

                        {title && (
                            <h1 className="text-base sm:text-lg font-syne font-bold text-accent truncate ml-1">
                                {title}
                            </h1>
                        )}
                    </div>

                    {/* Right: Actions */}
                    <div className="flex items-center gap-2 sm:gap-4 shrink-0">
                        <button className="relative p-2 rounded-full hover:bg-surface-2 transition-colors text-accent">
                            <Bell size={20} />
                            <span className="absolute top-2 right-2 w-2 h-2 bg-danger rounded-full border-2 border-white"></span>
                        </button>

                        <Link
                            to="/profile"
                            className="flex items-center justify-center w-9 h-9 rounded-full bg-primary-light border border-primary/20 text-primary font-syne font-bold text-sm hover:scale-105 transition-transform"
                        >
                            {initials.toUpperCase()}
                        </Link>
                    </div>

                </div>
            </div>
        </header>
    );
};

export default AppHeader;