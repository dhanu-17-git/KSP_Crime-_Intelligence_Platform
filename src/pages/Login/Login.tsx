import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import logo from '../../assets/ksp-logo.jpeg';
import { Lock, Globe2, Eye, EyeOff, Loader2 } from 'lucide-react';

const ConstellationSvg: React.FC = () => (
  <svg className="w-full h-[220px] text-slate-300 select-none" viewBox="0 0 400 220" fill="none" stroke="currentColor">
    {/* Grid backdrop */}
    <path d="M 50 0 L 50 220 M 100 0 L 100 220 M 150 0 L 150 220 M 200 0 L 200 220 M 250 0 L 250 220 M 300 0 L 300 220 M 350 0 L 350 220" stroke="#f1f5f9" strokeWidth="1" />
    <path d="M 0 30 L 400 30 M 0 75 L 400 75 M 0 120 L 400 120 M 0 165 L 400 165" stroke="#f1f5f9" strokeWidth="1" />
    
    {/* Network links */}
    <path d="M 120 60 L 200 40 L 280 100 L 200 170 L 120 60 Z" stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="3,3" />
    <path d="M 200 40 L 220 110 L 280 100 M 120 60 L 150 130 L 200 170" stroke="#94a3b8" strokeWidth="1.5" />
    <path d="M 150 130 L 220 110" stroke="#cbd5e1" strokeWidth="1" />
    
    {/* Station & suspect nodes */}
    <circle cx="120" cy="60" r="5" fill="#0B3D91" />
    <circle cx="200" cy="40" r="5" fill="#0B3D91" />
    <circle cx="280" cy="100" r="5" fill="#0B3D91" />
    <circle cx="200" cy="170" r="5" fill="#0B3D91" />
    <circle cx="220" cy="110" r="4" fill="#b89020" />
    <circle cx="150" cy="130" r="4" fill="#b89020" />
    
    {/* Orbit lines */}
    <circle cx="200" cy="100" r="70" stroke="#e2e8f0" strokeWidth="1" />
    <circle cx="200" cy="100" r="100" stroke="#f1f5f9" strokeWidth="1.5" strokeDasharray="5,5" />
  </svg>
);

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { language, setLanguage, setIsAuthenticated, addToast } = useApp();

  const [officerId, setOfficerId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberDevice, setRememberDevice] = useState(false);

  // Progressive verification checks states
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [authStepIndex, setAuthStepIndex] = useState(-1);
  const authSteps = [
    'Authenticating Officer...',
    'Verifying Credentials...',
    'Checking Security Clearance...',
    'Loading Intelligence Modules...',
    'Access Granted'
  ];

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!officerId.trim() || !password.trim()) {
      addToast(language === 'en' ? 'Please fill in all credentials.' : 'ದಯವಿಟ್ಟು ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ.', 'warn');
      return;
    }

    // Launch secure credentials checks pipeline
    setIsAuthenticating(true);
    setAuthStepIndex(0);

    let step = 0;
    const interval = setInterval(() => {
      if (step < authSteps.length - 1) {
        step++;
        setAuthStepIndex(step);
      } else {
        clearInterval(interval);
        setTimeout(() => {
          setIsAuthenticated(true);
          setIsAuthenticating(false);
          addToast(language === 'en' ? 'Terminal Session Opened.' : 'ಪ್ರವೇಶ ಅನುಮೋದಿಸಲಾಗಿದೆ.', 'success');
          navigate('/');
        }, 300);
      }
    }, 350); // resolving stages sequentially
  };

  const handleUseDemo = () => {
    setOfficerId('IPS001');
    setPassword('demo123');
    addToast(language === 'en' ? 'Demo credentials prefilled.' : 'ಡೆಮೊ ರುಜುವಾತುಗಳನ್ನು ಭರ್ತಿ ಮಾಡಲಾಗಿದೆ.', 'info');
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-[#F6F8FB] font-sans antialiased text-slate-800 relative">
      
      {/* 1. LANGUAGE SWITCH TOP BAR */}
      <header className="fixed top-0 left-0 w-full h-14 px-6 flex justify-end items-center z-40 select-none print:hidden">
        <button
          onClick={() => {
            setLanguage(language === 'en' ? 'kn' : 'en');
            addToast(language === 'en' ? 'ಭಾಷೆಯನ್ನು ಬದಲಾಯಿಸಲಾಗಿದೆ' : 'Language set to English', 'success');
          }}
          className="text-xs font-semibold text-slate-600 hover:text-brand-primary py-1 px-3 border border-slate-200 hover:border-slate-350 bg-white rounded flex items-center gap-1.5 transition-all cursor-pointer shadow-sm focus:ring-2 focus:ring-brand-primary/25"
        >
          <Globe2 className="w-3.5 h-3.5" />
          <span>{language === 'en' ? 'ಕನ್ನಡ' : 'English'}</span>
        </button>
      </header>

      {/* 2. SPLIT SCREEN WORKSPACE */}
      <main className="flex-1 flex flex-col lg:flex-row pt-14 pb-14 min-h-0 relative select-none">
        
        {/* LEFT PANEL: KSP Emblems & Illustration */}
        <section className="w-full lg:w-[40%] bg-white border-r border-slate-200 flex flex-col justify-between p-8 lg:p-12 min-h-0 relative">
          
          {/* Top Logo & Dept */}
          <div className="flex items-center gap-4">
            <img
              src={logo}
              alt="KSP Emblem"
              className="w-14 h-14 object-contain border border-slate-100 rounded shadow-xs"
            />
            <div>
              <h2 className="text-xs font-bold text-slate-500 font-mono tracking-widest leading-none uppercase">
                {language === 'en' ? 'Government of Karnataka' : 'ಕರ್ನಾಟಕ ಸರ್ಕಾರ'}
              </h2>
              <h1 className="text-sm font-extrabold text-brand-primary uppercase mt-1 leading-none">
                {language === 'en' ? 'Karnataka State Police' : 'ಕರ್ನಾಟಕ ರಾಜ್ಯ ಪೊಲೀಸ್'}
              </h1>
            </div>
          </div>

          {/* Central Titles & GIS illustration */}
          <div className="my-8 flex flex-col gap-6">
            <div>
              <h3 className="text-2xl font-black text-slate-800 tracking-tight leading-tight uppercase font-sans">
                {language === 'en' ? 'Crime Intelligence Platform' : 'ಅಪರಾಧ ಗುಪ್ತಚರ ವೇದಿಕೆ'}
              </h3>
              <p className="text-xs text-slate-500 font-sans mt-2">
                {language === 'en'
                  ? 'AI-Powered Spatial Investigation & Communication Syndicate Triangulation Workspace.'
                  : 'ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಆಧಾರಿತ ಪ್ರಾದೇಶಿಕ ತನಿಖೆ ಮತ್ತು ಸಂಪರ್ಕ ವಿಶ್ಲೇಷಣಾ ಕೇಂದ್ರ.'}
              </p>
            </div>
            
            {/* GIS / Constellation SVG */}
            <div className="bg-slate-50/50 border border-slate-150 rounded-lg p-2 overflow-hidden shadow-inner">
              <ConstellationSvg />
            </div>
          </div>

          {/* Footer security badges */}
          <div className="flex flex-wrap gap-2 text-[10px] font-mono text-slate-400">
            <span className="px-2 py-0.5 bg-slate-100 border border-slate-200 rounded">
              SECURE KSP-NET
            </span>
            <span className="px-2 py-0.5 bg-slate-100 border border-slate-200 rounded">
              AUTHORIZED USE ONLY
            </span>
            <span className="px-2 py-0.5 bg-slate-100 border border-slate-200 rounded">
              CLASS-A CLEARANCE
            </span>
          </div>

        </section>

        {/* RIGHT PANEL: Centered credentials form card */}
        <section className="w-full lg:w-[60%] flex items-center justify-center p-6 lg:p-12 relative min-h-0 bg-[#F6F8FB]">
          
          <div className="bg-white border border-slate-200 rounded-lg p-7 lg:p-9 shadow-lg w-full max-w-[460px] relative overflow-hidden transition-all duration-300">
            <div className="absolute top-0 left-0 w-full h-1 bg-brand-primary" />
            
            {/* Header */}
            <div className="border-b border-slate-100 pb-3 mb-6">
              <h3 className="text-sm font-mono tracking-wider text-slate-400 block uppercase">
                {language === 'en' ? 'Terminal Gateway' : 'ಪ್ರವೇಶ ದ್ವಾರ'}
              </h3>
              <h2 className="text-base font-extrabold text-slate-800 leading-none mt-1">
                {language === 'en' ? 'Officer Login Access' : 'ಅಧಿಕಾರಿಗಳ ಲಾಗಿನ್'}
              </h2>
              <p className="text-[11px] text-slate-500 mt-1.5 leading-normal">
                {language === 'en'
                  ? 'Sign in using your secure internal credentials.'
                  : 'ನಿಮ್ಮ ಅಧಿಕೃತ ಸಿಸ್ಟಮ್ ರುಜುವಾತುಗಳನ್ನು ಬಳಸಿಕೊಂಡು ಲಾಗಿನ್ ಮಾಡಿ.'}
              </p>
            </div>

            {/* Verification Loading Overlay state */}
            {isAuthenticating && (
              <div className="absolute inset-0 bg-white/95 z-35 flex flex-col items-center justify-center p-6 animate-in fade-in duration-200">
                <Loader2 className="w-8 h-8 text-brand-primary animate-spin" />
                <div className="mt-5 w-full max-w-[280px]">
                  {/* Stages items */}
                  <div className="flex flex-col gap-2.5 font-mono text-xs">
                    {authSteps.map((step, idx) => (
                      <div
                        key={idx}
                        className={`flex items-center gap-2 transition-all duration-200 ${
                          idx === authStepIndex ? 'text-brand-primary font-bold scale-105' :
                          idx < authStepIndex ? 'text-emerald-600' :
                          'text-slate-300'
                        }`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                          idx === authStepIndex ? 'bg-brand-primary animate-pulse' :
                          idx < authStepIndex ? 'bg-emerald-500' :
                          'bg-slate-200'
                        }`} />
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Login fields */}
            <form onSubmit={handleLoginSubmit} className="flex flex-col gap-4 text-xs">
              
              {/* Officer ID input */}
              <div className="flex flex-col gap-1">
                <label className="font-semibold text-slate-600">
                  {language === 'en' ? 'Officer ID / Badge number' : 'ಅಧಿಕಾರಿಯ ಗುರುತಿನ ಚೀಟಿ ಸಂಖ್ಯೆ'}
                </label>
                <input
                  type="text"
                  value={officerId}
                  onChange={(e) => setOfficerId(e.target.value)}
                  placeholder="e.g. IPS001"
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 hover:border-slate-300 focus:border-brand-primary focus:bg-white rounded outline-none transition-all focus:ring-2 focus:ring-brand-primary/10 font-mono"
                  required
                />
              </div>

              {/* Password input */}
              <div className="flex flex-col gap-1">
                <div className="flex justify-between items-center">
                  <label className="font-semibold text-slate-600">
                    {language === 'en' ? 'Access Password' : 'ಪಾಸ್‌ವರ್ಡ್'}
                  </label>
                  <button
                    type="button"
                    onClick={() => handleUseDemo()}
                    className="text-[10px] text-brand-secondary font-bold hover:underline cursor-pointer font-sans uppercase"
                  >
                    {language === 'en' ? 'Use Demo Credentials' : 'ಡೆಮೊ ವಿವರ ಬಳಸಿ'}
                  </button>
                </div>
                <div className="relative flex items-center">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full p-2.5 pr-10 bg-slate-50 border border-slate-200 hover:border-slate-300 focus:border-brand-primary focus:bg-white rounded outline-none transition-all focus:ring-2 focus:ring-brand-primary/10 font-mono"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 text-slate-400 hover:text-slate-600 p-0.5 rounded cursor-pointer"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Extra checkboxes */}
              <div className="flex items-center justify-between text-[11px] text-slate-500 select-none">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberDevice}
                    onChange={(e) => setRememberDevice(e.target.checked)}
                    className="rounded border-slate-300 text-brand-primary focus:ring-brand-primary"
                  />
                  <span>{language === 'en' ? 'Remember this terminal' : 'ಈ ಸಾಧನವನ್ನು ನೆನಪಿಡಿ'}</span>
                </label>
                <button
                  type="button"
                  onClick={() => addToast(language === 'en' ? 'Contact secure administrator for credential reissue.' : 'ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸಲು ಸಿಸ್ಟಮ್ ನಿರ್ವಾಹಕರನ್ನು ಸಂಪರ್ಕಿಸಿ.', 'info')}
                  className="font-semibold text-slate-450 hover:text-slate-700 hover:underline cursor-pointer"
                >
                  {language === 'en' ? 'Forgot Password?' : 'ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿದೆಯೇ?'}
                </button>
              </div>

              {/* Buttons Actions */}
              <div className="flex flex-col gap-2 mt-2">
                <button
                  type="submit"
                  className="w-full bg-brand-primary hover:bg-brand-primary-light text-white font-bold text-xs py-3 rounded flex items-center justify-center gap-1.5 transition-colors cursor-pointer shadow-sm"
                >
                  <Lock className="w-4 h-4 text-brand-secondary" />
                  <span>{language === 'en' ? 'SECURE PORTAL LOGIN' : 'ಸುರಕ್ಷಿತ ಪ್ರವೇಶ ಲಾಗಿನ್'}</span>
                </button>
              </div>

            </form>

            {/* Demo boxes details */}
            <div className="mt-6 pt-5 border-t border-slate-100 flex flex-col gap-2 text-[10px] select-text">
              <span className="text-slate-400 font-semibold font-mono tracking-wider block uppercase leading-none">
                Authorized Credentials for Review
              </span>
              <div className="bg-slate-50 border border-slate-200 rounded p-2.5 font-mono text-slate-550 flex items-center justify-between flex-wrap gap-2 leading-none">
                <div>
                  <span className="text-slate-400 font-bold block uppercase text-[8px]">OFFICER ID:</span>
                  <span className="text-brand-primary font-bold block mt-1">IPS001</span>
                </div>
                <div>
                  <span className="text-slate-400 font-bold block uppercase text-[8px]">SECURE PW:</span>
                  <span className="text-brand-primary font-bold block mt-1">demo123</span>
                </div>
                <button
                  onClick={() => handleUseDemo()}
                  className="py-1 px-2 border border-slate-200 hover:bg-slate-100 rounded text-slate-600 font-sans font-bold transition-all cursor-pointer shadow-xs ml-auto"
                >
                  Prefill Fields
                </button>
              </div>
            </div>

          </div>

        </section>

      </main>

      {/* 3. SECURE BASE FOOTER */}
      <footer className="fixed bottom-0 left-0 w-full h-10 px-6 bg-white border-t border-slate-200 flex justify-between items-center text-[10px] font-mono text-slate-400 z-40 select-none print:hidden">
        <span>Crime Intelligence Platform v1.0</span>
        <span className="hidden md:inline">Government of Karnataka | Karnataka State Police</span>
        <span>Datathon 2026 Prototype</span>
      </footer>

    </div>
  );
};
export default Login;
