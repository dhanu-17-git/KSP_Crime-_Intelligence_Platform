import React from 'react';
import { useApp } from '../../context/AppContext';
import { User, Shield, ShieldCheck, Mail, Phone, Calendar, Clock, Award } from 'lucide-react';

export const Profile: React.FC = () => {
  const { language } = useApp();

  const officerTasks = [
    { id: 1, text: 'Complete shift briefing logs with Day-Shift Inspectors.', done: true },
    { id: 2, text: 'Review and sign FIR 0142/2026 robbery ledger entry.', done: true },
    { id: 3, text: 'Issue Lookout Circular (LOC) alert for Vikram Hegde.', done: false },
    { id: 4, text: 'Conduct briefing on ANPR target hits with patrol unit.', done: false },
  ];

  return (
    <div className="p-6 flex flex-col gap-6 max-w-[1200px] mx-auto select-none">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <User className="w-5 h-5 text-brand-primary" />
            <h1 className="text-sm font-bold text-brand-primary uppercase tracking-wider">
              {language === 'en' ? 'Officer Command Profile' : 'ಅಧಿಕಾರಿಯ ವಿವರಗಳು'}
            </h1>
          </div>
          <p className="text-xs text-slate-500 font-sans mt-1">
            Browse registered ranks, credentials, assigned precincts, shift duties, and action rosters.
          </p>
        </div>
      </div>

      {/* Grid Content */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Column: Profile Card */}
        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm flex flex-col items-center text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1.5 bg-brand-primary" />
          <div className="w-24 h-24 rounded-full bg-brand-secondary text-brand-primary font-bold text-4xl flex items-center justify-center border-4 border-slate-50 shadow-inner mt-4">
            RK
          </div>
          <h2 className="text-base font-bold text-slate-800 mt-4 leading-none">Rajesh Kumar</h2>
          <span className="text-xs text-brand-secondary font-semibold mt-1">Inspector of Police</span>
          <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 font-mono text-[9px] font-bold rounded uppercase mt-2 border border-emerald-200 leading-none">
            Active Duty
          </span>

          {/* Details list */}
          <div className="w-full mt-6 pt-6 border-t border-slate-100 flex flex-col gap-3 text-xs text-left font-sans text-slate-600">
            <div className="flex items-center gap-2">
              <Award className="w-4 h-4 text-brand-primary shrink-0" />
              <span>Badge No: <span className="font-bold text-slate-800">KSP-9432</span></span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-brand-primary shrink-0" />
              <span>Precinct: <span className="font-bold text-slate-800">Koramangala, Bengaluru City</span></span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-brand-primary shrink-0" />
              <span>Email: <span className="font-bold text-slate-800">rajesh.k@ksp.gov.in</span></span>
            </div>
            <div className="flex items-center gap-2">
              <Phone className="w-4 h-4 text-brand-primary shrink-0" />
              <span>Radio Comm: <span className="font-mono font-bold text-slate-800">Sector-5 (CH-8)</span></span>
            </div>
          </div>
        </div>

        {/* Middle Column: Duty Shift & Tasks */}
        <div className="md:col-span-2 flex flex-col gap-6">
          
          {/* Duty details */}
          <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm">
            <div className="border-b border-slate-100 pb-2 mb-4 flex items-center gap-2">
              <Clock className="w-4.5 h-4.5 text-brand-secondary" />
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Shift Roster Assignments</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-3 bg-slate-50 border border-slate-150 rounded flex flex-col gap-1">
                <span className="text-[9px] text-slate-400 font-mono uppercase">CURRENT ROTATION</span>
                <span className="font-bold text-slate-800 flex items-center gap-1">
                  <Calendar className="w-4 h-4 text-slate-500" /> Night Patrol Duty
                </span>
                <span className="text-slate-500 mt-1 font-mono text-[10px]">Duty Period: 20:00 - 08:00 IST</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-150 rounded flex flex-col gap-1">
                <span className="text-[9px] text-slate-400 font-mono uppercase">SECURITY CLEARANCE</span>
                <span className="font-bold text-slate-800 flex items-center gap-1">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" /> Class II clearance
                </span>
                <span className="text-slate-500 mt-1 text-[10px]">Access Level: State Intelligence Vault</span>
              </div>
            </div>
          </div>

          {/* Action Tasks */}
          <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm">
            <div className="border-b border-slate-100 pb-2 mb-4 flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Duty Operations Checklist</h3>
              <span className="text-[10px] text-brand-secondary font-semibold font-mono">2 / 4 COMPLETED</span>
            </div>

            <div className="flex flex-col gap-3 font-sans">
              {officerTasks.map((t) => (
                <div key={t.id} className="flex gap-3 items-start text-xs leading-normal">
                  <input
                    type="checkbox"
                    checked={t.done}
                    readOnly
                    className="mt-0.5 rounded border-slate-300 text-brand-primary focus:ring-brand-primary shrink-0"
                  />
                  <span className={`font-medium ${t.done ? 'line-through text-slate-400' : 'text-slate-700'}`}>
                    {t.text}
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};
export default Profile;
