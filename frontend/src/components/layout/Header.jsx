import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const Header = ({ title, showBack = false, showNotification = false, showLanguage = false, variant = 'consumer' }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    // Get user from localStorage
    const user = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const userInitials = user.firstName && user.lastName
        ? `${user.firstName[0]}${user.lastName[0]}`.toUpperCase()
        : 'U';

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const bgClasses = {
        consumer: isScrolled ? 'bg-white/80 backdrop-blur-md border-b border-border' : 'bg-transparent',
        company: 'bg-white border-b border-border',
        nafdac: 'bg-white border-b border-border',
        dark: 'bg-accent text-white',
        transparent: 'bg-transparent text-white'
    };

    const navLinks = variant === 'company' ? [
        { name: 'Dashboard', path: '/company/dashboard' },
        { name: 'Registry', path: '/company/registry' },
        { name: 'Reports', path: '/company/reports' }
    ] : variant === 'nafdac' ? [
        { name: 'Dashboard', path: '/nafdac/dashboard' },
        { name: 'National Map', path: '/nafdac/map' },
        { name: 'Alerts', path: '/nafdac/alerts' }
    ] : [];

    return (
        <header
            aria-label="Site Header"
            className={`fixed top-0 w-full z-50 transition-all duration-300 ${bgClasses[variant]}`}
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">

                    {/* Left: Logo or Back + Title */}
                    <div className="flex items-center gap-3">
                        {showBack ? (
                            <button
                                onClick={() => navigate(-1)}
                                className={`p-2 rounded-full hover:bg-black/5 transition-colors ${variant.includes('dark') || variant === 'transparent' ? 'text-white' : 'text-accent'}`}
                                aria-label="Go back"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>
                            </button>
                        ) : null}

                        {title ? (
                            <h1 className="text-xl font-syne font-bold truncate">{title}</h1>
                        ) : (
                            <Link to="/home" className="flex items-center gap-2 group">
                                <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-primary-dark shadow-glow group-hover:scale-105 transition-transform duration-300">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg>
                                </div>
                                <span className={`font-syne font-bold text-xl tracking-tight hidden sm:block ${variant.includes('dark') || variant === 'transparent' ? 'text-white' : 'text-accent'}`}>
                                    Sabi<span className="text-primary">Lens</span>
                                </span>
                            </Link>
                        )}
                    </div>

                    {/* Center: Desktop Nav Links (For Dashboards) */}
                    {navLinks.length > 0 && (
                        <nav className="hidden md:flex items-center gap-6">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.name}
                                    to={link.path}
                                    className={`text-sm font-semibold transition-colors hover:text-primary ${location.pathname.includes(link.path)
                                            ? 'text-primary border-b-2 border-primary py-5'
                                            : 'text-muted'
                                        }`}
                                >
                                    {link.name}
                                </Link>
                            ))}
                        </nav>
                    )}

                    {/* Right: Actions & User */}
                    <div className="flex items-center gap-2 sm:gap-4">
                        {showLanguage && (
                            <button className={`p-2 rounded-full hover:bg-black/5 transition-colors ${variant.includes('dark') || variant === 'transparent' ? 'text-white' : 'text-accent'}`} aria-label="Select Language">
                                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" /><path d="M2 12h20" /></svg>
                            </button>
                        )}

                        {showNotification && (
                            <button className={`relative p-2 rounded-full hover:bg-black/5 transition-colors ${variant.includes('dark') || variant === 'transparent' ? 'text-white' : 'text-accent'}`} aria-label="Notifications">
                                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" /><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" /></svg>
                                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-danger border border-white"></span>
                            </button>
                        )}

                        {/* User Avatar */}
                        {!title && !showBack && (
                            <Link to="/profile" className="flex items-center gap-2 pl-2">
                                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-surface-2 text-primary font-bold text-sm border border-primary/20">
                                    {userInitials}
                                </div>
                                {variant !== 'consumer' && (
                                    <div className="hidden sm:block text-sm text-left leading-tight">
                                        <p className="font-bold truncate max-w-[100px]">{user.firstName || 'User'}</p>
                                        <p className="text-[10px] text-muted capitalize">{user.role || variant}</p>
                                    </div>
                                )}
                            </Link>
                        )}

                        {/* Mobile Hamburger (Only for dashboard variants) */}
                        {navLinks.length > 0 && (
                            <button
                                className="md:hidden p-2 text-accent"
                                onClick={() => setIsMenuOpen(!isMenuOpen)}
                                aria-label="Toggle menu"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    {isMenuOpen ? (
                                        <><path d="M18 6 6 18" /><path d="m6 6 12 12" /></>
                                    ) : (
                                        <><line x1="4" x2="20" y1="12" y2="12" /><line x1="4" x2="20" y1="6" y2="6" /><line x1="4" x2="20" y1="18" y2="18" /></>
                                    )}
                                </svg>
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Mobile Menu Dropdown */}
            <AnimatePresence>
                {isMenuOpen && navLinks.length > 0 && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="md:hidden bg-white border-b border-border overflow-hidden"
                    >
                        <nav className="flex flex-col px-4 pt-2 pb-4 gap-1">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.name}
                                    to={link.path}
                                    onClick={() => setIsMenuOpen(false)}
                                    className={`p-3 rounded-xl font-semibold transition-colors ${location.pathname.includes(link.path)
                                            ? 'bg-surface-2 text-primary'
                                            : 'text-accent hover:bg-gray-50'
                                        }`}
                                >
                                    {link.name}
                                </Link>
                            ))}
                        </nav>
                    </motion.div>
                )}
            </AnimatePresence>
        </header>
    );
};

export default Header;
