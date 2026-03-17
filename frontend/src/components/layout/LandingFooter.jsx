import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Twitter, Linkedin, Instagram, Youtube, Globe } from 'lucide-react';

const LandingFooter = () => {
    return (
        <footer className="bg-accent text-white pt-20 pb-8 rounded-t-[40px] mt-[-20px] relative z-10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-12 lg:gap-8 mb-16">

                    {/* Column 1 - Brand */}
                    <div className="lg:col-span-4 flex flex-col">
                        <Link to="/" className="flex items-center gap-2 mb-6 group inline-flex max-w-max">
                            <ShieldCheck className="text-primary w-8 h-8 group-hover:scale-110 transition-transform" />
                            <span className="font-syne font-bold text-2xl tracking-tight text-white">
                                Sabi<span className="text-primary">Lens</span>
                            </span>
                        </Link>
                        <p className="text-muted text-base leading-relaxed mb-6 max-w-xs font-sans">
                            "Protecting Nigerians,<br />One Scan at a Time"
                        </p>
                        <div className="flex gap-4 items-center">
                            <a href="#" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-white/70 hover:bg-primary hover:text-white transition-all">
                                <Twitter className="w-5 h-5" />
                            </a>
                            <a href="#" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-white/70 hover:bg-primary hover:text-white transition-all">
                                <Linkedin className="w-5 h-5" />
                            </a>
                            <a href="#" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-white/70 hover:bg-primary hover:text-white transition-all">
                                <Instagram className="w-5 h-5" />
                            </a>
                            <a href="#" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-white/70 hover:bg-primary hover:text-white transition-all">
                                <Youtube className="w-5 h-5" />
                            </a>
                        </div>
                        <p className="mt-6 text-sm text-white/40 font-mono">Made with ❤️ for Nigeria</p>
                    </div>

                    {/* Column 2 - Product */}
                    <div className="lg:col-span-2">
                        <h4 className="font-mono text-primary uppercase text-sm font-semibold tracking-wider mb-6">Product</h4>
                        <ul className="space-y-4">
                            <li><a href="/#features" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Features</a></li>
                            <li><a href="/#how-it-works" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">How It Works</a></li>
                            <li><a href="/#pricing" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Pricing</a></li>
                            <li><a href="#" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Download App</a></li>
                            <li><a href="#" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Changelog</a></li>
                            <li><a href="#" className="text-white/60 hover:text-primary transition-colors text-sm font-sans flex items-center gap-2">API <span className="bg-primary/20 text-primary text-[10px] px-2 py-0.5 rounded-full uppercase tracking-widest font-mono">beta</span></a></li>
                        </ul>
                    </div>

                    {/* Column 3 - Company */}
                    <div className="lg:col-span-3">
                        <h4 className="font-mono text-primary uppercase text-sm font-semibold tracking-wider mb-6">Company</h4>
                        <ul className="space-y-4">
                            <li><Link to="/about" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">About SabiLens</Link></li>
                            <li><a href="#" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Our Mission</a></li>
                            <li><a href="#" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Press Kit</a></li>
                            <li><a href="#" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Careers</a></li>
                            <li><a href="#" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Blog</a></li>
                            <li><a href="#" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Contact</a></li>
                        </ul>
                    </div>

                    {/* Column 4 - Regulatory */}
                    <div className="lg:col-span-3">
                        <h4 className="font-mono text-primary uppercase text-sm font-semibold tracking-wider mb-6">Regulatory</h4>
                        <ul className="space-y-4">
                            <li><a href="/nafdac/login" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">NAFDAC Partnership</a></li>
                            <li><a href="#" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">SON Compliance</a></li>
                            <li><Link to="/privacy-policy" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Privacy Policy</Link></li>
                            <li><Link to="/terms-of-service" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Terms of Service</Link></li>
                            <li><a href="#" className="text-white/60 hover:text-primary transition-colors text-sm font-sans">Data Protection (NDPR)</a></li>
                        </ul>
                    </div>

                </div>

                {/* Bottom Bar */}
                <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-sm text-white/40 font-sans">
                        © {new Date().getFullYear()} SabiLens Technologies Ltd. All rights reserved.
                    </p>

                    <div className="flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-white/30" />
                        <p className="text-sm text-white/40 font-sans font-medium">Powered by Sabi AI Engine</p>
                    </div>

                    <div className="flex items-center gap-2 text-white/50 bg-white/5 px-3 py-1.5 rounded-lg border border-white/10 cursor-pointer hover:bg-white/10 hover:text-white transition-all">
                        <Globe className="w-4 h-4" />
                        <span className="text-sm font-sans font-medium">EN</span>
                        <span className="opacity-40">|</span>
                        <span className="text-sm font-sans font-medium opacity-60 hover:opacity-100">YO</span>
                        <span className="opacity-40">|</span>
                        <span className="text-sm font-sans font-medium opacity-60 hover:opacity-100">HA</span>
                        <span className="opacity-40">|</span>
                        <span className="text-sm font-sans font-medium opacity-60 hover:opacity-100">IG</span>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default LandingFooter;
