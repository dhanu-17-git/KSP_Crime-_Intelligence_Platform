import React from 'react';
import { NavLink } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import {
  LayoutDashboard,
  Cpu,
  FolderLock,
  UserCheck,
  Car,
  Map,
  BarChart3,
  Network,
  FileSpreadsheet,
  Settings,
  ChevronLeft,
  ChevronRight,
  Shield
} from 'lucide-react';
import logo from '../assets/ksp-logo.jpeg';

export const Sidebar: React.FC = () => {
  const { sidebarCollapsed, setSidebarCollapsed, language } = useApp();

  const menuItems = [
    { path: '/', name: { en: 'Dashboard', kn: 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್' }, icon: LayoutDashboard },
    { path: '/ai-workspace', name: { en: 'AI Investigation', kn: 'ಎಐ ತನಿಖೆ' }, icon: Cpu },
    { path: '/cases', name: { en: 'Cases / FIRs', kn: 'ಪ್ರಕರಣಗಳು / ಎಫ್‌ಐಆರ್' }, icon: FolderLock },
    { path: '/suspects', name: { en: 'Suspects Database', kn: 'ಸಂದೇಹಾಸ್ಪದ ವ್ಯಕ್ತಿಗಳು' }, icon: UserCheck },
    { path: '/vehicles', name: { en: 'ANPR Vehicles', kn: 'ವಾಹನಗಳು (ANPR)' }, icon: Car },
    { path: '/map', name: { en: 'Crime Map', kn: 'ಅಪರಾಧ ನಕ್ಷೆ' }, icon: Map },
    { path: '/analytics', name: { en: 'Analytics', kn: 'ವಿಶ್ಲೇಷಣೆ' }, icon: BarChart3 },
    { path: '/network', name: { en: 'Criminal Network', kn: 'ಅಪರಾಧ ಜಾಲ' }, icon: Network },
    { path: '/reports', name: { en: 'Reports Builder', kn: 'ವರದಿಗಳು' }, icon: FileSpreadsheet },
    { path: '/settings', name: { en: 'System Settings', kn: 'ಸಿಸ್ಟಮ್ ಸೆಟ್ಟಿಂಗ್ಗಳು' }, icon: Settings },
  ];

  return (
    <aside
      className={`bg-brand-primary text-white flex flex-col justify-between border-r border-slate-800 transition-all duration-300 ${
        sidebarCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Header Logo */}
      <div>
        <div className="h-16 flex items-center px-3 gap-3 border-b border-slate-800">
          <img
            src={logo}
            alt="Karnataka Police Logo"
            className="w-10 h-10 object-cover rounded-full border border-brand-secondary/40 shrink-0"
          />
          {!sidebarCollapsed && (
            <div className="flex flex-col select-none">
              <span className="text-xs font-semibold text-brand-secondary uppercase tracking-wider">
                {language === 'en' ? 'Karnataka Police' : 'ಕರ್ನಾಟಕ ಪೊಲೀಸ್'}
              </span>
              <span className="text-[10px] text-slate-400 font-mono tracking-tight leading-none mt-0.5">
                {language === 'en' ? 'Crime Intel Platform' : 'ಅಪರಾಧ ಇಂಟೆಲಿಜೆನ್ಸ್'}
              </span>
            </div>
          )}
        </div>

        {/* Officer Profile Card */}
        {!sidebarCollapsed ? (
          <div className="p-4 mx-3 my-4 bg-brand-primary-light border border-slate-700/50 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-brand-secondary text-brand-primary font-bold flex items-center justify-center shrink-0">
                RK
              </div>
              <div className="overflow-hidden">
                <h4 className="text-sm font-medium text-slate-100 truncate">Rajesh Kumar</h4>
                <p className="text-xs text-brand-secondary font-semibold">Inspector of Police</p>
              </div>
            </div>
            <div className="mt-3 pt-2 border-t border-slate-700/60 flex flex-col gap-1">
              <span className="text-[10px] text-slate-400 font-mono">
                Badge: <span className="text-slate-200">KSP-9432</span>
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                PS: <span className="text-slate-200">Koramangala (City)</span>
              </span>
              <div className="flex items-center gap-1.5 mt-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-[9px] text-emerald-400 uppercase tracking-widest font-bold">Shift Active</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="my-4 flex justify-center">
            <div className="w-8 h-8 rounded-full bg-brand-secondary text-brand-primary font-bold flex items-center justify-center text-xs cursor-pointer" title="Inspector Rajesh Kumar">
              RK
            </div>
          </div>
        )}

        {/* Navigation Menu */}
        <nav className="flex flex-col gap-1 px-2 mt-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-all duration-150 ${
                    isActive
                      ? 'bg-brand-secondary text-brand-primary font-semibold'
                      : 'text-slate-300 hover:bg-brand-primary-light hover:text-white'
                  }`
                }
                title={sidebarCollapsed ? item.name[language] : undefined}
              >
                <Icon className="w-5 h-5 shrink-0" />
                {!sidebarCollapsed && <span className="truncate">{item.name[language]}</span>}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="border-t border-slate-800 p-3">
        {!sidebarCollapsed ? (
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
              <span className="flex items-center gap-1">
                <Shield className="w-3 h-3 text-brand-secondary" /> SECURE NET
              </span>
              <span className="text-emerald-400 font-semibold">ONLINE</span>
            </div>
            <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
              <span>DB SYNC</span>
              <span>LATEST</span>
            </div>
            <button
              onClick={() => setSidebarCollapsed(true)}
              className="mt-2 w-full py-1 bg-brand-primary-light hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white rounded flex items-center justify-center gap-1.5 transition-all text-xs"
            >
              <ChevronLeft className="w-4 h-4" />
              Collapse Menu
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <button
              onClick={() => setSidebarCollapsed(false)}
              className="p-1.5 bg-brand-primary-light hover:bg-slate-800 border border-slate-800 rounded text-slate-400 hover:text-white transition-all"
              title="Expand menu"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
};
