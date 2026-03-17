import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Home, History, LifeBuoy } from 'lucide-react';

const Footer = ({ variant = 'dark' }) => {
    const currentYear = new Date().getFullYear();

    const bgClasses = variant === 'dark'
        ? 'bg-accent text-white'
        : 'bg-white text-accent border-t border-border';

    const textMutedClasses = variant === 'dark'
        ? 'text-gray-400 hover:text-white'
        : 'text-muted hover:text-primary';

    return (
        <footer aria-label="Site Footer" className={`${bgClasses} pt-12 pb-6 mt-auto`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

                {/* Top Section */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">

                    {/* Left: Brand */}
                    <div className="flex flex-col items-center md:items-start space-y-4">
                        <Link to="/" className="flex items-center gap-2 group">
                            <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-primary-dark shadow-glow group-hover:scale-105 transition-transform duration-300">
                                <Shield className="w-[18px] h-[18px] text-white" />
                            </div>
                            <span className="font-syne font-bold text-xl tracking-tight">
                                Sabi<span className="text-primary">Lens</span>
                            </span>
                        </Link>
                        <p className={`text-sm text-center md:text-left ${variant === 'dark' ? 'text-gray-400' : 'text-muted'}`}>
                            Protecting Nigerians, One Scan at a Time
                        </p>
                    </div>

                    {/* Center: Quick Links */}
                    <div className="flex flex-col items-center space-y-4">
                        <h3 className="font-syne font-bold uppercase tracking-wider text-sm text-primary">Quick Links</h3>
                        <nav className="flex flex-wrap justify-center gap-4 text-sm font-medium">
                            <Link to="/home" className={`flex items-center gap-1.5 transition-colors ${textMutedClasses}`}>
                                <Home className="w-4 h-4" /> Dashboard
                            </Link>
                            <Link to="/scan" className={`flex items-center gap-1.5 transition-colors ${textMutedClasses}`}>
                                <Shield className="w-4 h-4" /> Scan
                            </Link>
                            <Link to="/scan-history" className={`flex items-center gap-1.5 transition-colors ${textMutedClasses}`}>
                                <History className="w-4 h-4" /> History
                            </Link>
                            <Link to="/profile" className={`flex items-center gap-1.5 transition-colors ${textMutedClasses}`}>
                                <LifeBuoy className="w-4 h-4" /> Support
                            </Link>
                        </nav>
                    </div>

                    {/* Right: Badges */}
                    <div className="flex flex-col items-center md:items-end space-y-4">
                        <p className="font-mono text-sm uppercase tracking-wider text-primary">Powered by Sabi AI</p>
                        <div className={`flex items-center gap-3 px-4 py-2 border rounded-xl ${variant === 'dark' ? 'border-gray-800 bg-accent-2' : 'border-border bg-surface-2'}`}>
                            <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                                <span className="text-green-700 font-bold text-xs">NG</span>
                            </div>
                            <div className="text-left">
                                <p className="text-[10px] font-bold text-muted uppercase tracking-wider leading-none mb-1">In Partnership With</p>
                                <p className="text-sm font-bold leading-none">NAFDAC</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Bottom Section */}
                <div className={`pt-6 border-t flex flex-col md:flex-row justify-between items-center gap-4 text-xs ${variant === 'dark' ? 'border-gray-800' : 'border-border'}`}>
                    <p className={variant === 'dark' ? 'text-gray-500' : 'text-gray-400'}>
                        &copy; {currentYear} SabiLens. All rights reserved.
                    </p>
                    <div className="flex gap-6">
                        <Link to="/privacy" className={`transition-colors ${textMutedClasses}`}>Privacy Policy</Link>
                        <Link to="/terms" className={`transition-colors ${textMutedClasses}`}>Terms of Service</Link>
                    </div>
                </div>

            </div>
        </footer>
    );
};

export default Footer;
