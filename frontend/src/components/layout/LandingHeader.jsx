import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, Globe, ChevronDown } from 'lucide-react';
import Button from '../ui/Button';
import SabiLensLogo from '../../assets/SabiLens_Logo.png';

const LandingHeader = ({ isTransparent = false }) => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [isAtTop, setIsAtTop] = useState(true);
    const location = useLocation();
    const navigate = useNavigate();

    // Handle scroll detection for sticky header
    useEffect(() => {
        const handleScroll = () => {
            const scrolled = window.scrollY > 20;
            setIsScrolled(scrolled);
            setIsAtTop(window.scrollY < 10);
        };

        // Set initial state immediately
        handleScroll();

        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    // Close mobile menu on route change
    useEffect(() => {
        setMobileMenuOpen(false);
    }, [location.pathname]);

    const navLinks = [
        { name: 'Features', href: '/#features' },
        { name: 'How It Works', href: '/#how-it-works' },
        { name: 'For Business', href: '/company/signup' },
        { name: 'For NAFDAC', href: '/nafdac/login' },
        { name: 'Pricing', href: '/#pricing' },
    ];

    const handleNavClick = (e, href) => {
        e.preventDefault();
        if (href.startsWith('/#')) {
            const section = href.substring(2);
            if (location.pathname !== '/') {
                navigate('/', { state: { scrollTo: section } });
            } else {
                const element = document.getElementById(section);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth' });
                }
            }
        } else {
            navigate(href);
        }
        setMobileMenuOpen(false);
    };

    // Determine header styles
    const shouldBeTransparent = isTransparent && isAtTop;
    const headerBg = shouldBeTransparent ? 'bg-transparent' : 'bg-white/95 backdrop-blur-md';
    const headerShadow = !shouldBeTransparent ? 'shadow-[0_4px_20px_rgba(0,0,0,0.08)]' : '';
    const headerBorder = !shouldBeTransparent ? 'border-b border-border/80' : '';
    
    const logoColor = shouldBeTransparent ? 'text-white' : 'text-accent';
    const navLinkColor = shouldBeTransparent ? 'text-white/90 hover:text-white' : 'text-accent hover:text-primary';
    const buttonColor = shouldBeTransparent ? 'text-white hover:text-white hover:bg-white/10' : '';

    return (
        <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${headerBg} ${headerShadow} ${headerBorder}`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-20">

                    {/* Logo (Left) - Using PNG from assets */}
                    <div className="flex-shrink-0 flex items-center">
                        <Link to="/" className="flex items-center gap-2 group">
                            <img 
                                src={SabiLensLogo} 
                                alt="SabiLens" 
                                className="h-8 w-auto group-hover:scale-110 transition-transform" 
                            />
                            <span className={`font-syne font-bold text-2xl tracking-tight transition-colors ${logoColor}`}>
                                Sabi<span className="text-primary">Lens</span>
                            </span>
                        </Link>
                    </div>

                    {/* Desktop Navigation (Center) */}
                    <nav className="hidden lg:flex items-center space-x-8">
                        {navLinks.map((link) => (
                            <a
                                key={link.name}
                                href={link.href}
                                onClick={(e) => handleNavClick(e, link.href)}
                                className={`font-sans font-medium text-[15px] transition-all relative after:absolute after:bottom-0 after:left-0 after:w-0 after:h-0.5 after:bg-primary hover:after:w-full after:transition-all after:duration-300 pb-1 ${navLinkColor}`}
                            >
                                {link.name}
                            </a>
                        ))}
                    </nav>

                    {/* Desktop Actions (Right) */}
                    <div className="hidden lg:flex items-center space-x-4">
                        <div className="relative group flex items-center gap-1 cursor-pointer">
                            <Globe className={`w-5 h-5 ${navLinkColor}`} />
                            <ChevronDown className={`w-4 h-4 ${navLinkColor}`} />
                            <div className="absolute top-full right-0 mt-2 w-32 bg-white rounded-xl shadow-card opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all pointer-events-none group-hover:pointer-events-auto flex flex-col overflow-hidden border border-border">
                                <button className="px-4 py-2 text-sm text-left hover:bg-surface-2 text-accent font-medium">English</button>
                                <button className="px-4 py-2 text-sm text-left hover:bg-surface-2 text-accent">Yorùbá</button>
                                <button className="px-4 py-2 text-sm text-left hover:bg-surface-2 text-accent">Hausa</button>
                                <button className="px-4 py-2 text-sm text-left hover:bg-surface-2 text-accent">Igbo</button>
                            </div>
                        </div>

                        <Link to="/login">
                            <Button variant="ghost" className={buttonColor}>
                                Log In
                            </Button>
                        </Link>
                        <Link to="/role-select">
                            <Button variant="primary">Get Started Free</Button>
                        </Link>
                    </div>

                    {/* Mobile menu button */}
                    <div className="flex items-center lg:hidden">
                        <button
                            type="button"
                            className={`inline-flex items-center justify-center p-2 rounded-md focus:outline-none transition-colors ${
                                shouldBeTransparent 
                                    ? 'text-white hover:bg-white/10' 
                                    : 'text-muted hover:text-accent hover:bg-surface-2'
                            }`}
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        >
                            <span className="sr-only">Open main menu</span>
                            {mobileMenuOpen ? (
                                <X className="block h-6 w-6" aria-hidden="true" />
                            ) : (
                                <Menu className="block h-6 w-6" aria-hidden="true" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu Drawer */}
            <div
                className={`fixed inset-0 z-40 bg-accent/40 backdrop-blur-sm transition-opacity lg:hidden ${
                    mobileMenuOpen ? 'opacity-100 visible' : 'opacity-0 invisible pointer-events-none'
                }`}
                onClick={() => setMobileMenuOpen(false)}
            />

            <div
                className={`fixed top-0 right-0 z-50 w-full max-w-sm h-screen bg-white shadow-[-10px_0_30px_rgba(0,0,0,0.1)] transition-transform duration-300 ease-in-out lg:hidden flex flex-col ${
                    mobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
                }`}
            >
                <div className="flex items-center justify-between px-6 py-6 border-b border-border">
                    {/* Mobile logo - Using PNG from assets */}
                    <Link to="/" className="flex items-center gap-2" onClick={() => setMobileMenuOpen(false)}>
                        <img 
                            src={SabiLensLogo} 
                            alt="SabiLens" 
                            className="h-7 w-auto" 
                        />
                        <span className="font-syne font-bold text-xl tracking-tight text-accent">
                            Sabi<span className="text-primary">Lens</span>
                        </span>
                    </Link>
                    <button
                        onClick={() => setMobileMenuOpen(false)}
                        className="p-2 text-muted hover:bg-surface-2 rounded-full transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto py-6 px-6">
                    <nav className="flex flex-col space-y-6">
                        {navLinks.map((link) => (
                            <a
                                key={link.name}
                                href={link.href}
                                onClick={(e) => handleNavClick(e, link.href)}
                                className="font-syne font-semibold text-lg text-accent hover:text-primary transition-colors"
                            >
                                {link.name}
                            </a>
                        ))}
                    </nav>

                    <div className="mt-8 pt-8 border-t border-border">
                        <div className="flex items-center gap-3 mb-6 text-accent">
                            <Globe className="w-5 h-5 text-muted" />
                            <select className="bg-transparent text-base font-medium focus:outline-none flex-1 font-sans">
                                <option value="en">English</option>
                                <option value="yo">Yorùbá</option>
                                <option value="ha">Hausa</option>
                                <option value="ig">Igbo</option>
                            </select>
                        </div>

                        <div className="flex flex-col gap-4">
                            <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                                <Button variant="outline" fullWidth>Log In</Button>
                            </Link>
                            <Link to="/signup" onClick={() => setMobileMenuOpen(false)}>
                                <Button variant="primary" fullWidth>Get Started Free</Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default LandingHeader;