import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import {
  Search,
  Bell,
  Globe2,
  LogOut,
  User,
  ShieldCheck,
  Calendar,
  Command,
  ShieldAlert,
  Cpu,
  FolderLock,
  Network,
  Lock
} from 'lucide-react';

export const Header: React.FC = () => {
  const { language, setLanguage, setAiQuery, addToast } = useApp();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [searchInput, setSearchInput] = useState('');
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [paletteSearch, setPaletteSearch] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setShowCommandPalette((prev) => !prev);
      }
      if (e.key === 'Escape') {
        setShowCommandPalette(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handlePaletteAction = (action: string) => {
    setShowCommandPalette(false);
    setPaletteSearch('');
    if (action === 'query-ka4421') {
      setAiQuery('Find all suspects connected with vehicle KA05MJ4421');
      addToast('Search parameter prefilled: KA05MJ4421', 'info');
      navigate('/ai-workspace');
    } else if (action === 'query-vikram') {
      setAiQuery('Find cases linked with suspect Vikram Hegde');
      addToast('Search parameter prefilled: Vikram Hegde', 'info');
      navigate('/ai-workspace');
    } else if (action === 'go-cases') {
      navigate('/cases');
    } else if (action === 'go-network') {
      navigate('/network');
    } else if (action === 'go-map') {
      navigate('/map');
    } else if (action === 'toggle-lang') {
      setLanguage(language === 'en' ? 'kn' : 'en');
      addToast(language === 'en' ? 'ಭಾಷೆಯನ್ನು ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗಿದೆ' : 'Language set to English', 'success');
    } else if (action === 'lock') {
      addToast('Terminal session secured and locked.', 'warn');
    }
  };

  const handlePaletteSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!paletteSearch.trim()) return;
    setAiQuery(paletteSearch);
    setShowCommandPalette(false);
    setPaletteSearch('');
    addToast(`Searching AI dossiers for "${paletteSearch}"`, 'info');
    navigate('/ai-workspace');
  };
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  const formatPathname = (path: string) => {
    if (path === '/') return language === 'en' ? 'Core Command Dashboard' : 'ಕೇಂದ್ರ ನಿಯಂತ್ರಣ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್';
    const clean = path.replace('/', '');
    const map: Record<string, string> = {
      'ai-workspace': language === 'en' ? 'AI Investigation Workspace' : 'ಎಐ ತನಿಖಾ ಕೊಠಡಿ',
      'cases': language === 'en' ? 'Cases Ledger' : 'ಪ್ರಕರಣಗಳ ಪಟ್ಟಿ',
      'suspects': language === 'en' ? 'Suspect Profile Registry' : 'ಸಂದೇಹಾಸ್ಪದ ವ್ಯಕ್ತಿಗಳ ದಾಖಲಾತಿ',
      'vehicles': language === 'en' ? 'ANPR Vehicle Track logs' : 'ವಾಹನ ಟ್ರ್ಯಾಕಿಂಗ್ ಲಾಗ್',
      'map': language === 'en' ? 'District Hotspot GIS Map' : 'ಅಪರಾಧ ನಕ್ಷೆ',
      'analytics': language === 'en' ? 'Crime Analytics & ECharts' : 'ಅಪರಾಧ ವಿಶ್ಲೇಷಣೆ',
      'network': language === 'en' ? 'Criminal Association Graph' : 'ಸಂಬಂಧಗಳ ನೆಟ್‌ವರ್ಕ್',
      'reports': language === 'en' ? 'Official Documents & Reports' : 'ಅಧಿಕೃತ ವರದಿಗಳು',
      'settings': language === 'en' ? 'System Controls' : 'ಸಿಸ್ಟಮ್ ಸೆಟ್ಟಿಂಗ್ಗಳು',
    };
    return map[clean] || clean;
  };

  const notifications = [
    { id: 1, title: 'ANPR Ping: KA05MJ4421', desc: 'Detected at Koramangala 80ft Road Junction CCTV.', time: '2 mins ago', severity: 'Critical' },
    { id: 2, title: 'New FIR Registered', desc: 'FIR 0142/2026 for armed robbery at Koramangala PS.', time: '10 mins ago', severity: 'Major' },
    { id: 3, title: 'Shift Handover Logged', desc: 'Day Shift handed over logs to Night Shift.', time: '1 hr ago', severity: 'Minor' },
  ];

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchInput.trim()) return;
    setAiQuery(searchInput);
    navigate('/ai-workspace');
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 relative z-30 select-none">
      {/* Left Breadcrumb Section */}
      <div className="flex items-center gap-3">
        <div className="w-1.5 h-6 bg-brand-primary rounded-full"></div>
        <div className="flex flex-col">
          <span className="text-[10px] text-slate-400 font-mono tracking-widest leading-none uppercase">
            {language === 'en' ? 'KARNATAKA POLICE FORCE' : 'ಕರ್ನಾಟಕ ಪೊಲೀಸ್ ಸೇವೆ'}
          </span>
          <span className="text-sm font-semibold text-brand-primary leading-tight mt-0.5">
            {formatPathname(location.pathname)}
          </span>
        </div>
      </div>

      {/* Middle Search Bar */}
      <form onSubmit={handleSearchSubmit} className="hidden md:flex items-center bg-slate-50 border border-slate-200 rounded-md w-96 px-3 py-1.5 focus-within:border-slate-400 focus-within:bg-white transition-all">
        <Search className="w-4 h-4 text-slate-400 shrink-0 mr-2" />
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder={language === 'en' ? 'Global Search (e.g. KA05MJ4421, Vikram)...' : 'ಜಾಗತಿಕ ಹುಡುಕಾಟ...'}
          className="bg-transparent border-none text-xs text-slate-800 focus:outline-none w-full placeholder-slate-400 font-sans"
        />
        <div className="flex items-center gap-0.5 ml-2 border border-slate-200 rounded bg-slate-100/80 px-1 py-0.5 text-[9px] text-slate-400 font-mono shrink-0">
          <Command className="w-2.5 h-2.5" />
          <span>K</span>
        </div>
      </form>

      {/* Right Controls Section */}
      <div className="flex items-center gap-4">
        {/* Language switch */}
        <button
          onClick={() => setLanguage(language === 'en' ? 'kn' : 'en')}
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded text-xs font-medium text-slate-700 transition-all cursor-pointer"
          title="Toggle language English/Kannada"
        >
          <Globe2 className="w-3.5 h-3.5 text-brand-primary" />
          <span>{language === 'en' ? 'English' : 'ಕನ್ನಡ'}</span>
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowProfile(false);
            }}
            className="p-2 text-slate-500 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-full transition-all relative cursor-pointer"
          >
            <Bell className="w-4.5 h-4.5" />
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-brand-accent border border-white animate-pulse"></span>
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-lg shadow-xl py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="px-4 py-2 border-b border-slate-100 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-800">Operational Alerts</span>
                <span className="text-[10px] text-brand-secondary font-semibold font-mono uppercase">Mission Critical</span>
              </div>
              <div className="max-h-60 overflow-y-auto">
                {notifications.map((n) => (
                  <div key={n.id} className="px-4 py-3 hover:bg-slate-50 border-b border-slate-50 last:border-b-0 cursor-pointer transition-colors">
                    <div className="flex items-center justify-between gap-2">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-bold leading-none ${
                        n.severity === 'Critical' ? 'bg-red-50 text-red-700' :
                        n.severity === 'Major' ? 'bg-orange-50 text-orange-700' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {n.severity}
                      </span>
                      <span className="text-[9px] text-slate-400 font-mono">{n.time}</span>
                    </div>
                    <h5 className="text-xs font-semibold text-slate-800 mt-1">{n.title}</h5>
                    <p className="text-[11px] text-slate-500 leading-normal mt-0.5">{n.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Officer Status Profile dropdown */}
        <div className="relative">
          <button
            onClick={() => {
              setShowProfile(!showProfile);
              setShowNotifications(false);
            }}
            className="flex items-center gap-2 p-1 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-lg cursor-pointer transition-all"
          >
            <div className="w-7 h-7 rounded bg-brand-primary text-brand-secondary font-bold flex items-center justify-center text-xs">
              RK
            </div>
            <div className="hidden lg:flex flex-col text-left pr-1.5 leading-none">
              <span className="text-xs font-semibold text-slate-800">Rajesh Kumar</span>
              <span className="text-[9px] text-slate-400 font-mono mt-0.5">Inspector KSP</span>
            </div>
          </button>

          {showProfile && (
            <div className="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-lg shadow-xl py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="px-4 py-2 border-b border-slate-100">
                <span className="text-[10px] text-slate-400 font-mono block">LOGGED TERMINAL</span>
                <span className="text-xs font-bold text-slate-800 block truncate mt-0.5">Koramangala Unit-A</span>
              </div>
              
              <button className="w-full text-left px-4 py-2 text-xs text-slate-700 hover:bg-slate-50 flex items-center gap-2 transition-colors">
                <User className="w-4 h-4 text-slate-400" /> My Activity Log
              </button>
              <button className="w-full text-left px-4 py-2 text-xs text-slate-700 hover:bg-slate-50 flex items-center gap-2 transition-colors">
                <ShieldCheck className="w-4 h-4 text-slate-400" /> Security Token Audit
              </button>
              <button className="w-full text-left px-4 py-2 text-xs text-slate-700 hover:bg-slate-50 flex items-center gap-2 transition-colors">
                <Calendar className="w-4 h-4 text-slate-400" /> Shift Records
              </button>
              
              <div className="border-t border-slate-100 mt-2 pt-2">
                <button className="w-full text-left px-4 py-2 text-xs text-red-600 hover:bg-red-50 flex items-center gap-2 transition-colors">
                  <LogOut className="w-4 h-4" /> Lock Secure Terminal
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ======================================================== */}
      {/* COMMAND PALETTE DIALOG OVERLAY */}
      {/* ======================================================== */}
      {showCommandPalette && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-start justify-center pt-[15vh] z-50 animate-in fade-in duration-200">
          <div className="absolute inset-0" onClick={() => setShowCommandPalette(false)} />
          
          <div className="relative bg-white w-[540px] max-w-[90vw] border border-slate-200 rounded-lg shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150 flex flex-col">
            <form onSubmit={handlePaletteSearchSubmit} className="flex items-center border-b border-slate-200 px-4 py-3 bg-slate-50">
              <Search className="w-5 h-5 text-slate-400 mr-3 shrink-0" />
              <input
                type="text"
                value={paletteSearch}
                onChange={(e) => setPaletteSearch(e.target.value)}
                placeholder="Search KSP records or type query..."
                className="bg-transparent border-none text-xs text-slate-800 focus:outline-none w-full placeholder-slate-400 font-sans"
                autoFocus
              />
              <span className="text-[9px] text-slate-400 font-mono border border-slate-200 rounded px-1.5 py-0.5 bg-white select-none">
                ESC
              </span>
            </form>

            <div className="max-h-72 overflow-y-auto p-2 flex flex-col gap-0.5">
              <span className="text-[9px] text-slate-400 font-mono tracking-widest px-3 py-1 uppercase font-semibold">
                Quick AI Prompts
              </span>
              <button
                onClick={() => handlePaletteAction('query-ka4421')}
                className="w-full text-left px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 hover:text-brand-primary rounded flex items-center gap-2.5 transition-colors cursor-pointer"
              >
                <Cpu className="w-4 h-4 text-brand-secondary" />
                <span>Search links for vehicle <span className="font-mono font-bold text-brand-primary">KA05MJ4421</span></span>
              </button>
              <button
                onClick={() => handlePaletteAction('query-vikram')}
                className="w-full text-left px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 hover:text-brand-primary rounded flex items-center gap-2.5 transition-colors cursor-pointer"
              >
                <Cpu className="w-4 h-4 text-brand-secondary" />
                <span>Search cases for suspect <span className="font-bold text-brand-primary">Vikram Hegde</span></span>
              </button>

              <div className="border-t border-slate-100 my-1" />

              <span className="text-[9px] text-slate-400 font-mono tracking-widest px-3 py-1 uppercase font-semibold">
                Navigation Shortcuts
              </span>
              <button
                onClick={() => handlePaletteAction('go-cases')}
                className="w-full text-left px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 hover:text-brand-primary rounded flex items-center gap-2.5 transition-colors cursor-pointer"
              >
                <FolderLock className="w-4 h-4 text-slate-400" />
                <span>Cases Ledger</span>
              </button>
              <button
                onClick={() => handlePaletteAction('go-network')}
                className="w-full text-left px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 hover:text-brand-primary rounded flex items-center gap-2.5 transition-colors cursor-pointer"
              >
                <Network className="w-4 h-4 text-slate-400" />
                <span>Criminal Network Graph</span>
              </button>
              <button
                onClick={() => handlePaletteAction('go-map')}
                className="w-full text-left px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 hover:text-brand-primary rounded flex items-center gap-2.5 transition-colors cursor-pointer"
              >
                <ShieldAlert className="w-4 h-4 text-slate-400" />
                <span>Crime GIS Map</span>
              </button>

              <div className="border-t border-slate-100 my-1" />

              <span className="text-[9px] text-slate-400 font-mono tracking-widest px-3 py-1 uppercase font-semibold">
                Quick Preferences
              </span>
              <button
                onClick={() => handlePaletteAction('toggle-lang')}
                className="w-full text-left px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 hover:text-brand-primary rounded flex items-center gap-2.5 transition-colors cursor-pointer"
              >
                <Globe2 className="w-4 h-4 text-slate-400" />
                <span>Toggle Language: English / Kannada</span>
              </button>
              <button
                onClick={() => handlePaletteAction('lock')}
                className="w-full text-left px-3 py-2 text-xs text-red-600 hover:bg-red-50 rounded flex items-center gap-2.5 transition-colors cursor-pointer"
              >
                <Lock className="w-4 h-4" />
                <span>Secure / Lock Terminal Session</span>
              </button>
            </div>
            
            <div className="border-t border-slate-150 p-2.5 bg-slate-50 flex items-center justify-between text-[10px] text-slate-400 font-mono select-none">
              <span>Use arrow keys to navigate lists</span>
              <span>Ctrl + K to toggle close</span>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
