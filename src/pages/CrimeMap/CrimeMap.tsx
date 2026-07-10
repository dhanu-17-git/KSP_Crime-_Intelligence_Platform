import React, { useState, useMemo } from 'react';
import { useApp } from '../../context/AppContext';
import { FIRs, DISTRICTS, POLICE_STATIONS, CCTV_RECORDS } from '../../services/mockDb';
import { MapWidget } from '../../components/ui/MapWidget';
import type { MapMarker } from '../../components/ui/MapWidget';
import { Filter, RefreshCw, Layers } from 'lucide-react';

export const CrimeMap: React.FC = () => {
  const { selectedDistrictId, setSelectedDistrictId, setSelectedFir, language } = useApp();

  // Filters State
  const [selectedStation, setSelectedStation] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  // Layer Overlays
  const [showCctvLayer, setShowCctvLayer] = useState(false);
  const [showHeatmap, setShowHeatmap] = useState(false);

  // Dropdown list categories
  const categories = useMemo(() => {
    return Array.from(new Set(FIRs.map((f) => f.category)));
  }, []);

  // Filtered FIRs
  const filteredFirs = useMemo(() => {
    return FIRs.filter((f) => {
      // District Filter
      if (selectedDistrictId !== 'all') {
        const ps = POLICE_STATIONS.find((p) => p.id === f.stationId);
        if (!ps || ps.districtId !== selectedDistrictId) return false;
      }
      // Police Station Filter
      if (selectedStation !== 'all' && f.stationId !== selectedStation) return false;
      // Category Filter
      if (selectedCategory !== 'all' && f.category !== selectedCategory) return false;
      // Severity Filter
      if (selectedSeverity !== 'all' && f.severity !== selectedSeverity) return false;
      // Date Range
      if (dateFrom && new Date(f.registrationDate) < new Date(dateFrom)) return false;
      if (dateTo && new Date(f.registrationDate) > new Date(dateTo)) return false;

      return true;
    });
  }, [selectedDistrictId, selectedStation, selectedCategory, selectedSeverity, dateFrom, dateTo]);

  // Reset all filters
  const resetFilters = () => {
    setSelectedDistrictId('all');
    setSelectedStation('all');
    setSelectedCategory('all');
    setSelectedSeverity('all');
    setDateFrom('');
    setDateTo('');
  };

  // Convert filtered FIRs and CCTV overlays to Map Markers
  const mapMarkers = useMemo((): MapMarker[] => {
    const casePins: MapMarker[] = filteredFirs.map((fir) => ({
      id: fir.id,
      position: [fir.latitude, fir.longitude],
      title: fir.id,
      description: `<b>Type:</b> ${fir.category}<br/><b>Jurisdiction:</b> ${fir.locationName}<br/><b>IPC:</b> ${fir.ipcSections.join(', ')}`,
      severity: fir.severity,
      onClick: () => setSelectedFir(fir)
    }));

    if (showCctvLayer) {
      // Filter CCTVs by district if selected
      const filteredCctvs = CCTV_RECORDS.filter(c => {
        if (selectedDistrictId === 'all') return true;
        return c.id.toLowerCase().includes(selectedDistrictId.toLowerCase()) || c.locationName.toLowerCase().includes(selectedDistrictId.toLowerCase());
      });

      const cctvPins: MapMarker[] = filteredCctvs.map((cctv) => ({
        id: cctv.id,
        position: [cctv.latitude, cctv.longitude],
        title: `CCTV Hub: ${cctv.id}`,
        description: `<b>Location:</b> ${cctv.locationName}<br/><b>Status:</b> ${cctv.status}<br/><b>Grid Connection:</b> Operational`,
        severity: 'Minor', // minor displays as slate blue default in MapWidget
        onClick: () => {}
      }));
      return [...casePins, ...cctvPins];
    }

    return casePins;
  }, [filteredFirs, setSelectedFir, showCctvLayer, selectedDistrictId]);

  // Dynamic Map center focus based on selected items
  const mapCenter: [number, number] = useMemo(() => {
    if (filteredFirs.length > 0) {
      return [filteredFirs[0].latitude, filteredFirs[0].longitude];
    }
    return [12.9345, 77.6268]; // Bengaluru center
  }, [filteredFirs]);

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col md:flex-row overflow-hidden select-none">
      
      {/* FILTER CONTROL PANEL SIDEBAR */}
      <div className="w-full md:w-80 bg-white border-r border-slate-200 flex flex-col p-5 shrink-0 overflow-y-auto justify-between">
        <div className="flex flex-col gap-5">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <div className="flex items-center gap-2">
              <Filter className="w-4.5 h-4.5 text-brand-primary" />
              <h2 className="text-xs font-bold text-brand-primary uppercase tracking-wider">
                {language === 'en' ? 'Incident Filters' : 'ಶೋಧಕ ನಿಯಂತ್ರಣಗಳು'}
              </h2>
            </div>
            <button
              onClick={resetFilters}
              className="p-1 hover:bg-slate-100 border border-transparent hover:border-slate-200 rounded text-slate-400 hover:text-slate-700 transition-all cursor-pointer"
              title="Reset Filters"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Form Fields */}
          <div className="flex flex-col gap-4 text-xs">
            {/* District */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold text-slate-600">District Boundary</label>
              <select
                value={selectedDistrictId}
                onChange={(e) => {
                  setSelectedDistrictId(e.target.value);
                  setSelectedStation('all'); // Reset sub-station
                }}
                className="w-full p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 focus:bg-white rounded outline-none"
              >
                <option value="all">All Karnataka Districts</option>
                {DISTRICTS.map((d) => (
                  <option key={d.id} value={d.id}>{d.name} ({d.code})</option>
                ))}
              </select>
            </div>

            {/* Police Station */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold text-slate-600">Police Station (PS)</label>
              <select
                value={selectedStation}
                onChange={(e) => setSelectedStation(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 focus:bg-white rounded outline-none"
              >
                <option value="all">All Jurisdictions</option>
                {POLICE_STATIONS.filter((ps) => selectedDistrictId === 'all' || ps.districtId === selectedDistrictId).map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            {/* Crime Category */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold text-slate-600">Crime Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 focus:bg-white rounded outline-none"
              >
                <option value="all">All Classifications</option>
                {categories.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            {/* Severity */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold text-slate-600">Severity Threshold</label>
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 focus:border-slate-400 focus:bg-white rounded outline-none"
              >
                <option value="all">All Priorities</option>
                <option value="Critical">Critical Priority</option>
                <option value="Major">Major Priority</option>
                <option value="Moderate">Moderate Priority</option>
                <option value="Minor">Minor Priority</option>
              </select>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-2">
              <div className="flex flex-col gap-1">
                <label className="font-semibold text-slate-600">Date From</label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="w-full p-1.5 bg-slate-50 border border-slate-200 focus:border-slate-400 focus:bg-white rounded outline-none font-mono text-[11px]"
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="font-semibold text-slate-600">Date To</label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="w-full p-1.5 bg-slate-50 border border-slate-200 focus:border-slate-400 focus:bg-white rounded outline-none font-mono text-[11px]"
                />
              </div>
            </div>

            {/* Layer Toggles */}
            <div className="flex flex-col gap-2.5 bg-slate-50 border border-slate-200 rounded-lg p-3 mt-1">
              <span className="text-[10px] text-slate-450 font-mono tracking-wider block font-semibold uppercase leading-none mb-1">
                Layer Controls
              </span>
              <div className="flex flex-col gap-2.5 text-xs text-slate-700">
                <label className="flex items-center gap-2.5 cursor-pointer font-semibold">
                  <input
                    type="checkbox"
                    checked={showCctvLayer}
                    onChange={(e) => setShowCctvLayer(e.target.checked)}
                    className="rounded border-slate-350 text-brand-primary focus:ring-brand-primary"
                  />
                  <span>CCTV Grid Nodes</span>
                </label>
                <label className="flex items-center gap-2.5 cursor-pointer font-semibold">
                  <input
                    type="checkbox"
                    checked={showHeatmap}
                    onChange={(e) => setShowHeatmap(e.target.checked)}
                    className="rounded border-slate-350 text-brand-primary focus:ring-brand-primary"
                  />
                  <span>Incident Hotspot Circles</span>
                </label>
              </div>
            </div>

          </div>
        </div>

        {/* Info telemetry footer */}
        <div className="border-t border-slate-100 pt-4 flex flex-col gap-2 text-[10px] text-slate-400 font-mono mt-6">
          <div className="flex justify-between">
            <span>FILTER HITCOUNT</span>
            <span className="font-bold text-brand-primary">{filteredFirs.length} Cases</span>
          </div>
          <div className="flex justify-between">
            <span>LAYER CACHE</span>
            <span className="text-emerald-500 font-bold">98% OPTIMIZED</span>
          </div>
        </div>
      </div>

      {/* MAP AND INCIDENT LIST SPLIT VIEW */}
      <div className="flex-1 flex flex-col md:flex-row relative">
        {/* Fullscreen Map container */}
        <div className="flex-1 h-full relative z-10">
          <MapWidget center={mapCenter} zoom={filteredFirs.length > 0 ? 13 : 8} markers={mapMarkers} height="100%" showHeatmap={showHeatmap} />
        </div>

        {/* Small slideable Sidebar listing matching Incidents */}
        <div className="w-full md:w-80 bg-white border-l border-slate-200 flex flex-col h-full z-20 overflow-hidden shadow-xl shrink-0">
          <div className="p-4 border-b border-slate-100 flex items-center gap-2 shrink-0">
            <Layers className="w-4 h-4 text-brand-primary" />
            <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">Filtered Case Ledger</span>
          </div>
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
            {filteredFirs.length === 0 ? (
              <div className="text-center py-10 text-xs text-slate-400">
                No matching incidents in this region
              </div>
            ) : (
              filteredFirs.map((fir) => (
                <div
                  key={fir.id}
                  onClick={() => setSelectedFir(fir)}
                  className="p-3 border border-slate-200 hover:border-slate-300 rounded cursor-pointer bg-slate-50/50 hover:bg-slate-50 transition-all flex flex-col gap-1 animate-in fade-in duration-200"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-mono font-bold text-brand-primary hover:underline">{fir.id}</span>
                    <span className={`px-1 py-0.5 rounded text-[8px] font-bold font-mono ${
                      fir.severity === 'Critical' ? 'bg-red-100 text-red-700' : 'bg-slate-200 text-slate-700'
                    }`}>
                      {fir.severity}
                    </span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-700 mt-1">{fir.category}</h4>
                  <p className="text-[10px] text-slate-500 font-mono mt-0.5">{fir.locationName}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

    </div>
  );
};
export default CrimeMap;
