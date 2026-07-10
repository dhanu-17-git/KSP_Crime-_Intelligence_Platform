import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { FIRs, SUSPECTS, VEHICLES } from '../../services/mockDb';
import { FileSpreadsheet, Printer, Edit3 } from 'lucide-react';

export const Reports: React.FC = () => {
  const { language } = useApp();
  const [reportType, setReportType] = useState('FIR Summary');
  const [selectedEntityId, setSelectedEntityId] = useState(FIRs[0].id);
  const [remarks, setRemarks] = useState('');

  // Handle report printing
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto select-none print:p-0 print:bg-white print:text-black">
      {/* Title Header (Hidden on print) */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-4 print:hidden">
        <div>
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-brand-primary" />
            <h1 className="text-sm font-bold text-brand-primary uppercase tracking-wider">
              {language === 'en' ? 'Official Documents & Reports Builder' : 'ವರದಿಗಳ ತಯಾರಿ ಕೇಂದ್ರ'}
            </h1>
          </div>
          <p className="text-xs text-slate-500 font-sans mt-1">
            Build, review, and print standardized legal dossiers, FIR reports, and vehicle ANPR track sheets.
          </p>
        </div>
      </div>

      {/* Main Grid View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Report Builder Options (Hidden on print) */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col gap-4 print:hidden">
          <div className="border-b border-slate-100 pb-2 flex items-center gap-2">
            <Edit3 className="w-4 h-4 text-brand-secondary" />
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Builder Parameters</h3>
          </div>

          <div className="flex flex-col gap-4 text-xs">
            {/* Report Type */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold text-slate-600">Document Classification</label>
              <select
                value={reportType}
                onChange={(e) => {
                  setReportType(e.target.value);
                  if (e.target.value === 'FIR Summary') setSelectedEntityId(FIRs[0].id);
                  else if (e.target.value === 'Suspect Profile') setSelectedEntityId(SUSPECTS[0].id);
                  else setSelectedEntityId(VEHICLES[0].id);
                }}
                className="w-full p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 focus:bg-white rounded outline-none"
              >
                <option value="FIR Summary">FIR Incident Report Sheet</option>
                <option value="Suspect Profile">Suspect Criminal Record Dossier</option>
                <option value="ANPR Tracking">ANPR Transit Log Audit</option>
              </select>
            </div>

            {/* Entity Linkage */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold text-slate-600">Linked Entity Database ID</label>
              <select
                value={selectedEntityId}
                onChange={(e) => setSelectedEntityId(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 focus:bg-white rounded outline-none font-mono text-[11px]"
              >
                {reportType === 'FIR Summary' &&
                  FIRs.map((f) => <option key={f.id} value={f.id}>{f.id} - {f.category}</option>)}
                {reportType === 'Suspect Profile' &&
                  SUSPECTS.map((s) => <option key={s.id} value={s.id}>{s.name} ({s.biometricId})</option>)}
                {reportType === 'ANPR Tracking' &&
                  VEHICLES.map((v) => <option key={v.id} value={v.id}>{v.id} - {v.color} {v.make}</option>)}
              </select>
            </div>

            {/* Remarks / Comments */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold text-slate-600">Officer Notes & Endorsement</label>
              <textarea
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                rows={4}
                placeholder="Include formal observations, evidence updates, or next directives..."
                className="w-full p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 focus:bg-white rounded outline-none resize-none font-sans"
              />
            </div>

            {/* Action Trigger */}
            <button
              onClick={handlePrint}
              className="py-2.5 px-4 bg-brand-primary hover:bg-brand-primary-light text-white font-bold rounded flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm mt-2"
            >
              <Printer className="w-4 h-4 text-brand-secondary" />
              Print Official Document
            </button>
          </div>
        </div>

        {/* Right Side: LIVE LETTERHEAD PREVIEW PANEL (Visible on print too) */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-lg p-8 shadow-sm flex flex-col justify-between min-h-[600px] max-w-4xl mx-auto font-mono text-xs text-slate-800 relative print:border-none print:shadow-none print:p-0 print:mx-0">
          
          {/* Letterhead Top Emblem Header */}
          <div className="text-center border-b-2 border-slate-800 pb-4 flex flex-col items-center">
            <span className="text-[10px] uppercase font-bold tracking-widest text-slate-500 block leading-none">
              Government of Karnataka
            </span>
            <span className="text-sm font-bold uppercase tracking-wider text-brand-primary mt-1 block">
              Karnataka State Police Department
            </span>
            <span className="text-[10px] text-slate-500 mt-2 block font-mono">
              OFFICIAL OPERATIONAL REPORT SHEET // LAW ENFORCEMENT RECORD
            </span>
            <div className="w-full flex justify-between items-center text-[8px] font-mono text-slate-400 mt-3 px-2">
              <span>SYSTEM CODE: KSP-NET-DOC-9842</span>
              <span>DATE GENERATED: {new Date().toLocaleDateString()}</span>
            </div>
          </div>

          {/* Letterhead Document body */}
          <div className="my-6 flex-1 flex flex-col gap-6">
            
            {/* General Block */}
            <div className="grid grid-cols-2 gap-4 bg-slate-50 border border-slate-200 rounded p-4 text-[11px] font-sans">
              <div>
                <span className="text-[9px] text-slate-400 block font-mono uppercase">Document Scope</span>
                <span className="text-slate-800 font-bold block">{reportType} Dossier</span>
              </div>
              <div>
                <span className="text-[9px] text-slate-400 block font-mono uppercase">Security Classification</span>
                <span className="text-red-700 font-bold block">CONFIDENTIAL</span>
              </div>
              <div>
                <span className="text-[9px] text-slate-400 block font-mono uppercase">Authorizing Unit</span>
                <span className="text-slate-700 block">Koramangala Precinct, Bangalore City</span>
              </div>
              <div>
                <span className="text-[9px] text-slate-400 block font-mono uppercase">Author Officer Badge</span>
                <span className="text-slate-700 block font-mono">Rajesh Kumar (Badge: KSP-9432)</span>
              </div>
            </div>

            {/* Mapped Entity Profile Details */}
            <div className="border-t border-slate-100 pt-4">
              <h4 className="font-bold text-slate-800 uppercase mb-2">1. Linked Entity Dossier Details</h4>
              
              {/* Type 1: FIR summary */}
              {reportType === 'FIR Summary' && (() => {
                const fir = FIRs.find((f) => f.id === selectedEntityId) || FIRs[0];
                return (
                  <div className="pl-3 border-l-2 border-brand-primary flex flex-col gap-2 leading-relaxed">
                    <p><b>FIR Number:</b> {fir.id}</p>
                    <p><b>IPC Sections Charged:</b> {fir.ipcSections.join(', ')}</p>
                    <p><b>Jurisdiction Station:</b> Koramangala Police Station</p>
                    <p><b>Incident Brief:</b> {fir.summary}</p>
                  </div>
                );
              })()}

              {/* Type 2: Suspect details */}
              {reportType === 'Suspect Profile' && (() => {
                const suspect = SUSPECTS.find((s) => s.id === selectedEntityId) || SUSPECTS[0];
                return (
                  <div className="pl-3 border-l-2 border-brand-primary flex flex-col gap-2 leading-relaxed">
                    <p><b>Suspect Profile Name:</b> {suspect.name}</p>
                    <p><b>Biometric Index:</b> {suspect.biometricId}</p>
                    <p><b>Aadhaar ID Record:</b> {suspect.aadhaarNo}</p>
                    <p><b>Operational Gang Affiliation:</b> {suspect.gangAffiliation}</p>
                    <p><b>Verified Crime Narrative:</b> {suspect.bio}</p>
                  </div>
                );
              })()}

              {/* Type 3: Vehicle ANPR tracking */}
              {reportType === 'ANPR Tracking' && (() => {
                const veh = VEHICLES.find((v) => v.id === selectedEntityId) || VEHICLES[0];
                return (
                  <div className="pl-3 border-l-2 border-brand-primary flex flex-col gap-2 leading-relaxed">
                    <p><b>Vehicle Registration Plate:</b> {veh.id}</p>
                    <p><b>Model Class:</b> {veh.color} {veh.make} {veh.model}</p>
                    <p><b>Registered Owner:</b> {veh.ownerName} (Aadhaar: {veh.ownerAadhaar})</p>
                    <p><b>Latest ANPR Camera Log:</b> {veh.anprLogs[0]?.locationName} CCTV @ {new Date(veh.anprLogs[0]?.timestamp).toLocaleString()}</p>
                  </div>
                );
              })()}
            </div>

            {/* Officer remarks block */}
            <div className="border-t border-slate-100 pt-4">
              <h4 className="font-bold text-slate-800 uppercase mb-2">2. Endorsing Officer Remarks</h4>
              <p className="pl-3 leading-relaxed text-slate-600 bg-slate-50 border border-slate-100 rounded p-3 font-sans min-h-[80px]">
                {remarks.trim() || 'No supplementary comments entered by compilation officer. Document generated on system query parameters only.'}
              </p>
            </div>

          </div>

          {/* Letterhead Signature block */}
          <div className="flex justify-between items-end border-t border-slate-200 pt-8 mt-12">
            <div className="flex flex-col gap-1">
              <span className="font-bold">Inspector signature: _______________________</span>
              <span className="text-[10px] text-slate-400">Inspector Rajesh Kumar (KSP-9432)</span>
            </div>
            <div className="flex flex-col gap-1 items-end">
              <span className="font-bold">Station Seal: _______________________</span>
              <span className="text-[10px] text-slate-400">Koramangala Precinct, Bangalore City</span>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};
export default Reports;
