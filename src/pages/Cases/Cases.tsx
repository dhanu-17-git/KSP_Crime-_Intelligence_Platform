import React, { useState, useMemo } from 'react';
import { useApp } from '../../context/AppContext';
import { FIRs, POLICE_STATIONS } from '../../services/mockDb';
import { FolderLock, Search, Filter, Eye } from 'lucide-react';

export const Cases: React.FC = () => {
  const { selectedDistrictId, setSelectedFir, language } = useApp();

  // Filters State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStation, setSelectedStation] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  // Filter logic
  const filteredFirs = useMemo(() => {
    return FIRs.filter((f) => {
      // District Filter
      if (selectedDistrictId !== 'all') {
        const ps = POLICE_STATIONS.find((p) => p.id === f.stationId);
        if (!ps || ps.districtId !== selectedDistrictId) return false;
      }

      const matchSearch =
        f.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        f.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        f.summary.toLowerCase().includes(searchQuery.toLowerCase());
      
      if (!matchSearch) return false;
      if (selectedStation !== 'all' && f.stationId !== selectedStation) return false;
      if (selectedSeverity !== 'all' && f.severity !== selectedSeverity) return false;
      if (selectedStatus !== 'all' && f.status !== selectedStatus) return false;

      return true;
    });
  }, [selectedDistrictId, searchQuery, selectedStation, selectedSeverity, selectedStatus]);

  return (
    <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto select-none">
      {/* Page Title */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <FolderLock className="w-5 h-5 text-brand-primary" />
            <h1 className="text-sm font-bold text-brand-primary uppercase tracking-wider">
              {language === 'en' ? 'Active Case Ledger (FIRs)' : 'ಪ್ರಕರಣಗಳ ದಾಖಲಾತಿ'}
            </h1>
          </div>
          <p className="text-xs text-slate-500 font-sans mt-1">
            Access and manage officially registered FIR records, IPC sections, and jurisdictional files.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex flex-col md:flex-row md:items-center gap-3 text-xs">
        {/* Search */}
        <div className="flex-1 flex items-center border border-slate-200 focus-within:border-slate-400 focus-within:bg-white rounded-md bg-slate-50 px-3 py-2 transition-all">
          <Search className="w-4 h-4 text-slate-400 mr-2 shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by FIR no, category, or keywords..."
            className="bg-transparent border-none text-xs w-full focus:outline-none placeholder-slate-400 font-sans"
          />
        </div>

        {/* Station Filter */}
        <div className="flex items-center gap-1.5 shrink-0">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={selectedStation}
            onChange={(e) => setSelectedStation(e.target.value)}
            className="p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 rounded outline-none"
          >
            <option value="all">All Stations</option>
            {POLICE_STATIONS.map((ps) => (
              <option key={ps.id} value={ps.id}>{ps.name}</option>
            ))}
          </select>
        </div>

        {/* Severity */}
        <select
          value={selectedSeverity}
          onChange={(e) => setSelectedSeverity(e.target.value)}
          className="p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 rounded outline-none shrink-0"
        >
          <option value="all">All Severities</option>
          <option value="Critical">Critical</option>
          <option value="Major">Major</option>
          <option value="Moderate">Moderate</option>
        </select>

        {/* Status */}
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 rounded outline-none shrink-0"
        >
          <option value="all">All Statuses</option>
          <option value="Active">Active</option>
          <option value="Under Review">Under Review</option>
          <option value="Closed (Charge Sheeted)">Closed</option>
        </select>
      </div>

      {/* Case Ledger Table */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-400 font-mono text-[10px] uppercase">
                <th className="py-3 px-4 font-semibold">FIR Number</th>
                <th className="py-3 px-4 font-semibold">Jurisdiction (PS)</th>
                <th className="py-3 px-4 font-semibold">Classification Type</th>
                <th className="py-3 px-4 font-semibold">Incident Date</th>
                <th className="py-3 px-4 font-semibold">Severity</th>
                <th className="py-3 px-4 font-semibold">Investigation Status</th>
                <th className="py-3 px-4 font-semibold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredFirs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-slate-400 font-sans">
                    No matching FIR records found in KSP database
                  </td>
                </tr>
              ) : (
                filteredFirs.map((fir) => {
                  const stationObj = POLICE_STATIONS.find((ps) => ps.id === fir.stationId);
                  return (
                    <tr
                      key={fir.id}
                      onClick={() => setSelectedFir(fir)}
                      className="hover:bg-slate-50/70 transition-colors cursor-pointer"
                    >
                      <td className="py-3 px-4 font-mono font-bold text-brand-primary">{fir.id}</td>
                      <td className="py-3 px-4 font-medium text-slate-600">
                        {stationObj ? stationObj.name : 'Unknown Unit'}
                      </td>
                      <td className="py-3 px-4 font-semibold text-slate-700">{fir.category}</td>
                      <td className="py-3 px-4 font-mono text-slate-500">
                        {new Date(fir.incidentDate).toLocaleString()}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-block px-1.5 py-0.5 rounded text-[9px] font-bold font-mono ${
                          fir.severity === 'Critical' ? 'bg-red-50 text-red-700 border border-red-200' :
                          fir.severity === 'Major' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
                          'bg-slate-100 text-slate-700 border border-slate-200'
                        }`}>
                          {fir.severity}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="flex items-center gap-1.5">
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            fir.status === 'Active' ? 'bg-emerald-500' :
                            fir.status === 'Under Review' ? 'bg-amber-400' :
                            'bg-slate-400'
                          }`} />
                          <span className="font-semibold text-slate-600">{fir.status}</span>
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => setSelectedFir(fir)}
                          className="py-1 px-2.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 rounded font-semibold text-[10px] transition-all inline-flex items-center gap-1 cursor-pointer"
                        >
                          <Eye className="w-3.5 h-3.5" /> Dossier
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default Cases;
