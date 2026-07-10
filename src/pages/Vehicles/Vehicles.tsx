import React, { useState, useMemo } from 'react';
import { useApp } from '../../context/AppContext';
import { VEHICLES, SUSPECTS } from '../../services/mockDb';
import { Car, Search, Camera, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Vehicles: React.FC = () => {
  const navigate = useNavigate();
  const { setSelectedVehicle, setSelectedSuspect, setAiQuery, language } = useApp();

  // Filters State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');

  // Filter logic
  const filteredVehicles = useMemo(() => {
    return VEHICLES.filter((v) => {
      const matchSearch =
        v.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        v.model.toLowerCase().includes(searchQuery.toLowerCase()) ||
        v.make.toLowerCase().includes(searchQuery.toLowerCase()) ||
        v.ownerName.toLowerCase().includes(searchQuery.toLowerCase());

      if (!matchSearch) return false;
      if (selectedStatus !== 'all' && v.status !== selectedStatus) return false;

      return true;
    });
  }, [searchQuery, selectedStatus]);

  const handleAnalyze = (plate: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setAiQuery(`Find all suspects connected with vehicle ${plate}`);
    navigate('/ai-workspace');
  };

  const handleOpenOwner = (ownerName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const suspectObj = SUSPECTS.find((s) => s.name === ownerName);
    if (suspectObj) {
      setSelectedSuspect(suspectObj);
    }
  };

  return (
    <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto select-none">
      {/* Page Title */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Car className="w-5 h-5 text-brand-primary" />
            <h1 className="text-sm font-bold text-brand-primary uppercase tracking-wider">
              {language === 'en' ? 'ANPR Watchlist & Vehicle Logs' : 'ವಾಹನಗಳ ಮಾಹಿತಿ (ANPR)'}
            </h1>
          </div>
          <p className="text-xs text-slate-500 font-sans mt-1">
            Browse live number plate scans, camera locations, ownership profiles, and alert statuses.
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
            placeholder="Search by license plate, make, model, owner..."
            className="bg-transparent border-none text-xs w-full focus:outline-none placeholder-slate-400 font-sans"
          />
        </div>

        {/* Status */}
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 rounded outline-none shrink-0"
        >
          <option value="all">All Watchlist States</option>
          <option value="Flagged">Flagged</option>
          <option value="Under Investigation">Under Investigation</option>
          <option value="Seized">Seized</option>
          <option value="Clean">Clean State</option>
        </select>
      </div>

      {/* Vehicle Registry Table */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-400 font-mono text-[10px] uppercase">
                <th className="py-3 px-4 font-semibold">License Plate</th>
                <th className="py-3 px-4 font-semibold">Make & Model</th>
                <th className="py-3 px-4 font-semibold">Registered Owner</th>
                <th className="py-3 px-4 font-semibold">Last CCTV Location</th>
                <th className="py-3 px-4 font-semibold font-mono">Last Scanned Time</th>
                <th className="py-3 px-4 font-semibold">Monitor Status</th>
                <th className="py-3 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredVehicles.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-slate-400 font-sans">
                    No matching transport assets in KSP watchlist
                  </td>
                </tr>
              ) : (
                filteredVehicles.map((vehicle) => {
                  const lastLog = vehicle.anprLogs[0];
                  return (
                    <tr
                      key={vehicle.id}
                      onClick={() => setSelectedVehicle(vehicle)}
                      className="hover:bg-slate-50/70 transition-colors cursor-pointer"
                    >
                      <td className="py-3 px-4 font-mono font-bold text-brand-primary text-sm">{vehicle.id}</td>
                      <td className="py-3 px-4 font-semibold text-slate-700">
                        {vehicle.color} {vehicle.make} {vehicle.model}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          onClick={(e) => handleOpenOwner(vehicle.ownerName, e)}
                          className="font-bold text-slate-700 hover:underline cursor-pointer"
                        >
                          {vehicle.ownerName}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-600">
                        {lastLog ? (
                          <span className="flex items-center gap-1">
                            <Camera className="w-3.5 h-3.5 text-slate-400" />
                            {lastLog.locationName}
                          </span>
                        ) : 'No scans logged'}
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-500">
                        {lastLog ? new Date(lastLog.timestamp).toLocaleString() : 'N/A'}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-block px-1.5 py-0.5 rounded text-[9px] font-bold font-mono ${
                          vehicle.status === 'Flagged' ? 'bg-red-50 text-red-700 border border-red-200' :
                          vehicle.status === 'Under Investigation' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
                          'bg-slate-100 text-slate-700 border border-slate-200'
                        }`}>
                          {vehicle.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex gap-2 justify-end">
                          <button
                            onClick={(e) => handleAnalyze(vehicle.id, e)}
                            className="py-1 px-2.5 bg-brand-secondary text-brand-primary font-bold text-[10px] rounded hover:bg-brand-secondary/90 transition-all cursor-pointer"
                          >
                            AI Track
                          </button>
                          <button
                            onClick={() => setSelectedVehicle(vehicle)}
                            className="py-1 px-2.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 rounded font-semibold text-[10px] transition-all inline-flex items-center gap-1 cursor-pointer"
                          >
                            <Eye className="w-3.5 h-3.5" /> Tracker
                          </button>
                        </div>
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
export default Vehicles;
