import React, { useState, useMemo } from 'react';
import { useApp } from '../../context/AppContext';
import { SUSPECTS } from '../../services/mockDb';
import { UserCheck, Search, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Suspects: React.FC = () => {
  const navigate = useNavigate();
  const { setSelectedSuspect, setAiQuery, language } = useApp();

  // Filters State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRisk, setSelectedRisk] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  // Filter logic
  const filteredSuspects = useMemo(() => {
    return SUSPECTS.filter((s) => {
      const matchSearch =
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.aliases.some((a) => a.toLowerCase().includes(searchQuery.toLowerCase())) ||
        s.gangAffiliation.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.biometricId.toLowerCase().includes(searchQuery.toLowerCase());
      
      if (!matchSearch) return false;
      if (selectedRisk !== 'all' && s.riskLevel !== selectedRisk) return false;
      if (selectedStatus !== 'all' && s.status !== selectedStatus) return false;

      return true;
    });
  }, [searchQuery, selectedRisk, selectedStatus]);

  const handleAnalyze = (name: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setAiQuery(`Find all cases and contacts for suspect ${name}`);
    navigate('/ai-workspace');
  };

  return (
    <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto select-none">
      {/* Page Title */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-brand-primary" />
            <h1 className="text-sm font-bold text-brand-primary uppercase tracking-wider">
              {language === 'en' ? 'Suspect Intel Registry' : 'ಶಂಕಿತ ವ್ಯಕ್ತಿಗಳ ಮಾಹಿತಿ ನೋಂದಣಿ'}
            </h1>
          </div>
          <p className="text-xs text-slate-500 font-sans mt-1">
            Browse and query verified profiles, biometrics, gang affiliations, and risk level indexes.
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex flex-col md:flex-row md:items-center gap-3 text-xs">
        <div className="flex-1 flex items-center border border-slate-200 focus-within:border-slate-400 focus-within:bg-white rounded-md bg-slate-50 px-3 py-2 transition-all">
          <Search className="w-4 h-4 text-slate-400 mr-2 shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by name, alias, gang, biometric ID..."
            className="bg-transparent border-none text-xs w-full focus:outline-none placeholder-slate-400 font-sans"
          />
        </div>

        {/* Risk Level */}
        <select
          value={selectedRisk}
          onChange={(e) => setSelectedRisk(e.target.value)}
          className="p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 rounded outline-none shrink-0"
        >
          <option value="all">All Risk Levels</option>
          <option value="Critical">Critical Risk</option>
          <option value="High">High Risk</option>
          <option value="Medium">Medium Risk</option>
        </select>

        {/* Status */}
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 rounded outline-none shrink-0"
        >
          <option value="all">All Statuses</option>
          <option value="Absconding">Absconding</option>
          <option value="Under Surveillance">Under Surveillance</option>
          <option value="Detained">Detained</option>
          <option value="In Custody">In Custody</option>
        </select>
      </div>

      {/* Grid of Suspect Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredSuspects.length === 0 ? (
          <div className="col-span-full text-center py-10 bg-white border border-slate-200 rounded-lg text-slate-400 text-xs">
            No matching profiles in state register
          </div>
        ) : (
          filteredSuspects.map((suspect) => (
            <div
              key={suspect.id}
              onClick={() => setSelectedSuspect(suspect)}
              className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm hover:border-slate-300 transition-all flex flex-col justify-between gap-4 cursor-pointer relative overflow-hidden"
            >
              {/* Highlight bar based on risk */}
              <div className={`absolute top-0 left-0 w-full h-1 ${
                suspect.riskLevel === 'Critical' ? 'bg-red-600' :
                suspect.riskLevel === 'High' ? 'bg-orange-500' :
                'bg-amber-400'
              }`} />

              <div className="flex gap-4 items-start">
                <div className={`w-14 h-14 rounded-lg flex items-center justify-center font-extrabold border text-lg shrink-0 ${suspect.photoPlaceholder}`}>
                  {suspect.name.charAt(0)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex justify-between items-start gap-2">
                    <h3 className="text-xs font-bold text-slate-800 truncate hover:underline">{suspect.name}</h3>
                    <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold font-mono uppercase ${
                      suspect.riskLevel === 'Critical' ? 'bg-red-50 text-red-700' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {suspect.riskLevel}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 font-mono mt-0.5">ID: {suspect.biometricId}</p>
                  <p className="text-[10px] font-bold text-brand-secondary mt-1">{suspect.gangAffiliation}</p>
                </div>
              </div>

              <div className="bg-slate-50 border border-slate-100 rounded p-3 text-[10.5px] text-slate-500 leading-normal font-sans line-clamp-2">
                {suspect.bio}
              </div>

              {/* Card Footer Actions */}
              <div className="flex justify-between items-center border-t border-slate-100 pt-3">
                <span className="text-[10px] text-slate-400 font-mono">Status: <span className="font-bold text-slate-700">{suspect.status}</span></span>
                <div className="flex gap-2">
                  <button
                    onClick={(e) => handleAnalyze(suspect.name, e)}
                    className="py-1 px-2 bg-brand-secondary text-brand-primary font-bold text-[9px] rounded hover:bg-brand-secondary/90 transition-colors cursor-pointer"
                  >
                    AI Analyze
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedSuspect(suspect);
                    }}
                    className="py-1 px-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-[9px] rounded transition-colors cursor-pointer flex items-center gap-0.5"
                  >
                    <Eye className="w-3 h-3" /> Profile
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
export default Suspects;
