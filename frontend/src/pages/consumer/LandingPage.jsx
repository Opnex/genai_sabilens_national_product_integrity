import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  CheckCircle, MapPin, Database, Play, ShieldAlert, 
  Zap, Globe, Users, Building, ShieldCheck, ChevronRight,
  Scan, Mic, BarChart, Download
} from 'lucide-react';
import LandingHeader from '../../components/layout/LandingHeader';
import LandingFooter from '../../components/layout/LandingFooter';
import Button from '../../components/ui/Button';
import FeatureCard from '../../components/sections/FeatureCard';

const LandingPage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024 && window.location.pathname === '/') {
        navigate('/onboarding', { replace: true });
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [navigate]);

  return (
    <div className="min-h-screen bg-background font-sans selection:bg-primary/20 selection:text-primary-dark">
      <LandingHeader isTransparent={false} />

      {/* ── HERO SECTION ──────────────────────────── */}
      <section className="relative pt-20 pb-20 lg:pt-28 lg:pb-32 overflow-hidden bg-white">
        {/* Abstract Background Elements */}
        <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
          <div className="absolute -top-[20%] -right-[10%] w-[70%] h-[70%] rounded-full bg-primary/5 blur-[120px]" />
          <div className="absolute bottom-[10%] -left-[10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[100px]" />
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9InJnYmEoMCwgMCwgMCwgMC4wNSkiLz48L3N2Zz4=')] [mask-image:linear-gradient(to_bottom,white,transparent)] opacity-60" />
        </div>

        {/* Container with equal padding on both sides */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-8 items-center">

            {/* Left Column - Text */}
            <div className="max-w-2xl mx-auto lg:mx-0 text-center lg:text-left">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-light border border-primary/20 text-primary font-semibold text-sm mb-8 animate-fade-up">
                <ShieldCheck className="w-4 h-4" /> Nigeria's #1 AI Verification Platform
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-heading font-extrabold text-accent mb-6 animate-fade-up stagger-1 tracking-tight">
                <span className="block mb-3">Scan Any Product.</span>
                <span className="block mb-3">Know If It's Real —</span>
                <span className="text-primary relative inline-block">
                  Instantly.
                  <svg className="absolute w-full h-3 -bottom-2 left-0 text-primary/30" viewBox="0 0 100 10" preserveAspectRatio="none">
                    <path d="M0 5 Q 50 10 100 5" stroke="currentColor" strokeWidth="4" fill="none" />
                  </svg>
                </span>
              </h1>

              <p className="text-lg sm:text-xl text-muted mb-10 leading-relaxed animate-fade-up stagger-2 max-w-lg mx-auto lg:mx-0">
                SabiLens uses multimodal forensic AI to verify product authenticity in seconds. Protecting Nigerians from counterfeits — in your language.
              </p>

              <div className="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start mb-12 animate-fade-up stagger-3">
                <Link to="/role-select" className="w-full sm:w-auto">
                  <Button variant="primary" size="lg" className="w-full sm:w-auto text-lg px-8">
                    Start Scanning Free <ChevronRight className="w-5 h-5 ml-1" />
                  </Button>
                </Link>
                <button className="flex items-center justify-center gap-3 text-accent font-semibold hover:text-primary transition-all py-3 px-6 rounded-xl border-2 border-primary/30 hover:border-primary/60 bg-white/50 backdrop-blur-sm w-full sm:w-auto group">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-colors">
                    <Play className="w-4 h-4 fill-current ml-0.5" />
                  </div>
                  Watch How It Works
                </button>
              </div>

              <div className="flex items-center justify-center lg:justify-start gap-8 text-sm animate-fade-up stagger-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <MapPin className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <span className="font-heading font-bold text-2xl text-accent block">36</span>
                    <span className="text-muted">States Covered</span>
                  </div>
                </div>
                <div className="w-px h-10 bg-border" />
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <Globe className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <span className="font-heading font-bold text-2xl text-accent block">4</span>
                    <span className="text-muted">Languages</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column - Phone Mockup with Original Design Preserved */}
            <div className="relative hidden lg:block w-full max-w-md ml-auto animate-fade-up stagger-3">
              {/* Phone Frame Container - for proper popup positioning */}
              <div className="relative ml-auto w-[300px] h-[600px]">
                {/* Phone Frame - Original Design */}
                <div className="relative w-full h-full bg-accent rounded-[40px] border-[8px] border-accent shadow-2xl overflow-hidden z-10">
                  {/* iPhone Notch */}
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-6 bg-accent rounded-b-[16px] z-30" />

                  {/* Screen Content - Scanner Demo - Original */}
                  <div className="absolute inset-0 bg-accent-2 flex flex-col justify-between pt-12 pb-8 px-6">
                    <div className="flex justify-center z-20">
                      <div className="bg-primary/20 border border-primary/40 rounded-full px-3 py-1 flex items-center gap-2 shadow-[0_0_15px_rgba(0,135,83,0.3)]">
                        <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                        <span className="text-primary text-[10px] font-mono tracking-widest uppercase font-bold">Sabi AI Active</span>
                      </div>
                    </div>

                    {/* Viewfinder Context - Original */}
                    <div className="relative w-full aspect-square border-2 border-primary/30 rounded-2xl flex items-center justify-center overflow-hidden">
                      {/* Scanning Animation */}
                      <div className="absolute left-0 right-0 h-1 bg-primary/80 shadow-[0_0_15px_rgba(0,135,83,0.8)] z-20 animate-scan-line" />

                      {/* Viewfinder Corners */}
                      <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-primary rounded-tl-xl" />
                      <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-primary rounded-tr-xl" />
                      <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-primary rounded-bl-xl" />
                      <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-primary rounded-br-xl" />

                      {/* Placeholder content being scanned */}
                      <div className="w-3/4 h-3/4 border-2 border-white/10 rounded-xl bg-white/5 backdrop-blur-sm flex items-center justify-center relative z-10">
                        <div className="w-16 h-8 bg-white/20 rounded mb-4 animate-pulse" />
                        <div className="absolute bottom-4 left-4 right-4 h-2 bg-white/20 rounded animate-pulse" />
                      </div>
                    </div>

                    <div className="text-center">
                      <p className="text-white/60 text-sm font-sans mb-1">Align product packaging</p>
                      <p className="text-white text-base font-heading font-semibold">Hold steady to verify</p>
                    </div>
                  </div>
                </div>

                {/* Floating Cards - Positioned relative to phone container */}
                {/* Top Card */}
                <div className="absolute -left-36 top-24 z-20 animate-float">
                  <div className="bg-white p-4 rounded-xl shadow-card border border-border w-48 text-left">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      </div>
                      <span className="text-xs font-bold text-green-700 tracking-wide uppercase">Safe to Buy</span>
                    </div>
                    <p className="text-sm font-heading font-semibold text-accent leading-tight">Molfix Diapers Size 4</p>
                    <p className="text-xs text-muted mt-1">98% Authentic Match</p>
                  </div>
                </div>

                {/* Bottom Card */}
                <div className="absolute -left-40 bottom-32 z-20 animate-float [animation-delay:1.5s]">
                  <div className="bg-white p-4 rounded-xl shadow-card border border-border w-52 text-left">
                    <div className="flex items-center gap-2 mb-2">
                      <ShieldCheck className="w-5 h-5 text-primary" />
                      <span className="text-xs font-bold text-accent tracking-wide uppercase">NAFDAC Verified</span>
                    </div>
                    <p className="text-sm font-heading font-semibold text-accent leading-tight w-full truncate">Reg: A7-1234 · Authentic</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── TRUST BAR ─────────────────────────────── */}
      <section className="bg-background border-y border-border py-10 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm font-medium text-muted uppercase tracking-wider mb-8">
            Trusted by organisations protecting Nigerians
          </p>
          <div className="flex justify-center items-center gap-12 sm:gap-20 flex-wrap opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
            <ShieldCheck className="w-8 h-8 text-accent" />
            <span className="font-heading font-extrabold text-2xl text-accent tracking-tighter">NAFDAC</span>
            <span className="font-heading font-bold text-xl text-accent tracking-widest">SON</span>
            <span className="font-heading font-bold text-lg text-accent uppercase">FMITI</span>
            <div className="flex items-center gap-2">
              <Building className="w-6 h-6 text-accent" />
              <span className="font-heading font-bold text-lg text-accent">MAN</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── FEATURES SECTION ──────────────────────── */}
      <section id="features" className="py-24 bg-white relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16 animate-fade-up">
            <h3 className="text-primary font-heading font-bold tracking-widest uppercase text-sm mb-4">Features</h3>
            <h2 className="text-3xl md:text-5xl font-heading font-bold text-accent mb-6 leading-tight">Everything You Need to Stay Safe</h2>
            <p className="text-lg text-muted font-sans">
              State-of-the-art technology disguised as a simple camera app.
              SabiLens replaces uncertainty with instant verification.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<Scan className="text-primary w-6 h-6" />}
              title="2-Point Forensic Scan"
              description="Scan the front and back of any product. Our AI analyses packaging, fonts, holograms, and regulatory codes simultaneously."
              delay="stagger-1"
            />
            <FeatureCard
              icon={<Mic className="text-primary w-6 h-6" />}
              title="Voice Results in Your Language"
              description="Hear clear 'Buy' or 'Don't Buy' guidance in Yorùbá, Hausa, Igbo, or English — instantly after every scan."
              delay="stagger-2"
            />
            <FeatureCard
              icon={<ShieldCheck className="text-primary w-6 h-6" />}
              title="Live NAFDAC Cross-Check"
              description="Every scan is validated against NAFDAC's official product registry in real time. No guesswork — only facts."
              delay="stagger-3"
            />
            <FeatureCard
              icon={<MapPin className="text-primary w-6 h-6" />}
              title="Location-Locked Evidence"
              description="When a fake is found, SabiLens captures GPS coordinates, timestamp, and product images — ready for enforcement."
              delay="stagger-4"
            />
            <FeatureCard
              icon={<BarChart className="text-primary w-6 h-6" />}
              title="Brand Protection Dashboard"
              description="Manufacturers see real-time counterfeit hotspots, risk scores, and supply chain intelligence — all in one place."
              delay="stagger-5"
            />
            <FeatureCard
              icon={<Zap className="text-primary w-6 h-6" />}
              title="One-Tap NAFDAC Report"
              description="Submit evidence to NAFDAC in one tap. Automatic case ID, GPS attachment, and status tracking included."
              delay="stagger-5"
            />
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS SECTION ──────────────────── */}
      <section id="how-it-works" className="py-24 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-20 animate-fade-up">
            <h3 className="text-primary font-heading font-bold tracking-widest uppercase text-sm mb-4">Process</h3>
            <h2 className="text-3xl md:text-5xl font-heading font-bold text-accent mb-6">How It Works</h2>
            <p className="text-lg text-muted font-sans">
              Verify any physical product in three simple steps.
            </p>
          </div>

          <div className="relative">
            {/* Connecting Line Desktop */}
            <div className="hidden lg:block absolute top-[10%] left-[15%] right-[15%] h-px bg-border z-0 border-dashed border-2" />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 relative z-10">

              {/* Step 1 */}
              <div className="flex flex-col items-center text-center animate-fade-up stagger-1">
                <div className="w-16 h-16 rounded-2xl bg-primary text-white flex items-center justify-center font-heading font-bold text-2xl mb-8 shadow-glow">1</div>
                <div className="mb-6 w-full max-w-[280px] aspect-video bg-white rounded-2xl border border-border shadow-soft flex items-center justify-center p-4">
                  <div className="relative w-12 h-20 border-2 border-primary rounded-lg flex items-center justify-center">
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4/5 h-px bg-primary animate-scan-line" />
                  </div>
                </div>
                <h3 className="text-xl font-heading font-bold text-accent mb-3">Scan the Product</h3>
                <p className="text-muted font-sans text-sm px-4">Open SabiLens and scan the front and back of any product — food, medicine, cosmetics.</p>
              </div>

              {/* Step 2 */}
              <div className="flex flex-col items-center text-center animate-fade-up stagger-2">
                <div className="w-16 h-16 rounded-2xl bg-primary text-white flex items-center justify-center font-heading font-bold text-2xl mb-8 shadow-glow">2</div>
                <div className="mb-6 w-full max-w-[280px] aspect-video bg-white rounded-2xl border border-border shadow-soft flex items-center justify-center p-4">
                  <div className="relative">
                    <Database className="w-10 h-10 text-accent/20" />
                    <Zap className="w-8 h-8 text-primary absolute -right-4 -bottom-2" />
                  </div>
                </div>
                <h3 className="text-xl font-heading font-bold text-accent mb-3">AI Analyses in Seconds</h3>
                <p className="text-muted font-sans text-sm px-4">Our forensic AI checks packaging features, NAFDAC codes, batch numbers, and holograms.</p>
              </div>

              {/* Step 3 */}
              <div className="flex flex-col items-center text-center animate-fade-up stagger-3">
                <div className="w-16 h-16 rounded-2xl bg-primary text-white flex items-center justify-center font-heading font-bold text-2xl mb-8 shadow-glow">3</div>
                <div className="mb-6 w-full max-w-[280px] aspect-video bg-white rounded-2xl border border-border shadow-soft flex items-center justify-center p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    </div>
                    <div className="h-2 w-16 bg-border rounded-full" />
                  </div>
                </div>
                <h3 className="text-xl font-heading font-bold text-accent mb-3">Hear Your Safe Result</h3>
                <p className="text-muted font-sans text-sm px-4">Get instant voice guidance in your language. Safe products get a green pass. Fakes get flagged.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── USER TYPES SECTION ────────────────────── */}
      <section className="py-24 bg-accent text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4=')] [mask-image:radial-gradient(ellipse_at_center,white,transparent)]" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto mb-16 animate-fade-up">
            <h2 className="text-3xl md:text-5xl font-heading font-bold mb-6">Built for Everyone Protecting Nigeria</h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
            {/* Consumer Card */}
            <div className="bg-accent-2 border border-white/10 rounded-3xl p-8 flex flex-col hover:border-primary/50 transition-colors duration-300">
              <Users className="w-12 h-12 text-primary mb-6" />
              <h3 className="font-heading font-bold text-2xl mb-6">For Consumers</h3>
              <ul className="space-y-4 mb-10 flex-1 font-sans text-white/70">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span>Scan before you buy at any market</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span>Voice results in your native language</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span>Report fakes directly in one tap</span>
                </li>
              </ul>
              <Link to="/signup">
                <Button variant="outline" fullWidth className="border-primary/50 text-white hover:bg-primary/20 hover:text-white">Download App →</Button>
              </Link>
            </div>

            {/* Brands Card (Featured) */}
            <div className="bg-accent-2 border-2 border-primary rounded-3xl p-8 flex flex-col relative transform lg:-translate-y-4 shadow-glow">
              <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-primary text-white font-heading font-bold text-sm px-4 py-1 rounded-full uppercase tracking-wider">
                Most Popular
              </div>
              <Building className="w-12 h-12 text-primary mb-6" />
              <h3 className="font-heading font-bold text-2xl mb-6">For Brands</h3>
              <ul className="space-y-4 mb-10 flex-1 font-sans text-white/70">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span className="text-white">Real-time counterfeit intelligence reports</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span className="text-white">Heat maps by location and product SKU</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span className="text-white">Evidence vault for swift legal enforcement</span>
                </li>
              </ul>
              <Link to="/company/signup">
                <Button variant="primary" fullWidth className="shadow-none">Protect Your Brand →</Button>
              </Link>
            </div>

            {/* NAFDAC Card */}
            <div className="bg-accent-2 border border-white/10 rounded-3xl p-8 flex flex-col hover:border-primary/50 transition-colors duration-300">
              <ShieldAlert className="w-12 h-12 text-primary mb-6" />
              <h3 className="font-heading font-bold text-2xl mb-6">For NAFDAC Officers</h3>
              <ul className="space-y-4 mb-10 flex-1 font-sans text-white/70">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span>National counterfeit tracking dashboard</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span>Live alert feed by state and danger level</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span>Export comprehensive evidence packages</span>
                </li>
              </ul>
              <Link to="/nafdac/login">
                <Button variant="outline" fullWidth className="border-primary/50 text-white hover:bg-primary/20 hover:text-white">Access Dashboard →</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── TESTIMONIALS SECTION ──────────────────── */}
      <section className="bg-primary-light py-24 border-y border-primary/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* Testimonial 1 */}
            <div className="bg-white p-8 rounded-3xl shadow-soft relative flex flex-col justify-between">
              <div className="absolute top-8 right-8 text-primary/20 text-6xl font-heading font-bold leading-none">"</div>
              <p className="font-sans text-lg text-accent leading-relaxed italic mb-8 relative z-10">
                "SabiLens helped me avoid buying fake malaria medicine at Idumota market. The voice result in Yorùbá made it very clear."
              </p>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center font-heading font-bold text-primary text-xl">
                  A
                </div>
                <div>
                  <h4 className="font-heading font-bold text-accent">Adaeze O.</h4>
                  <p className="text-sm font-sans text-muted">Lagos Consumer</p>
                </div>
              </div>
            </div>

            {/* Testimonial 2 */}
            <div className="bg-white p-8 rounded-3xl shadow-soft relative flex flex-col justify-between">
              <div className="absolute top-8 right-8 text-primary/20 text-6xl font-heading font-bold leading-none">"</div>
              <p className="font-sans text-lg text-accent leading-relaxed italic mb-8 relative z-10">
                "We detected a counterfeit ring operating across 3 states within 48 hours of deploying SabiLens to our field officers."
              </p>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-accent rounded-full flex items-center justify-center font-heading font-bold text-white text-xl">
                  N
                </div>
                <div>
                  <h4 className="font-heading font-bold text-accent">NAFDAC Officer</h4>
                  <p className="text-sm font-sans text-muted">Kano State Field Agent</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── DOWNLOAD / CTA SECTION ────────────────── */}
      <section className="bg-accent py-24 relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl aspect-square bg-primary/20 rounded-full blur-[100px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="bg-accent-2 border border-white/10 rounded-[40px] p-10 lg:p-16 flex flex-col lg:flex-row items-center justify-between gap-12 overflow-hidden relative">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4=')] opacity-[0.03]" />

            <div className="max-w-xl text-center lg:text-left relative z-10">
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-heading font-bold text-white mb-6 leading-tight">
                Start Protecting Yourself Today
              </h2>
              <p className="font-sans text-lg text-white/60 mb-10">
                Join thousands of Nigerians verifying products before they buy. Registration takes less than a minute.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Link to="/role-select">
                  <Button variant="primary" size="lg" className="w-full sm:w-auto">Use Web App Free →</Button>
                </Link>
                <div className="flex gap-4">
                  <button className="h-[52px] px-4 border border-white/20 rounded-xl flex items-center gap-2 hover:bg-white/10 transition group">
                    <Download className="w-4 h-4 text-white/60 group-hover:text-white" />
                    <span className="font-sans text-white font-medium text-sm">App Store</span>
                  </button>
                  <button className="h-[52px] px-4 border border-white/20 rounded-xl flex items-center gap-2 hover:bg-white/10 transition group">
                    <Download className="w-4 h-4 text-white/60 group-hover:text-white" />
                    <span className="font-sans text-white font-medium text-sm">Google Play</span>
                  </button>
                </div>
              </div>
            </div>

            <div className="w-full max-w-sm lg:w-[400px] aspect-[4/3] bg-accent/50 rounded-2xl border border-white/5 flex items-center justify-center relative shadow-2xl z-10">
              <div className="w-64 h-auto bg-white rounded-2xl p-4 shadow-dark transform rotate-3 hover:rotate-0 transition-transform duration-500">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-heading font-bold text-accent text-sm">Product Authentic</h4>
                    <p className="font-sans text-xs text-muted">Scanned 2 mins ago</p>
                  </div>
                </div>
                <div className="h-2 w-full bg-surface-2 rounded-full mb-2" />
                <div className="h-2 w-3/4 bg-surface-2 rounded-full mb-4" />
                <div className="w-full py-2 bg-primary/10 text-primary font-heading font-bold text-xs text-center rounded-lg uppercase tracking-wider">
                  NAFDAC Verified
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <LandingFooter />
    </div>
  );
};

export default LandingPage;