import React from 'react';
import { EChart } from '../../components/ui/EChart';
import { BarChart3, Download, RefreshCw, Eye, ShieldAlert } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { DISTRICTS } from '../../services/mockDb';

export const Analytics: React.FC = () => {
  const { selectedDistrictId, setSelectedDistrictId, language } = useApp();

  // Dynamic scaling factor representing district load index
  const getScaleFactor = (distId: string) => {
    if (distId === 'blr') return 0.65;
    if (distId === 'mys') return 0.20;
    if (distId === 'mng') return 0.12;
    if (distId === 'bel') return 0.08;
    return 1.0;
  };

  const scale = getScaleFactor(selectedDistrictId);

  // Chart 1: Crime Categories Donut Chart
  const categoryDonutOption = {
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
    legend: { bottom: '0%', left: 'center', textStyle: { color: '#64748b', fontSize: 10 } },
    series: [
      {
        name: 'Classification',
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 12, fontWeight: 'bold' } },
        data: [
          { value: Math.round(45 * scale), name: 'Armed Robbery', itemStyle: { color: '#0f1e36' } },
          { value: Math.round(30 * scale), name: 'Vehicle Theft', itemStyle: { color: '#1e3a5f' } },
          { value: Math.round(15 * scale), name: 'Extortion', itemStyle: { color: '#b89020' } },
          { value: Math.round(8 * scale), name: 'Smuggling', itemStyle: { color: '#cbd5e1' } },
          { value: Math.round(12 * scale), name: 'Cyber Fraud', itemStyle: { color: '#b91c1c' } }
        ]
      }
    ]
  };

  // Chart 2: 6-Month Volatility Trend Area Chart
  const trendAreaOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { style: { color: '#64748b', fontSize: 10 } }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { style: { color: '#64748b', fontSize: 10 } }
    },
    series: [
      {
        name: 'Reported Incidents',
        type: 'line',
        smooth: true,
        lineStyle: { width: 3, color: '#0f1e36' },
        showSymbol: false,
        areaStyle: {
          opacity: 0.1,
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#0f1e36' },
              { offset: 1, color: '#ffffff' }
            ]
          }
        },
        data: [120, 135, 110, 160, 145, 188].map(v => Math.round(v * scale))
      }
    ]
  };

  // Chart 3: Horizontal Bar Chart of District Loading
  const districtBarOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '5%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { style: { color: '#64748b', fontSize: 10 } }
    },
    yAxis: {
      type: 'category',
      data: ['Kalaburagi', 'Belagavi', 'Hubballi', 'Mangaluru', 'Mysuru', 'Bengaluru'],
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      axisLabel: { style: { color: '#64748b', fontSize: 10 } }
    },
    series: [
      {
        name: 'Case Count',
        type: 'bar',
        barWidth: '55%',
        itemStyle: {
          color: '#1e3a5f',
          borderRadius: [0, 4, 4, 0]
        },
        data: [12, 19, 25, 34, 42, 112].map(v => Math.round(v * scale))
      }
    ]
  };

  // Chart 4: Radar Threat Matrix
  const threatRadarOption = {
    tooltip: { trigger: 'item' },
    radar: {
      indicator: [
        { name: 'Financial Capital', max: 100 },
        { name: 'Logistical Range', max: 100 },
        { name: 'Cell Tower Ties', max: 100 },
        { name: 'Violent Record', max: 100 },
        { name: 'Weapon Capability', max: 100 }
      ],
      axisName: { textStyle: { color: '#64748b', fontSize: 10 } },
      splitArea: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    series: [
      {
        name: 'Syndicate Profile',
        type: 'radar',
        data: [
          {
            value: [80, 50, 90, 60, 45].map(v => Math.round(v * scale)),
            name: 'Hegde Network',
            itemStyle: { color: '#0f1e36' },
            areaStyle: { opacity: 0.15, color: '#0f1e36' }
          },
          {
            value: [40, 60, 35, 80, 75].map(v => Math.round(v * scale)),
            name: 'Gowda Network',
            itemStyle: { color: '#b89020' },
            areaStyle: { opacity: 0.15, color: '#b89020' }
          }
        ]
      }
    ]
  };

  return (
    <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto select-none">
      {/* Title block */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-brand-primary" />
            <h1 className="text-sm font-bold text-brand-primary uppercase tracking-wider">
              {language === 'en' ? 'Crime Analytics Centre' : 'ವಿಶ್ಲೇಷಣಾ ಕೇಂದ್ರ'}
            </h1>
          </div>
          <p className="text-xs text-slate-500 font-sans mt-1">
            State-wide telemetry trends, load rates, and threat matrix evaluations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Global District filter */}
          <select
            value={selectedDistrictId}
            onChange={(e) => setSelectedDistrictId(e.target.value)}
            className="p-1.5 bg-white border border-slate-200 text-xs font-semibold rounded text-slate-700 outline-none focus:border-slate-400"
          >
            <option value="all">All Karnataka Districts</option>
            {DISTRICTS.map((d) => (
              <option key={d.id} value={d.id}>{d.name} ({d.code})</option>
            ))}
          </select>

          <button className="py-1.5 px-3 bg-white border border-slate-200 hover:bg-slate-50 text-xs font-semibold rounded text-slate-700 flex items-center gap-1.5 transition-all cursor-pointer">
            <RefreshCw className="w-3.5 h-3.5" /> Synchronize Logs
          </button>
          <button className="py-1.5 px-3 bg-brand-primary hover:bg-brand-primary-light text-white font-bold text-xs rounded flex items-center gap-1.5 transition-all cursor-pointer shadow-sm">
            <Download className="w-3.5 h-3.5 text-brand-secondary" /> Export Sheets
          </button>
        </div>
      </div>

      {/* Analytics Summary Stats widget */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div className="flex items-start gap-3 border-r border-slate-100 last:border-r-0 pr-4">
          <div className="p-2 bg-slate-50 border border-slate-100 rounded text-brand-primary mt-1">
            <ShieldAlert className="w-4.5 h-4.5" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 font-mono tracking-wide uppercase">Operational Risk Index</span>
            <h4 className="text-sm font-bold text-slate-800 mt-0.5">
              {Math.round(82 * (scale >= 1 ? 1 : scale + 0.2))} / 100 High Alert
            </h4>
            <p className="text-[10.5px] text-slate-500 mt-1">Spike in highway hijacks logged over South Range sector.</p>
          </div>
        </div>
        <div className="flex items-start gap-3 border-r border-slate-100 last:border-r-0 pr-4">
          <div className="p-2 bg-slate-50 border border-slate-100 rounded text-brand-primary mt-1">
            <Eye className="w-4.5 h-4.5" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 font-mono tracking-wide uppercase">Weekly Capture rate</span>
            <h4 className="text-sm font-bold text-slate-800 mt-0.5">68% Suspect Apprehension</h4>
            <p className="text-[10.5px] text-slate-500 mt-1">4 of 6 flagged vehicles detained at outer city checkpoints.</p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="p-2 bg-slate-50 border border-slate-100 rounded text-brand-primary mt-1">
            <BarChart3 className="w-4.5 h-4.5" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 font-mono tracking-wide uppercase">Active Patrol Coverage</span>
            <h4 className="text-sm font-bold text-slate-800 mt-0.5">92% Sector Dispatch</h4>
            <p className="text-[10.5px] text-slate-500 mt-1">98 GPS-enabled highway cruisers sync live with central KSP net.</p>
          </div>
        </div>
      </div>

      {/* ECharts Grids (2x2 Layout) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Card 1: Donut Chart */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm">
          <div className="border-b border-slate-100 pb-2 mb-4 flex justify-between items-center">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Crime Classifications Distribution</h3>
            <span className="text-[10px] text-slate-400 font-mono">GLOBAL SHARE</span>
          </div>
          <div className="h-[280px]">
            <EChart option={categoryDonutOption} style={{ height: '280px' }} />
          </div>
        </div>

        {/* Card 2: Smooth Area Chart */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm">
          <div className="border-b border-slate-100 pb-2 mb-4 flex justify-between items-center">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">6-Month Crime Volatility Trend</h3>
            <span className="text-[10px] text-slate-400 font-mono">STATEWIDE</span>
          </div>
          <div className="h-[280px]">
            <EChart option={trendAreaOption} style={{ height: '280px' }} />
          </div>
        </div>

        {/* Card 3: Horizontal Bar Chart */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm">
          <div className="border-b border-slate-100 pb-2 mb-4 flex justify-between items-center">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Jurisdiction Workload Index</h3>
            <span className="text-[10px] text-slate-400 font-mono">BY DISTRICT</span>
          </div>
          <div className="h-[280px]">
            <EChart option={districtBarOption} style={{ height: '280px' }} />
          </div>
        </div>

        {/* Card 4: Radar Chart */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm">
          <div className="border-b border-slate-100 pb-2 mb-4 flex justify-between items-center">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Syndicate Threat Matrix Comparison</h3>
            <span className="text-[10px] text-slate-400 font-mono">AI ASSESSED</span>
          </div>
          <div className="h-[280px]">
            <EChart option={threatRadarOption} style={{ height: '280px' }} />
          </div>
        </div>

      </div>
    </div>
  );
};
export default Analytics;
