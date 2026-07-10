import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import {
  FIRs,
  SUSPECTS,
  VEHICLES,
  CCTV_RECORDS
} from '../../services/mockDb';
import { MapWidget } from '../../components/ui/MapWidget';
import type { MapMarker } from '../../components/ui/MapWidget';
import { EChart } from '../../components/ui/EChart';
import {
  FolderLock,
  UserCheck,
  Car,
  Activity,
  ArrowRight,
  TrendingUp,
  Cpu,
  Search,
  Eye
} from 'lucide-react';

// Custom lightweight counter hook for React 19 compatibility
const useCountUp = (target: number, duration: number = 800) => {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = 0;
    const end = target;
    if (start === end) return;
    const incrementTime = Math.floor(duration / end) || 10;
    const timer = setInterval(() => {
      start += 1;
      setCount(start);
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      }
    }, incrementTime);
    return () => clearInterval(timer);
  }, [target, duration]);
  return count;
};

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { setAiQuery, setSelectedFir, language, addToast } = useApp();
  const [quickQueryText, setQuickQueryText] = useState('');

  const handleQuickInvestigate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickQueryText.trim()) return;
    setAiQuery(quickQueryText);
    navigate('/ai-workspace');
  };

  const triggerSampleQuery = (text: string) => {
    setAiQuery(text);
    navigate('/ai-workspace');
  };

  // KPI calculations
  const totalFirs = FIRs.length;
  const abscondingSuspects = SUSPECTS.filter((s) => s.status === 'Absconding').length;
  const totalAnprScans = VEHICLES.reduce((acc, v) => acc + v.anprLogs.length, 0);
  const operationalCctv = CCTV_RECORDS.filter((c) => c.status === 'Operational').length;

  // Bound animated count values
  const countFirs = useCountUp(totalFirs);
  const countAbsconding = useCountUp(abscondingSuspects);
  const countAnpr = useCountUp(totalAnprScans);
  const countCctv = useCountUp(operationalCctv);

  // Dynamic Live log state
  const [logs, setLogs] = useState([
    { id: 1, type: 'ANPR', msg: 'KA05MJ4421 spotted at Koramangala 80ft Road', time: '19:40', status: 'critical' },
    { id: 2, type: 'TELECOM', msg: 'Call link: Vikram Hegde to Suresh Gowda (240s)', time: '17:10', status: 'major' },
    { id: 3, type: 'ANPR', msg: 'KA51MD9876 detected at Indiranagar 100ft Road', time: '17:30', status: 'moderate' },
    { id: 4, type: 'SYS', msg: 'Inspector Rajesh Kumar signed into Terminal A', time: '15:30', status: 'normal' },
  ]);

  useEffect(() => {
    const logInterval = setInterval(() => {
      const mockPings = [
        { type: 'ANPR', msg: 'KA05MJ4421 pinged Majestic Metro Junction CCTV', status: 'critical' },
        { type: 'ANPR', msg: 'KA51MD9876 detected approaching Koramangala block', status: 'moderate' },
        { type: 'TELECOM', msg: 'Intercept: Suresh Gowda linked to cell tower TWR-jn-02', status: 'major' },
        { type: 'ANPR', msg: 'KA03MH1122 Toll cross at Hosur Road Plaza', status: 'normal' },
        { type: 'BIOMETRIC', msg: 'Iris recognition match: Kiran Kumar at Majestic Transit Hub', status: 'critical' },
      ];
      const selectRandom = mockPings[Math.floor(Math.random() * mockPings.length)];
      const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      setLogs((prev) => [
        { id: Date.now(), type: selectRandom.type, msg: selectRandom.msg, time: timestamp, status: selectRandom.status },
        ...prev.slice(0, 4) // keep max 5 logs in view
      ]);

      // Add toast
      if (selectRandom.status === 'critical') {
        addToast(`CRITICAL ALERT: ${selectRandom.msg}`, 'error');
      } else if (selectRandom.status === 'major') {
        addToast(`Telemetry Log: ${selectRandom.msg}`, 'warn');
      }
    }, 8500); // 8.5s interval updates live feed

    return () => clearInterval(logInterval);
  }, [addToast]);

  // Map markers from FIRs
  const mapMarkers: MapMarker[] = FIRs.map((fir) => ({
    id: fir.id,
    position: [fir.latitude, fir.longitude],
    title: fir.id,
    description: `${fir.category} - ${fir.locationName}`,
    severity: fir.severity,
    onClick: () => setSelectedFir(fir)
  }));

  // EChart options
  const weeklyTrendOption = {
    grid: { top: 30, right: 10, bottom: 30, left: 40 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category' as const,
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { style: { color: '#64748b', fontSize: 10 } }
    },
    yAxis: {
      type: 'value' as const,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { style: { color: '#64748b', fontSize: 10 } }
    },
    series: [
      {
        name: 'Cases Filed',
        type: 'bar',
        barWidth: '40%',
        itemStyle: {
          color: echartColorGradient()
        },
        data: [4, 6, 2, 8, 5, 9, 3]
      }
    ]
  };

  function echartColorGradient() {
    return {
      type: 'linear',
      x: 0, y: 0, x2: 0, y2: 1,
      colorStops: [
        { offset: 0, color: '#1e3a5f' }, // brand-primary-light
        { offset: 1, color: '#0f1e36' }  // brand-primary
      ]
    };
  }

  return (
    <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto select-none">
      {/* ======================================================== */}
      {/* ROW 1: KPI STATS CARDS */}
      {/* ======================================================== */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Stat Card 1 */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 flex flex-col justify-between shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-[10px] text-slate-400 font-mono tracking-widest block uppercase">
                {language === 'en' ? 'TOTAL ACTIVE CASES' : 'ಒಟ್ಟು ದಾಖಲಾದ ಪ್ರಕರಣಗಳು'}
              </span>
              <span className="text-2xl font-bold text-brand-primary block mt-1">{countFirs}</span>
            </div>
            <div className="p-2 bg-slate-50 border border-slate-100 rounded-lg text-brand-primary">
              <FolderLock className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[10px] text-emerald-650 font-semibold flex items-center gap-0.5">
              <TrendingUp className="w-3.5 h-3.5" /> +15% {language === 'en' ? 'vs Last Mo' : 'ಹಿಂದಿನ ತಿಂಗಳು'}
            </span>
            <svg viewBox="0 0 100 30" className="w-20 h-8 text-emerald-500 shrink-0">
              <path d="M 0 25 Q 20 10 40 20 T 80 5 T 100 15" fill="none" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>
        </div>

        {/* Stat Card 2 */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 flex flex-col justify-between shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-[10px] text-slate-400 font-mono tracking-widest block uppercase">
                {language === 'en' ? 'ABSCONDING SUSPECTS' : 'ತಲೆಮರೆಸಿಕೊಂಡಿರುವ ಅಪರಾಧಿಗಳು'}
              </span>
              <span className="text-2xl font-bold text-brand-primary block mt-1">{countAbsconding}</span>
            </div>
            <div className="p-2 bg-slate-50 border border-slate-100 rounded-lg text-brand-primary">
              <UserCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[10px] text-red-600 font-bold bg-red-50 border border-red-200 px-1.5 py-0.5 rounded uppercase animate-pulse">
              {language === 'en' ? 'Critical Watch' : 'ಹೆಚ್ಚಿನ ಗಮನ'}
            </span>
            <svg viewBox="0 0 100 30" className="w-20 h-8 text-red-400 shrink-0">
              <path d="M 0 5 Q 30 25 60 10 T 100 25" fill="none" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>
        </div>

        {/* Stat Card 3 */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 flex flex-col justify-between shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-[10px] text-slate-400 font-mono tracking-widest block uppercase">
                {language === 'en' ? 'ANPR PLATE SCANS' : 'ಎಎನ್‌ಪಿಆರ್ ವಾಹನ ಸ್ಕ್ಯಾನ್‌ಗಳು'}
              </span>
              <span className="text-2xl font-bold text-brand-primary block mt-1">{countAnpr}</span>
            </div>
            <div className="p-2 bg-slate-50 border border-slate-100 rounded-lg text-brand-primary">
              <Car className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[10px] text-slate-550 font-mono font-bold uppercase">
              {language === 'en' ? 'Active ANPR Array' : 'ಕಾರ್ಯಕಾರಿ ಎಎನ್‌ಪಿಆರ್'}
            </span>
            <svg viewBox="0 0 100 30" className="w-20 h-8 text-slate-400 shrink-0">
              <path d="M 0 20 Q 20 20 40 10 T 80 25 T 100 5" fill="none" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>
        </div>

        {/* Stat Card 4 */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 flex flex-col justify-between shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-[10px] text-slate-400 font-mono tracking-widest block uppercase">
                {language === 'en' ? 'CCTV CAMERA NODES' : 'ಸಿಸಿಟಿವಿ ನೆಟ್‌ವರ್ಕ್'}
              </span>
              <span className="text-2xl font-bold text-brand-primary block mt-1">{countCctv}</span>
            </div>
            <div className="p-2 bg-slate-50 border border-slate-100 rounded-lg text-brand-primary">
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[10px] text-emerald-600 font-bold uppercase">
              100% {language === 'en' ? 'Operational' : 'ಕಾರ್ಯಕಾರಿ'}
            </span>
            <div className="flex gap-0.5 items-end h-5">
              <span className="w-1.5 h-2 bg-emerald-300 rounded-t-xs"></span>
              <span className="w-1.5 h-4 bg-emerald-400 rounded-t-xs"></span>
              <span className="w-1.5 h-3 bg-emerald-300 rounded-t-xs"></span>
              <span className="w-1.5 h-5 bg-emerald-500 rounded-t-xs animate-pulse"></span>
            </div>
          </div>
        </div>
      </div>

      {/* ======================================================== */}
      {/* ROW 2: COPILOT PANEL & GIS MAP + LIVE ALERTS */}
      {/* ======================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Side: Copilot widget + Map */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* AI Investigation Widget */}
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Cpu className="w-5 h-5 text-brand-secondary" />
              <h2 className="text-sm font-bold text-brand-primary uppercase tracking-wider">
                {language === 'en' ? 'AI Investigation Copilot' : 'ಎಐ ತನಿಖಾ ಕೋ-ಪೈಲಟ್'}
              </h2>
            </div>
            <p className="text-xs text-slate-500 leading-normal">
              {language === 'en'
                ? 'Enter natural language prompts to scan VAHAN registries, cell towers, biometrics, and FIR databases.'
                : 'ವಾಹನ ನೋಂದಣಿ, ಸೆಲ್ ಗೋಪುರಗಳು, ಮತ್ತು ಎಫ್‌ಐಆರ್ ಡೇಟಾಬೇಸ್‌ಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಲು ತನಿಖಾ ಪ್ರಶ್ನೆಯನ್ನು ನಮೂದಿಸಿ.'}
            </p>

            <form onSubmit={handleQuickInvestigate} className="mt-4 flex gap-2">
              <div className="flex-1 flex items-center border border-slate-200 focus-within:border-brand-secondary focus-within:ring-2 focus-within:ring-brand-secondary/20 rounded bg-slate-50 px-3 py-1.5 transition-all">
                <Search className="w-4 h-4 text-slate-400 mr-2 shrink-0" />
                <input
                  type="text"
                  value={quickQueryText}
                  onChange={(e) => setQuickQueryText(e.target.value)}
                  placeholder={language === 'en' ? 'Search vehicle license, suspect names...' : 'ವಾಹನ ಸಂಖ್ಯೆ ಅಥವಾ ಶಂಕಿತರ ಹೆಸರು ನಮೂದಿಸಿ...'}
                  className="bg-transparent border-none text-xs w-full focus:outline-none placeholder-slate-400 font-sans"
                />
              </div>
              <button
                type="submit"
                className="bg-brand-primary hover:bg-brand-primary-light text-white font-bold text-xs px-5 py-2 rounded transition-colors cursor-pointer"
              >
                {language === 'en' ? 'Investigate' : 'ವಿಶ್ಲೇಷಿಸಿ'}
              </button>
            </form>

            <div className="mt-3.5 flex flex-wrap gap-2 items-center text-xs">
              <span className="text-slate-450 font-medium">Quick Queries:</span>
              <button
                onClick={() => triggerSampleQuery('Find all suspects connected with vehicle KA05MJ4421')}
                className="px-2 py-0.5 bg-slate-100 hover:bg-slate-250 border border-slate-200 rounded font-mono text-[9px] text-brand-primary transition-all cursor-pointer"
              >
                Vehicle KA05MJ4421
              </button>
              <button
                onClick={() => triggerSampleQuery('Find cases linked with suspect Vikram Hegde')}
                className="px-2 py-0.5 bg-slate-100 hover:bg-slate-250 border border-slate-200 rounded font-mono text-[9px] text-brand-primary transition-all cursor-pointer"
              >
                Vikram Hegde (Syndicate Leader)
              </button>
            </div>
          </div>

          {/* Mini Crime Map Container */}
          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex flex-col gap-3">
            <div className="flex justify-between items-center border-b border-slate-100 pb-2">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-brand-secondary" />
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  {language === 'en' ? 'ACTIVE INCIDENT RADAR (BENGALURU)' : 'ಸಕ್ರಿಯ ಪ್ರಕರಣ ನಕ್ಷೆ (ಬೆಂಗಳೂರು)'}
                </h3>
              </div>
              <button
                onClick={() => navigate('/map')}
                className="text-[10px] text-brand-secondary font-bold hover:underline flex items-center gap-0.5 cursor-pointer uppercase"
              >
                View Fullscreen Map <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="h-[280px]">
              <MapWidget center={[12.9345, 77.6268]} zoom={12} markers={mapMarkers} height="280px" />
            </div>
          </div>
        </div>

        {/* Right Side: Live Incident Feed */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex flex-col h-full justify-between">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                {language === 'en' ? 'OPERATIONAL LOG FEED' : 'ಲೈವ್ ಘಟನೆಗಳ ಲಾಗ್'}
              </h3>
            </div>
            <div className="flex flex-col gap-3 overflow-y-auto max-h-[360px] pr-1">
              {logs.map((log) => (
                <div key={log.id} className="p-3 border border-slate-100 rounded bg-slate-50 flex items-start gap-3 text-xs leading-normal animate-in fade-in slide-in-from-top-1 duration-300">
                  <div className={`mt-1.5 w-1.5 h-1.5 rounded-full shrink-0 ${
                    log.status === 'critical' ? 'bg-red-600 animate-ping' :
                    log.status === 'major' ? 'bg-orange-500' :
                    log.status === 'moderate' ? 'bg-amber-400' :
                    'bg-slate-400'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-center gap-2">
                      <span className="font-mono text-[9px] font-bold text-slate-400 uppercase tracking-wider">{log.type}</span>
                      <span className="font-mono text-[9px] text-slate-400">{log.time}</span>
                    </div>
                    <p className="text-slate-700 font-sans mt-0.5 text-[11px] font-medium leading-normal">{log.msg}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="border-t border-slate-100 pt-3 mt-4 text-center">
            <span className="text-[10px] text-slate-400 font-mono">
              SYSTEM ENCRYPTED: KSP-NET-SECURE
            </span>
          </div>
        </div>
      </div>

      {/* ======================================================== */}
      {/* ROW 3: RECENT CASES TABLE & WEEKLY BAR CHART */}
      {/* ======================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Table: Recent Cases */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col gap-4">
          <div className="flex justify-between items-center border-b border-slate-100 pb-2">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <FolderLock className="w-4.5 h-4.5 text-brand-primary" />
              {language === 'en' ? 'RECENT REGISTERED FIRs' : 'ಇತ್ತೀಚಿನ ಎಫ್‌ಐಆರ್ ದಾಖಲೆಗಳು'}
            </h3>
            <button
              onClick={() => navigate('/cases')}
              className="text-[10px] text-brand-secondary font-bold hover:underline flex items-center gap-0.5 cursor-pointer uppercase"
            >
              Go to Cases Ledger <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 font-mono text-[10px] uppercase">
                  <th className="py-2.5 font-semibold">FIR Number</th>
                  <th className="py-2.5 font-semibold">Incident Type</th>
                  <th className="py-2.5 font-semibold">Registered</th>
                  <th className="py-2.5 font-semibold">Severity</th>
                  <th className="py-2.5 font-semibold">Status</th>
                  <th className="py-2.5 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {FIRs.map((fir) => (
                  <tr key={fir.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 font-mono font-bold text-brand-primary">{fir.id}</td>
                    <td className="py-3 font-semibold text-slate-700">{fir.category}</td>
                    <td className="py-3 font-mono text-slate-500">{new Date(fir.registrationDate).toLocaleDateString()}</td>
                    <td className="py-3">
                      <span className={`inline-block px-1.5 py-0.5 rounded text-[9px] font-bold font-mono ${
                        fir.severity === 'Critical' ? 'bg-red-50 text-red-700 border border-red-200' :
                        fir.severity === 'Major' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
                        'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}>
                        {fir.severity}
                      </span>
                    </td>
                    <td className="py-3 font-semibold">
                      <span className={`text-[10px] ${
                        fir.status === 'Active' ? 'text-brand-accent' : 'text-slate-500'
                      }`}>
                        {fir.status}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => setSelectedFir(fir)}
                        className="py-1 px-2.5 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded font-bold text-[10px] text-slate-700 flex items-center gap-1 ml-auto cursor-pointer"
                      >
                        <Eye className="w-3.5 h-3.5" /> Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Weekly Trend Bar Chart */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col gap-4">
          <div className="border-b border-slate-100 pb-2">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              {language === 'en' ? 'WEEKLY CASE FILINGS' : 'ವಾರದ ಪ್ರಕರಣಗಳ ಪ್ರವೃತ್ತಿ'}
            </h3>
          </div>
          <div className="h-[220px]">
            <EChart option={weeklyTrendOption} style={{ height: '220px' }} />
          </div>
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
