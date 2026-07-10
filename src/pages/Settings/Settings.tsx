import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Settings, Shield, Sliders, Database, History } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { language, setLanguage } = useApp();

  // Settings State
  const [anprConfidence, setAnprConfidence] = useState(95);
  const [livePings, setLivePings] = useState(true);
  const [soundAlerts, setSoundAlerts] = useState(false);

  return (
    <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto select-none">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-brand-primary" />
            <h1 className="text-sm font-bold text-brand-primary uppercase tracking-wider">
              {language === 'en' ? 'System Controls & Configurations' : 'ಸಿಸ್ಟಮ್ ಸೆಟ್ಟಿಂಗ್ಗಳು'}
            </h1>
          </div>
          <p className="text-xs text-slate-500 font-sans mt-1">
            Manage terminal thresholds, telemetry alerts, active database sockets, and audit logs.
          </p>
        </div>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Card 1: ANPR Sensitivity Sliders */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col gap-4">
          <div className="border-b border-slate-100 pb-2 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-brand-secondary" />
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">ANPR & Alert Sensitivity</h3>
          </div>

          <div className="flex flex-col gap-4 text-xs">
            {/* Range slider */}
            <div className="flex flex-col gap-2">
              <div className="flex justify-between font-semibold text-slate-600">
                <span>ANPR Camera Reading Confidence Threshold</span>
                <span className="font-mono text-brand-primary">{anprConfidence}%</span>
              </div>
              <input
                type="range"
                min="70"
                max="100"
                value={anprConfidence}
                onChange={(e) => setAnprConfidence(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-primary"
              />
              <p className="text-[10px] text-slate-400">
                Determines character recognition accuracy before issuing lookup warnings to highway interceptors.
              </p>
            </div>

            {/* Toggle 1 */}
            <div className="flex justify-between items-center py-2 border-t border-slate-50">
              <div>
                <span className="font-semibold text-slate-700 block">Live Telemetry Alerts</span>
                <span className="text-[10.5px] text-slate-400 block mt-0.5">Show incoming warnings on Dashboard Log Feed.</span>
              </div>
              <input
                type="checkbox"
                checked={livePings}
                onChange={(e) => setLivePings(e.target.checked)}
                className="w-9 h-5 bg-slate-200 checked:bg-brand-primary rounded-full cursor-pointer focus:ring-0 appearance-none border border-slate-300 checked:border-brand-primary relative before:content-[''] before:absolute before:w-4 before:h-4 before:bg-white before:rounded-full before:top-[1px] before:left-[1px] checked:before:translate-x-4 before:transition-all"
              />
            </div>

            {/* Toggle 2 */}
            <div className="flex justify-between items-center py-2 border-t border-slate-50">
              <div>
                <span className="font-semibold text-slate-700 block">Critical Audio Warnings</span>
                <span className="text-[10.5px] text-slate-400 block mt-0.5">Sound distress alarm on high-severity ANPR plate hits.</span>
              </div>
              <input
                type="checkbox"
                checked={soundAlerts}
                onChange={(e) => setSoundAlerts(e.target.checked)}
                className="w-9 h-5 bg-slate-200 checked:bg-brand-primary rounded-full cursor-pointer focus:ring-0 appearance-none border border-slate-300 checked:border-brand-primary relative before:content-[''] before:absolute before:w-4 before:h-4 before:bg-white before:rounded-full before:top-[1px] before:left-[1px] checked:before:translate-x-4 before:transition-all"
              />
            </div>
          </div>
        </div>

        {/* Card 2: Simulated Database Nodes */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col gap-4">
          <div className="border-b border-slate-100 pb-2 flex items-center gap-2">
            <Database className="w-4 h-4 text-brand-secondary" />
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Database Node Sockets</h3>
          </div>

          <div className="flex flex-col gap-3.5 text-xs">
            {/* Node 1 */}
            <div className="flex items-center justify-between p-2.5 bg-slate-50 border border-slate-150 rounded">
              <div>
                <span className="font-bold text-slate-700 block">State Data Centre Hub</span>
                <span className="text-[10px] font-mono text-slate-400 block">URL: sdc.ksp.gov.in/intel-socket</span>
              </div>
              <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded font-mono font-bold text-[9px] uppercase border border-emerald-200">
                Connected
              </span>
            </div>

            {/* Node 2 */}
            <div className="flex items-center justify-between p-2.5 bg-slate-50 border border-slate-150 rounded">
              <div>
                <span className="font-bold text-slate-700 block">Telecom CDR Triangulation Grid</span>
                <span className="text-[10px] font-mono text-slate-400 block">URL: cell-tower.ksp.net/triangulate</span>
              </div>
              <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded font-mono font-bold text-[9px] uppercase border border-emerald-200">
                Connected
              </span>
            </div>

            {/* Node 3 */}
            <div className="flex items-center justify-between p-2.5 bg-slate-50 border border-slate-150 rounded">
              <div>
                <span className="font-bold text-slate-700 block">National VAHAN Registry Api</span>
                <span className="text-[10px] font-mono text-slate-400 block">URL: vahan.nic.in/api/v4/lookup</span>
              </div>
              <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded font-mono font-bold text-[9px] uppercase border border-emerald-200">
                Connected
              </span>
            </div>
          </div>
        </div>

        {/* Card 3: Terminal Audit Registry */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col gap-4">
          <div className="border-b border-slate-100 pb-2 flex items-center gap-2">
            <History className="w-4 h-4 text-brand-secondary" />
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Terminal Access Audit Log</h3>
          </div>

          <div className="flex flex-col gap-2 text-xs font-mono">
            <div className="p-2 border border-slate-100 bg-slate-50 rounded flex justify-between text-[10.5px]">
              <span>[20:18:24] Rajesh Kumar queried "KA05MJ4421"</span>
              <span className="text-emerald-600 font-bold">SUCCESS</span>
            </div>
            <div className="p-2 border border-slate-100 bg-slate-50 rounded flex justify-between text-[10.5px]">
              <span>[19:55:12] Rajesh Kumar queried "Vikram Hegde"</span>
              <span className="text-emerald-600 font-bold">SUCCESS</span>
            </div>
            <div className="p-2 border border-slate-100 bg-slate-50 rounded flex justify-between text-[10.5px]">
              <span>[19:40:02] ANPR Node-01 auto-triggered plate alert</span>
              <span className="text-amber-600 font-bold">WARN</span>
            </div>
          </div>
        </div>

        {/* Card 4: Security Cryptography */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col gap-4">
          <div className="border-b border-slate-100 pb-2 flex items-center gap-2">
            <Shield className="w-4 h-4 text-brand-secondary" />
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Security & Cryptography</h3>
          </div>

          <div className="flex flex-col gap-3 text-xs">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-700 block">Session Encryption key</span>
                <span className="text-[10px] font-mono text-slate-400 block mt-0.5">RSA-4096-AES-GCM Node Token</span>
              </div>
              <span className="font-mono text-slate-500 font-bold">KSP-SHA256...</span>
            </div>
            <div className="flex justify-between items-center py-2 border-t border-slate-50">
              <div>
                <span className="font-semibold text-slate-700 block">Language Interface defaults</span>
                <span className="text-[10.5px] text-slate-400 block mt-0.5">Swap dashboard language interface.</span>
              </div>
              <button
                onClick={() => setLanguage(language === 'en' ? 'kn' : 'en')}
                className="py-1 px-3 bg-slate-50 border border-slate-200 hover:bg-slate-100 rounded font-bold"
              >
                {language === 'en' ? 'English (EN)' : 'ಕನ್ನಡ (KN)'}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
export default SettingsPage;
