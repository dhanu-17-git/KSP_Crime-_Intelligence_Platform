import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Header } from '../components/Header';
import { useApp } from '../context/AppContext';
import {
  X,
  ShieldAlert,
  FileText,
  UserCheck,
  Car,
  PhoneCall,
  ExternalLink,
  BookOpen,
  Camera
} from 'lucide-react';
import { CALL_LOGS, SUSPECTS, VEHICLES } from '../services/mockDb';

export const DashboardLayout: React.FC = () => {
  const navigate = useNavigate();
  const {
    selectedFir,
    setSelectedFir,
    selectedSuspect,
    setSelectedSuspect,
    selectedVehicle,
    setSelectedVehicle,
    setAiQuery,
    language,
    toasts,
    removeToast
  } = useApp();

  const handleOpenSuspect = (id: string) => {
    const s = SUSPECTS.find((item) => item.id === id);
    if (s) {
      setSelectedFir(null);
      setSelectedVehicle(null);
      setSelectedSuspect(s);
    }
  };

  const handleOpenVehicle = (plate: string) => {
    const v = VEHICLES.find((item) => item.id === plate);
    if (v) {
      setSelectedFir(null);
      setSelectedSuspect(null);
      setSelectedVehicle(v);
    }
  };

  const handleAnalyzeInWorkspace = (query: string) => {
    setAiQuery(query);
    setSelectedFir(null);
    setSelectedSuspect(null);
    setSelectedVehicle(null);
    navigate('/ai-workspace');
  };

  const handleViewInNetwork = (_suspectName: string) => {
    setSelectedSuspect(null);
    navigate('/network');
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 font-sans select-none">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Core View Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto bg-slate-50 relative">
          <Outlet />
        </main>
      </div>

      {/* ======================================================== */}
      {/* OVERLAY BACKDROP */}
      {/* ======================================================== */}
      {(selectedFir || selectedSuspect || selectedVehicle) && (
        <div
          onClick={() => {
            setSelectedFir(null);
            setSelectedSuspect(null);
            setSelectedVehicle(null);
          }}
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 transition-opacity"
        />
      )}

      {/* ======================================================== */}
      {/* CASE / FIR DRAWER DETAILS */}
      {/* ======================================================== */}
      {selectedFir && (
        <div className="fixed top-0 right-0 h-full w-[520px] bg-white shadow-2xl z-50 border-l border-slate-200 flex flex-col justify-between transform transition-transform duration-300 animate-in slide-in-from-right">
          <div className="flex-1 overflow-y-auto">
            {/* Drawer Header */}
            <div className="px-6 py-5 bg-brand-primary text-white flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-brand-secondary" />
                <div>
                  <h3 className="text-sm font-mono tracking-wider text-slate-300">CASE DOSSIER DETAILS</h3>
                  <h2 className="text-base font-bold text-white leading-none mt-0.5">{selectedFir.id}</h2>
                </div>
              </div>
              <button
                onClick={() => setSelectedFir(null)}
                className="p-1 text-slate-300 hover:text-white bg-brand-primary-light border border-slate-700/60 rounded cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Drawer Content */}
            <div className="p-6 flex flex-col gap-6">
              {/* Highlight Action */}
              <button
                onClick={() => handleAnalyzeInWorkspace(`Find all suspects connected with case ${selectedFir.id}`)}
                className="w-full py-2 px-3 bg-brand-secondary text-brand-primary font-bold text-xs rounded border border-brand-secondary hover:bg-brand-secondary/90 transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-sm"
              >
                <ExternalLink className="w-4 h-4" />
                {language === 'en' ? 'Launch Workspace Analysis for this Case' : 'ಈ ಪ್ರಕರಣದ ಎಐ ತನಿಖೆ ಪ್ರಾರಂಭಿಸಿ'}
              </button>

              {/* Grid Metadata */}
              <div className="grid grid-cols-2 gap-4 bg-slate-50 border border-slate-200 rounded-lg p-4 text-xs font-sans">
                <div>
                  <span className="text-[10px] text-slate-400 block font-mono">INCIDENT TYPE</span>
                  <span className="text-slate-800 font-bold block mt-0.5">{selectedFir.category}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-mono">SEVERITY LEVEL</span>
                  <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold mt-1 font-mono ${
                    selectedFir.severity === 'Critical' ? 'bg-red-50 text-red-700 border border-red-200' :
                    selectedFir.severity === 'Major' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
                    'bg-slate-100 text-slate-700 border border-slate-200'
                  }`}>
                    {selectedFir.severity}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-mono">INCIDENT TIME</span>
                  <span className="text-slate-700 block mt-0.5 font-mono">
                    {new Date(selectedFir.incidentDate).toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-mono">REGISTERED TIMESTAMP</span>
                  <span className="text-slate-700 block mt-0.5 font-mono">
                    {new Date(selectedFir.registrationDate).toLocaleString()}
                  </span>
                </div>
                <div className="col-span-2">
                  <span className="text-[10px] text-slate-400 block font-mono">IPC SECTIONS CHARGED</span>
                  <div className="flex flex-wrap gap-1 mt-1 font-mono">
                    {selectedFir.ipcSections.map((sec, idx) => (
                      <span key={idx} className="bg-slate-200/80 text-slate-800 px-1.5 py-0.5 rounded text-[10px]">
                        {sec}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Case Summary */}
              <div>
                <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5 border-b border-slate-100 pb-1">
                  <FileText className="w-4 h-4 text-brand-secondary" /> Incident Brief Summary
                </h4>
                <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 border border-slate-100 rounded p-3 font-sans">
                  {selectedFir.summary}
                </p>
              </div>

              {/* Associated Suspects */}
              <div>
                <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5 border-b border-slate-100 pb-1">
                  <UserCheck className="w-4 h-4 text-brand-secondary" /> Linked Suspects ({selectedFir.suspectIds.length})
                </h4>
                <div className="flex flex-col gap-2">
                  {selectedFir.suspectIds.map((sId) => {
                    const suspectObj = SUSPECTS.find((s) => s.id === sId);
                    return suspectObj ? (
                      <div
                        key={sId}
                        onClick={() => handleOpenSuspect(sId)}
                        className="flex items-center justify-between p-2 hover:bg-slate-50 border border-slate-200 rounded cursor-pointer transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-[10px]">
                            {suspectObj.name.charAt(0)}
                          </div>
                          <span className="text-xs font-semibold text-brand-primary hover:underline">{suspectObj.name}</span>
                        </div>
                        <span className="text-[10px] text-slate-400 font-mono italic">{suspectObj.gangAffiliation}</span>
                      </div>
                    ) : null;
                  })}
                </div>
              </div>

              {/* Associated Vehicles */}
              <div>
                <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5 border-b border-slate-100 pb-1">
                  <Car className="w-4 h-4 text-brand-secondary" /> Linked Vehicles ({selectedFir.vehicleIds.length})
                </h4>
                <div className="flex flex-col gap-2">
                  {selectedFir.vehicleIds.map((vId) => {
                    const vehicleObj = VEHICLES.find((v) => v.id === vId);
                    return vehicleObj ? (
                      <div
                        key={vId}
                        onClick={() => handleOpenVehicle(vId)}
                        className="flex items-center justify-between p-2 hover:bg-slate-50 border border-slate-200 rounded cursor-pointer transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <Car className="w-4 h-4 text-slate-400" />
                          <span className="text-xs font-mono font-bold text-brand-primary hover:underline">{vId}</span>
                        </div>
                        <span className="text-[10px] bg-red-50 text-red-700 px-1 rounded font-mono font-bold">
                          {vehicleObj.status}
                        </span>
                      </div>
                    ) : null;
                  })}
                </div>
              </div>
            </div>
          </div>
          <div className="p-4 border-t border-slate-100 bg-slate-50 text-right">
            <button
              onClick={() => setSelectedFir(null)}
              className="py-1.5 px-4 bg-white border border-slate-300 hover:bg-slate-50 text-xs font-semibold rounded text-slate-700 transition-colors cursor-pointer"
            >
              Close Dossier
            </button>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* SUSPECT PROFILE DRAWER */}
      {/* ======================================================== */}
      {selectedSuspect && (
        <div className="fixed top-0 right-0 h-full w-[520px] bg-white shadow-2xl z-50 border-l border-slate-200 flex flex-col justify-between transform transition-transform duration-300 animate-in slide-in-from-right">
          <div className="flex-1 overflow-y-auto">
            {/* Drawer Header */}
            <div className="px-6 py-5 bg-brand-primary text-white flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center gap-2">
                <UserCheck className="w-5 h-5 text-brand-secondary" />
                <div>
                  <h3 className="text-sm font-mono tracking-wider text-slate-300">SUSPECT PROFILE LEDGER</h3>
                  <h2 className="text-base font-bold text-white leading-none mt-0.5">{selectedSuspect.name}</h2>
                </div>
              </div>
              <button
                onClick={() => setSelectedSuspect(null)}
                className="p-1 text-slate-300 hover:text-white bg-brand-primary-light border border-slate-700/60 rounded cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Drawer Content */}
            <div className="p-6 flex flex-col gap-6">
              {/* Bio Grid */}
              <div className="flex gap-4 items-start">
                <div className={`w-20 h-20 border rounded-lg flex items-center justify-center text-2xl font-bold shrink-0 ${selectedSuspect.photoPlaceholder}`}>
                  {selectedSuspect.name.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-base font-bold text-slate-800">{selectedSuspect.name}</h3>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold font-mono ${
                      selectedSuspect.riskLevel === 'Critical' ? 'bg-red-50 text-red-700 border border-red-200' :
                      selectedSuspect.riskLevel === 'High' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
                      'bg-slate-100 text-slate-700 border border-slate-200'
                    }`}>
                      {selectedSuspect.riskLevel} Risk
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1 font-mono">
                    Aliases: {selectedSuspect.aliases.join(', ') || 'None'}
                  </p>
                  <p className="text-xs font-semibold text-brand-secondary mt-1">
                    Gang: {selectedSuspect.gangAffiliation}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => handleAnalyzeInWorkspace(`Find all suspects connected with Vikram Hegde`)}
                  className="py-2 px-3 bg-brand-secondary text-brand-primary font-bold text-xs rounded border border-brand-secondary hover:bg-brand-secondary/90 transition-all flex items-center justify-center gap-1 cursor-pointer"
                >
                  <ExternalLink className="w-4 h-4" />
                  Analyze Dossier
                </button>
                <button
                  onClick={() => handleViewInNetwork(selectedSuspect.name)}
                  className="py-2 px-3 bg-brand-primary text-white font-bold text-xs rounded hover:bg-brand-primary-light transition-all flex items-center justify-center gap-1 cursor-pointer"
                >
                  <ExternalLink className="w-4 h-4 text-brand-secondary" />
                  Network Graph
                </button>
              </div>

              {/* Biometrics */}
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-xs font-sans grid grid-cols-2 gap-3">
                <div>
                  <span className="text-[10px] text-slate-400 font-mono">BIOMETRIC RECORD NO</span>
                  <span className="text-slate-800 font-bold block mt-0.5">{selectedSuspect.biometricId}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-mono">AADHAAR RECORD ID</span>
                  <span className="text-slate-800 font-bold block mt-0.5 font-mono">{selectedSuspect.aadhaarNo}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-mono">CONTACT NUMBER</span>
                  <span className="text-slate-700 block mt-0.5 font-mono">{selectedSuspect.phoneNo}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-mono">OPERATIONAL STATUS</span>
                  <span className="text-slate-700 block mt-0.5 font-bold">{selectedSuspect.status}</span>
                </div>
              </div>

              {/* Suspect Bio */}
              <div>
                <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5 border-b border-slate-100 pb-1">
                  <BookOpen className="w-4 h-4 text-brand-secondary" /> Intelligence Narrative
                </h4>
                <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 border border-slate-100 rounded p-3">
                  {selectedSuspect.bio}
                </p>
              </div>

              {/* Associated Transport */}
              {selectedSuspect.associatedVehicleId && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5 border-b border-slate-100 pb-1">
                    <Car className="w-4 h-4 text-brand-secondary" /> Primary Vehicle Associated
                  </h4>
                  <div
                    onClick={() => handleOpenVehicle(selectedSuspect.associatedVehicleId!)}
                    className="p-3 bg-slate-50 border border-slate-200 rounded flex items-center justify-between cursor-pointer hover:bg-slate-100 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <Car className="w-5 h-5 text-slate-500" />
                      <div>
                        <span className="text-xs font-mono font-bold text-brand-primary block">
                          {selectedSuspect.associatedVehicleId}
                        </span>
                        <span className="text-[10px] text-slate-400 block leading-none">Mahindra Scorpio (White)</span>
                      </div>
                    </div>
                    <span className="text-[10px] text-brand-secondary font-bold uppercase tracking-wider">ANPR LOGGED</span>
                  </div>
                </div>
              )}

              {/* Telecommunication Ties */}
              <div>
                <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5 border-b border-slate-100 pb-1">
                  <PhoneCall className="w-4 h-4 text-brand-secondary" /> Intercepted Phone Logs
                </h4>
                <div className="flex flex-col gap-2">
                  {CALL_LOGS.filter(c => c.fromName === selectedSuspect.name || c.toName === selectedSuspect.name).map((call, idx) => (
                    <div key={idx} className="p-2 border border-slate-100 rounded bg-slate-50 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-semibold text-slate-700">
                          {call.fromName === selectedSuspect.name ? `Dialed ${call.toName}` : `Received from ${call.fromName}`}
                        </span>
                        <span className="text-[10px] text-slate-400 block font-mono">Tower: {call.cellTowerId}</span>
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] text-slate-500 font-mono block">
                          {new Date(call.timestamp).toLocaleTimeString()}
                        </span>
                        <span className="text-[10px] text-slate-400 block font-mono">{call.durationSeconds}s duration</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          <div className="p-4 border-t border-slate-100 bg-slate-50 text-right">
            <button
              onClick={() => setSelectedSuspect(null)}
              className="py-1.5 px-4 bg-white border border-slate-300 hover:bg-slate-50 text-xs font-semibold rounded text-slate-700 transition-colors cursor-pointer"
            >
              Close Profile
            </button>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* VEHICLE DOSSIER DRAWER */}
      {/* ======================================================== */}
      {selectedVehicle && (
        <div className="fixed top-0 right-0 h-full w-[520px] bg-white shadow-2xl z-50 border-l border-slate-200 flex flex-col justify-between transform transition-transform duration-300 animate-in slide-in-from-right">
          <div className="flex-1 overflow-y-auto">
            {/* Drawer Header */}
            <div className="px-6 py-5 bg-brand-primary text-white flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Car className="w-5 h-5 text-brand-secondary" />
                <div>
                  <h3 className="text-sm font-mono tracking-wider text-slate-300">ANPR TRANSPORT RECORD</h3>
                  <h2 className="text-base font-bold text-white leading-none mt-0.5">{selectedVehicle.id}</h2>
                </div>
              </div>
              <button
                onClick={() => setSelectedVehicle(null)}
                className="p-1 text-slate-300 hover:text-white bg-brand-primary-light border border-slate-700/60 rounded cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Drawer Content */}
            <div className="p-6 flex flex-col gap-6">
              {/* Highlight Action */}
              <button
                onClick={() => handleAnalyzeInWorkspace(`Find all suspects connected with vehicle ${selectedVehicle.id}`)}
                className="w-full py-2 px-3 bg-brand-secondary text-brand-primary font-bold text-xs rounded border border-brand-secondary hover:bg-brand-secondary/90 transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-sm"
              >
                <ExternalLink className="w-4 h-4" />
                {language === 'en' ? 'Launch Workspace Analysis for this Vehicle' : 'ಈ ವಾಹನದ ಎಐ ತನಿಖೆ ಪ್ರಾರಂಭಿಸಿ'}
              </button>

              {/* Basic Vehicle Details */}
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-xs font-sans grid grid-cols-2 gap-3">
                <div>
                  <span className="text-[10px] text-slate-400 font-mono">REGISTRATION PLATE</span>
                  <span className="text-slate-800 font-bold block mt-0.5 font-mono">{selectedVehicle.id}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-mono">MONITOR STATUS</span>
                  <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold mt-1 font-mono ${
                    selectedVehicle.status === 'Flagged' ? 'bg-red-50 text-red-700 border border-red-200' :
                    selectedVehicle.status === 'Under Investigation' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
                    'bg-slate-100 text-slate-700 border border-slate-200'
                  }`}>
                    {selectedVehicle.status}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-mono">VEHICLE CLASS</span>
                  <span className="text-slate-700 block mt-0.5 font-semibold">
                    {selectedVehicle.color} {selectedVehicle.make} {selectedVehicle.model}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-mono">REGISTERED OWNER</span>
                  <span className="text-brand-primary font-bold block mt-0.5 hover:underline cursor-pointer"
                        onClick={() => {
                          const sObj = SUSPECTS.find(s => s.name === selectedVehicle.ownerName);
                          if (sObj) handleOpenSuspect(sObj.id);
                        }}>
                    {selectedVehicle.ownerName}
                  </span>
                </div>
              </div>

              {/* ANPR Track Logs */}
              <div>
                <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-3 flex items-center gap-1.5 border-b border-slate-100 pb-1">
                  <Camera className="w-4 h-4 text-brand-secondary" /> ANPR CCTV Camera Pings ({selectedVehicle.anprLogs.length})
                </h4>
                <div className="relative border-l border-slate-200 pl-4 ml-2 flex flex-col gap-4">
                  {selectedVehicle.anprLogs.map((log, idx) => (
                    <div key={idx} className="relative text-xs">
                      {/* Timeline dot */}
                      <span className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-brand-primary border-2 border-white ring-1 ring-brand-primary/50" />
                      
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-semibold text-slate-800">{log.locationName}</span>
                        <span className="text-[10px] text-slate-400 font-mono">
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 mt-0.5 text-slate-500 font-mono text-[10px]">
                        <span>Camera ID: {log.cctvId}</span>
                        <span>•</span>
                        <span className="text-emerald-600 font-semibold">Confidence: {log.confidence}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          <div className="p-4 border-t border-slate-100 bg-slate-50 text-right">
            <button
              onClick={() => setSelectedVehicle(null)}
              className="py-1.5 px-4 bg-white border border-slate-300 hover:bg-slate-50 text-xs font-semibold rounded text-slate-700 transition-colors cursor-pointer"
            >
              Close Dossier
            </button>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* TOAST NOTIFICATION STACK */}
      {/* ======================================================== */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className="pointer-events-auto w-80 bg-white border border-slate-200 shadow-xl rounded-lg p-3.5 flex items-start justify-between gap-3 animate-in slide-in-from-bottom-2 fade-in duration-200"
          >
            <div className="flex items-start gap-2.5">
              <span className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${
                toast.type === 'success' ? 'bg-emerald-500' :
                toast.type === 'error' ? 'bg-red-500 animate-pulse' :
                toast.type === 'warn' ? 'bg-amber-500' :
                'bg-slate-400'
              }`} />
              <div className="text-xs">
                <span className="text-[9px] text-slate-400 font-mono tracking-wider block font-semibold uppercase leading-none mb-1">
                  {toast.type === 'success' ? 'SYSTEM NOTIFY' : 'CRITICAL TELEMETRY'}
                </span>
                <p className="text-slate-700 font-medium leading-normal">{toast.message}</p>
              </div>
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-slate-400 hover:text-slate-600 p-0.5 rounded cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
