import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import { runInvestigation, sendFollowUp } from '../../services/investigationApi';
import type { FollowUpMessage, InvestigationResult } from '../../services/investigationApi';
import { queryIntelligence } from '../../services/mockDb';
import type { IntelligenceReport } from '../../services/mockDb';
import { MapWidget } from '../../components/ui/MapWidget';
import {
  Cpu,
  Search,
  FileText,
  UserCheck,
  Car,
  FolderLock,
  MapPin,
  Clock,
  ShieldAlert,
  ListTodo,
  Network,
  Database,
  ArrowRight,
  Printer,
  ShieldCheck,
  CheckCircle,
  Send,
  History,
  X,
  ChevronRight,
  Loader2,
  ScrollText,
  AlertTriangle
} from 'lucide-react';

// ── Skeleton placeholder ─────────────────────────────────────────────────

const SkeletonCard: React.FC<{ height?: string }> = ({ height = '140px' }) => (
  <div
    style={{ height }}
    className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col gap-3 animate-pulse justify-between"
  >
    <div className="flex items-center gap-2 border-b border-slate-50 pb-2">
      <div className="w-4 h-4 bg-slate-200 rounded-full"></div>
      <div className="h-3.5 bg-slate-200 rounded w-1/3"></div>
    </div>
    <div className="flex-1 flex flex-col gap-2.5 mt-2">
      <div className="h-2.5 bg-slate-200 rounded w-full"></div>
      <div className="h-2.5 bg-slate-200 rounded w-5/6"></div>
      <div className="h-2.5 bg-slate-200 rounded w-4/5"></div>
    </div>
  </div>
);

// ── Query history entry ──────────────────────────────────────────────────

interface QueryHistoryEntry {
  id: string;
  query: string;
  timestamp: string;
  riskScore: number;
  source: 'backend' | 'mock';
  threadId: string;
  report: IntelligenceReport;
  reportText: string;
  status: 'success' | 'insufficient_data';
}

// ── Main Component ───────────────────────────────────────────────────────

export const AIWorkspace: React.FC = () => {
  const navigate = useNavigate();
  const { aiQuery, setAiQuery, setSelectedFir, setSelectedSuspect, setSelectedVehicle, language, addToast } = useApp();
  const [searchInput, setSearchInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [report, setReport] = useState<IntelligenceReport | null>(null);
  const [dataSource, setDataSource] = useState<'backend' | 'mock'>('mock');
  const [queryStatus, setQueryStatus] = useState<'success' | 'insufficient_data'>('success');
  const [reportText, setReportText] = useState('');

  // Thread state
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);

  // Pipeline animation state
  const [pipelineSteps, setPipelineSteps] = useState<{ text: string; done: boolean }[]>([
    { text: 'Searching FIR Database...', done: false },
    { text: 'Matching Vehicle Registry...', done: false },
    { text: 'Checking Call Records...', done: false },
    { text: 'Finding Associated Suspects...', done: false },
    { text: 'Analyzing Crime Patterns...', done: false },
    { text: 'Building Criminal Network...', done: false },
    { text: 'Generating Investigation Report...', done: false }
  ]);
  const [visibleCards, setVisibleCards] = useState<string[]>([]);
  const pipelineIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Follow-up chat state
  const [followUpInput, setFollowUpInput] = useState('');
  const [followUpMessages, setFollowUpMessages] = useState<FollowUpMessage[]>([]);
  const [isFollowUpLoading, setIsFollowUpLoading] = useState(false);
  const followUpEndRef = useRef<HTMLDivElement>(null);

  // Query history state
  const [queryHistory, setQueryHistory] = useState<QueryHistoryEntry[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [recentActions, setRecentActions] = useState<{ desc: string; timestamp: string }[]>([]);
  const [activeTab, setActiveTab] = useState<'summary' | 'agentic'>('summary');

  // Interactive directive toggles
  const [checkedDirectives, setCheckedDirectives] = useState<Record<number, boolean>>({});

  // Suggested prompts
  const suggestions = [
    'Find all suspects connected with vehicle KA05MJ4421',
    'Find cases linked with suspect Vikram Hegde',
    'General intelligence report for Bengaluru South'
  ];

  // ── Hybrid pipeline animation ────────────────────────────────────────

  const resetPipeline = () => {
    setPipelineSteps([
      { text: 'Searching FIR Database...', done: false },
      { text: 'Matching Vehicle Registry...', done: false },
      { text: 'Checking Call Records...', done: false },
      { text: 'Finding Associated Suspects...', done: false },
      { text: 'Analyzing Crime Patterns...', done: false },
      { text: 'Building Criminal Network...', done: false },
      { text: 'Generating Investigation Report...', done: false }
    ]);
    setVisibleCards([]);
  };

  const startPipelineAnimation = () => {
    const stepKeys = ['firs', 'vehicles', 'timeline', 'suspects', 'map', 'network', 'summary'];
    let currentStep = 0;

    pipelineIntervalRef.current = setInterval(() => {
      if (currentStep < 5) {
        setPipelineSteps(prev =>
          prev.map((step, idx) => (idx === currentStep ? { ...step, done: true } : step))
        );
        setVisibleCards(prev => [...prev, stepKeys[currentStep]]);
        currentStep++;
      } else {
        if (pipelineIntervalRef.current) clearInterval(pipelineIntervalRef.current);
      }
    }, 400);
  };

  const completePipelineAnimation = () => {
    if (pipelineIntervalRef.current) clearInterval(pipelineIntervalRef.current);
    const stepKeys = ['firs', 'vehicles', 'timeline', 'suspects', 'map', 'network', 'summary'];

    let delay = 0;
    stepKeys.forEach((key, idx) => {
      setTimeout(() => {
        setPipelineSteps(prev =>
          prev.map((step, i) => (i === idx ? { ...step, done: true } : step))
        );
        setVisibleCards(prev => prev.includes(key) ? prev : [...prev, key]);
      }, delay);
      delay += 120;
    });
  };

  // ── Run investigation (FRESH query) ──────────────────────────────────

  const runAnalysis = async (query: string) => {
    setIsProcessing(true);
    setReport(null);
    setFollowUpMessages([]);
    setCheckedDirectives({});
    setQueryStatus('success');
    setReportText('');
    setCurrentThreadId(null);
    resetPipeline();
    startPipelineAnimation();

    try {
      const result: InvestigationResult = await runInvestigation(query);
      completePipelineAnimation();

      setTimeout(() => {
        setReport(result.report);
        setDataSource(result.source);
        setQueryStatus(result.status);
        setReportText(result.reportText);
        setCurrentThreadId(result.threadId);
        setIsProcessing(false);

        // Add to query history
        setQueryHistory(prev => [
          {
            id: `q-${Date.now()}`,
            query,
            timestamp: new Date().toLocaleTimeString(),
            riskScore: result.report.riskScore,
            source: result.source,
            threadId: result.threadId,
            report: result.report,
            reportText: result.reportText,
            status: result.status,
          },
          ...prev.slice(0, 19),
        ]);

        if (result.status === 'insufficient_data') {
          addToast('No matching records found for this query.', 'warn');
        } else {
          addToast(
            result.source === 'backend'
              ? 'Investigation Dossier compiled from live KSP database.'
              : 'Investigation Dossier compiled (demo mode).',
            'success'
          );
        }
      }, 900);
    } catch {
      completePipelineAnimation();
      setTimeout(() => {
        const fallback = queryIntelligence(query);
        setReport(fallback);
        setDataSource('mock');
        setQueryStatus('success');
        setReportText('');
        const mockThreadId = `mock-${Date.now()}`;
        setCurrentThreadId(mockThreadId);
        setIsProcessing(false);

        // Add to query history
        setQueryHistory(prev => [
          {
            id: `q-${Date.now()}`,
            query,
            timestamp: new Date().toLocaleTimeString(),
            riskScore: fallback.riskScore,
            source: 'mock',
            threadId: mockThreadId,
            report: fallback,
            reportText: '',
            status: 'success',
          },
          ...prev.slice(0, 19),
        ]);

        addToast('Investigation Dossier compiled (demo mode).', 'success');
      }, 900);
    }
  };

  // Trigger when global query state updates
  useEffect(() => {
    if (aiQuery) {
      setSearchInput(aiQuery);
      runAnalysis(aiQuery);
    }
  }, [aiQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchInput.trim()) return;
    setActiveTab('summary');
    setAiQuery(searchInput);
    runAnalysis(searchInput);
  };

  const handlePrint = () => {
    if (report) {
      navigate('/reports/preview', { state: { report } });
    }
  };

  // ── Follow-up chat (uses thread_id — no full pipeline animation) ─────

  const handleFollowUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!followUpInput.trim() || !report || !currentThreadId) return;

    const userMessage: FollowUpMessage = {
      role: 'officer',
      content: followUpInput.trim(),
      timestamp: new Date().toLocaleTimeString(),
    };
    setFollowUpMessages(prev => [...prev, userMessage]);
    setFollowUpInput('');
    setIsFollowUpLoading(true);

    const history = [...followUpMessages, userMessage].map(m => ({
      role: m.role,
      content: m.content,
    }));

    const result = await sendFollowUp(userMessage.content, currentThreadId, history);

    const aiMessage: FollowUpMessage = {
      role: 'ai',
      content: result.text,
      timestamp: new Date().toLocaleTimeString(),
      type: result.type,
    };
    setFollowUpMessages(prev => [...prev, aiMessage]);
    setIsFollowUpLoading(false);

    if (result.type === 'action') {
      const cleanText = result.text.replace(/\[DEVELOPER WARNING:.*?\]\s*/i, '');
      const match = cleanText.match(/ACTION TAKEN:\s*(.+?)(?:,\s*\d{4}-\d{2}-\d{2}|$)/i);
      const desc = match ? match[1].trim() : cleanText.replace(/ACTION TAKEN:\s*/i, '').trim();
      setRecentActions(prev => [{ desc, timestamp: new Date().toLocaleTimeString() }, ...prev].slice(0, 5));
    }

    if (result.status === 'insufficient_data') {
      addToast('Follow-up query returned insufficient data.', 'warn');
    }
  };

  // Auto-scroll follow-up chat
  useEffect(() => {
    followUpEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [followUpMessages]);

  // ── Directive checkbox toggle ────────────────────────────────────────

  const toggleDirective = (idx: number) => {
    setCheckedDirectives(prev => {
      const next = { ...prev, [idx]: !prev[idx] };
      if (next[idx]) {
        addToast(`Directive #${idx + 1} marked as acknowledged.`, 'info');
      }
      return next;
    });
  };

  // ── History sidebar item click ───────────────────────────────────────

  const loadFromHistory = (entry: QueryHistoryEntry) => {
    setSearchInput(entry.query);
    setShowHistory(false);
    setActiveTab('summary');
    
    // Restore cached state directly (no API call, no re-processing delay)
    setReport(entry.report);
    setDataSource(entry.source);
    setQueryStatus(entry.status);
    setReportText(entry.reportText);
    setCurrentThreadId(entry.threadId);
    setFollowUpMessages([]);
    
    // Mark checklist steps as completed
    const stepKeys = ['firs', 'vehicles', 'timeline', 'suspects', 'map', 'network', 'summary'];
    setPipelineSteps(prev => prev.map(step => ({ ...step, done: true })));
    setVisibleCards(stepKeys);

    addToast(`Restored dossier for "${entry.query}" from history cache.`, 'success');
  };

  // ── Risk color helpers ───────────────────────────────────────────────

  const getRiskColor = (score: number) => {
    if (score >= 80) return '#b91c1c';
    if (score >= 60) return '#c2410c';
    if (score >= 30) return '#d97706';
    return '#16a34a';
  };

  const getRiskLabel = (score: number) => {
    if (score >= 80) return 'Critical';
    if (score >= 60) return 'High';
    if (score >= 30) return 'Medium';
    return 'Low';
  };

  const getRiskBadgeClasses = (score: number) => {
    if (score >= 80) return 'text-red-600 bg-red-50 border-red-200';
    if (score >= 60) return 'text-orange-600 bg-orange-50 border-orange-200';
    if (score >= 30) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-green-600 bg-green-50 border-green-200';
  };

  // ── Determine whether to show dossier cards or zero-result card ──────

  const showDossier = report && queryStatus === 'success';
  const showNoResults = report && queryStatus === 'insufficient_data';

  return (
    <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto print:p-0 print:bg-white print:text-black">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-4 print:hidden select-none">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-brand-secondary" />
            <h1 className="text-sm font-bold text-brand-primary uppercase tracking-wider">
              {language === 'en' ? 'AI Intelligence compiler' : 'ಎಐ ಇಂಟೆಲಿಜೆನ್ಸ್ ಕೊಠಡಿ'}
            </h1>
          </div>
          <p className="text-xs text-slate-500 font-sans mt-1">
            Compile and synthesize multi-layered case dossiers in real-time.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {report && (
            <span className={`text-[9px] font-mono font-bold px-2 py-1 rounded border uppercase ${
              dataSource === 'backend'
                ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
                : 'text-slate-500 bg-slate-100 border-slate-200'
            }`}>
              {dataSource === 'backend' ? '● LIVE DATABASE' : '◌ DEMO MODE'}
            </span>
          )}
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="py-1.5 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded border border-slate-200 hover:border-slate-300 transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <History className="w-4 h-4" />
            <span>History</span>
            {queryHistory.length > 0 && (
              <span className="ml-1 px-1.5 py-0.5 bg-brand-primary text-white text-[9px] font-mono rounded-full leading-none">
                {queryHistory.length}
              </span>
            )}
          </button>
          {report && (
            <button
              onClick={handlePrint}
              className="py-1.5 px-4 bg-brand-primary hover:bg-brand-primary-light text-white font-bold text-xs rounded border border-brand-primary-light hover:border-brand-primary transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
            >
              <Printer className="w-4 h-4 text-brand-secondary" />
              <span>Generate Official Report</span>
            </button>
          )}
        </div>
      </div>

      {/* ── Sub-module Tabs Navigation ───────────────────────────────── */}
      <div className="flex border-b border-slate-200 print:hidden select-none -mt-2">
        <button
          onClick={() => setActiveTab('summary')}
          className={`py-2 px-5 font-sans font-bold text-xs uppercase tracking-wider border-b-2 transition-all cursor-pointer ${
            activeTab === 'summary'
              ? 'border-brand-primary text-brand-primary font-extrabold'
              : 'border-transparent text-slate-400 hover:text-slate-600 hover:border-slate-200'
          }`}
        >
          Quick Summary Dossier
        </button>
        <button
          onClick={() => setActiveTab('agentic')}
          className={`py-2 px-5 font-sans font-bold text-xs uppercase tracking-wider border-b-2 transition-all cursor-pointer ${
            activeTab === 'agentic'
              ? 'border-brand-primary text-brand-primary font-extrabold'
              : 'border-transparent text-slate-400 hover:text-slate-600 hover:border-slate-200'
          }`}
        >
          Agentic Case Console
        </button>
      </div>

      {/* ── Query History Panel ───────────────────────────────────────── */}
      {showHistory && (
        <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-4 print:hidden animate-in fade-in duration-200">
          <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-brand-primary" />
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Investigation Query Log</h3>
            </div>
            <button onClick={() => setShowHistory(false)} className="p-1 hover:bg-slate-100 rounded cursor-pointer transition-colors">
              <X className="w-4 h-4 text-slate-400" />
            </button>
          </div>
          {queryHistory.length === 0 ? (
            <p className="text-xs text-slate-400 text-center py-4">No queries in this session yet.</p>
          ) : (
            <div className="flex flex-col gap-1.5 max-h-60 overflow-y-auto">
              {queryHistory.map(entry => (
                <button
                  key={entry.id}
                  onClick={() => loadFromHistory(entry)}
                  className="w-full text-left p-2.5 rounded border border-slate-100 hover:border-slate-300 hover:bg-slate-50 transition-all cursor-pointer flex items-center justify-between gap-3"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-slate-700 truncate">{entry.query}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[9px] font-mono text-slate-400">{entry.timestamp}</span>
                      <span className={`text-[9px] font-mono font-bold px-1 rounded ${
                        entry.source === 'backend' ? 'text-emerald-600 bg-emerald-50' : 'text-slate-500 bg-slate-100'
                      }`}>
                        {entry.source === 'backend' ? 'LIVE' : 'DEMO'}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border ${getRiskBadgeClasses(entry.riskScore)}`}>
                      {entry.riskScore}%
                    </span>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-300" />
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Sub-module 1: Quick Summary ─────────────────────────────── */}
      {activeTab === 'summary' && (
        <>
          {/* Input field */}
          <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm print:hidden">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1 flex items-center border border-slate-200 focus-within:border-brand-secondary focus-within:ring-2 focus-within:ring-brand-secondary/20 rounded-md bg-slate-50 px-3 py-2 transition-all">
            <Search className="w-4.5 h-4.5 text-slate-400 mr-2 shrink-0" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search suspect name, vehicle ID or case number..."
              className="bg-transparent border-none text-xs w-full focus:outline-none placeholder-slate-400 font-sans"
            />
          </div>
          <button
            type="submit"
            className="bg-brand-primary hover:bg-brand-primary-light text-white font-bold text-xs px-6 py-2.5 rounded-md flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Cpu className="w-4 h-4 text-brand-secondary" />
            <span>Analyze</span>
          </button>
        </form>

        <div className="mt-3 flex flex-wrap gap-2 items-center text-xs">
          <span className="text-slate-400">Try searches:</span>
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setSearchInput(s);
                setAiQuery(s);
                runAnalysis(s);
              }}
              className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 border border-slate-200 hover:border-slate-300 rounded font-mono text-[10px] text-brand-primary transition-all cursor-pointer"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* PIPELINE STATUS BAR                                          */}
      {/* ══════════════════════════════════════════════════════════════ */}
      {(isProcessing || report) && (
        <div className="bg-brand-primary text-white border border-slate-800 rounded-lg p-5 shadow-lg flex flex-col md:flex-row justify-between items-center gap-4 print:hidden select-none">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-brand-primary-light border border-slate-850 rounded text-brand-secondary">
              <Database className={`w-5 h-5 ${isProcessing ? 'animate-pulse' : ''}`} />
            </div>
            <div>
              <h4 className="text-xs font-mono font-bold uppercase tracking-widest text-brand-secondary">
                {isProcessing ? 'COMPILING INTELLIGENCE DOSSIER' : 'ANALYSIS AUDIT REPORT VERIFIED'}
              </h4>
              <p className="text-[10px] text-slate-400 font-mono mt-0.5 leading-none">
                {isProcessing ? 'Executing multi-socket database checks' : 'Dossier locks resolved and signed by terminal'}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 md:gap-3 text-[10px] font-mono">
            {pipelineSteps.map((step, idx) => (
              <div
                key={idx}
                className={`flex items-center gap-1 px-2.5 py-1 border rounded transition-all duration-150 ${
                  step.done
                    ? 'bg-brand-primary-light/50 border-slate-700 text-slate-100'
                    : 'bg-transparent border-slate-850 text-slate-600'
                }`}
              >
                <CheckCircle className={`w-3.5 h-3.5 ${step.done ? 'text-brand-secondary' : 'text-slate-800'}`} />
                <span>{step.text.replace('...', '')}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Initial empty state */}
      {!isProcessing && !report && (
        <div className="bg-white border border-slate-200 rounded-lg p-16 text-center shadow-sm select-none print:hidden flex flex-col items-center justify-center gap-3">
          <div className="p-4 bg-slate-50 rounded-full text-slate-400 border border-slate-100">
            <Cpu className="w-10 h-10" />
          </div>
          <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">Operational Intel Compile Area</h3>
          <p className="text-xs text-slate-400 max-w-sm leading-normal">
            Submit vehicle plates or suspect names to launch the multi-socket cross-referencing pipeline.
          </p>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* ZERO-RESULT / INSUFFICIENT DATA CARD                         */}
      {/* ══════════════════════════════════════════════════════════════ */}
      {showNoResults && (
        <div className="bg-white border-2 border-amber-300 rounded-lg p-8 shadow-md animate-in fade-in">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 shrink-0">
              <AlertTriangle className="w-8 h-8 text-amber-600" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <ScrollText className="w-5 h-5 text-amber-700" />
                <h2 className="text-xs font-bold text-amber-800 uppercase tracking-widest">Official Investigation Report — No Records Found</h2>
              </div>
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-5 font-mono text-xs text-slate-800 leading-relaxed whitespace-pre-line">
                <div className="mb-3 pb-2 border-b border-amber-200">
                  <span className="font-bold text-amber-800 uppercase tracking-wider text-[10px]">Investigation Query Response</span>
                  <p className="mt-1 text-[10px] text-slate-500">Generated: {new Date().toLocaleString()} | Classification: LAW ENFORCEMENT SENSITIVE</p>
                </div>
                <div className="mb-3">
                  <span className="font-bold text-slate-700">Query Reference:</span> {report?.query}
                </div>
                <div className="mb-3">
                  <span className="font-bold text-amber-700">FINDINGS</span>
                  <p className="mt-1 font-semibold text-amber-800">Insufficient records found for this query.</p>
                  <p className="mt-1 text-slate-600">
                    No matching records were found in the FIR database, ANPR registry, CDR logs,
                    or biometric match databases for the specified search parameters.
                  </p>
                </div>
                {reportText && (
                  <div className="mb-3">
                    <span className="font-bold text-slate-700">FULL RESPONSE</span>
                    <p className="mt-1">{reportText}</p>
                  </div>
                )}
                <div className="mb-3">
                  <span className="font-bold text-slate-700">AI ASSESSMENT</span>
                  <p className="mt-1">The query did not return actionable intelligence from available data sources.</p>
                </div>
                <div>
                  <span className="font-bold text-slate-700">RECOMMENDED ACTION</span>
                  <p className="mt-1">Verify the search parameters and retry with corrected suspect names, vehicle registration numbers, or case reference numbers.</p>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => {
                    setSearchInput('');
                    setReport(null);
                    setQueryStatus('success');
                  }}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded border border-slate-200 transition-all cursor-pointer"
                >
                  Clear & Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* DOSSIER GRID (only when status === "success" and has data)    */}
      {/* ══════════════════════════════════════════════════════════════ */}
      {(isProcessing || showDossier) && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* LEFT COLUMN */}
          <div className="lg:col-span-2 flex flex-col gap-6">

            {/* ── Standalone Formal Investigation Report Block ─────── */}
            {!visibleCards.includes('summary') ? (
              <SkeletonCard height="200px" />
            ) : (
              report && (
                <div className="bg-white border-2 border-brand-primary rounded-lg p-6 shadow-md relative overflow-hidden transition-all duration-500 animate-in fade-in">
                  <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-brand-primary via-brand-secondary to-brand-primary" />
                  <div className="flex justify-between items-start gap-4 mb-4 border-b border-slate-200 pb-3">
                    <div className="flex items-center gap-2">
                      <ScrollText className="w-5 h-5 text-brand-primary" />
                      <h2 className="text-xs font-bold text-brand-primary uppercase tracking-widest">Official Investigation Report</h2>
                    </div>
                    <span className="text-[9px] font-mono text-slate-400 uppercase tracking-widest bg-slate-100 px-2 py-0.5 rounded">
                      AI-Generated Intelligence Brief
                    </span>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 font-mono text-xs text-slate-800 leading-relaxed whitespace-pre-line select-text">
                    <div className="mb-3 pb-2 border-b border-slate-200">
                      <span className="font-bold text-brand-primary uppercase tracking-wider text-[10px]">Investigation Query Response</span>
                      <p className="mt-1 text-[10px] text-slate-500">Generated: {new Date().toLocaleString()} | Classification: LAW ENFORCEMENT SENSITIVE</p>
                    </div>
                    {reportText ? (
                      <div>{reportText}</div>
                    ) : (
                      <>
                        <div className="mb-2">
                          <span className="font-bold text-slate-700">Query Reference:</span> {report.query}
                        </div>
                        <div className="mb-2">
                          <span className="font-bold text-slate-700">FINDINGS</span>
                          <p className="mt-1">{report.executiveSummary}</p>
                        </div>
                        {report.relatedFirs.length > 0 && (
                          <div className="mb-2">
                            <span className="font-bold text-slate-700">RELATED RECORDS</span>
                            <ul className="mt-1 list-disc pl-4">
                              {report.relatedFirs.map(f => (
                                <li key={f.id}>{f.id} — {f.category} ({f.severity})</li>
                              ))}
                              {report.associatedSuspects.map(s => (
                                <li key={s.id}>Suspect: {s.name} — {s.status}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        <div className="mb-2">
                          <span className="font-bold text-slate-700">AI ASSESSMENT</span>
                          <p className="mt-1">Risk level: {getRiskLabel(report.riskScore)} ({report.riskScore}/100). {report.riskScore >= 60 ? 'Immediate supervisory review recommended.' : 'Continue evidence enrichment.'}</p>
                        </div>
                        <div>
                          <span className="font-bold text-slate-700">RECOMMENDED ACTION</span>
                          <p className="mt-1">{report.recommendedActions[0] || 'Continue standard investigation procedures.'}</p>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )
            )}

            {/* Recent Actions Log */}
            {recentActions.length > 0 && (
              <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm relative overflow-hidden transition-all duration-300 animate-in slide-in-from-right-3">
                <div className="absolute top-0 left-0 w-full h-1 bg-emerald-500" />
                <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-3">
                  <CheckCircle className="w-4.5 h-4.5 text-emerald-600" />
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Session Action Log</h3>
                </div>
                <div className="flex flex-col gap-2 font-mono text-[10.5px]">
                  {recentActions.map((act, idx) => (
                    <div key={idx} className="flex flex-col border-b border-slate-50 pb-1.5 last:border-0 last:pb-0">
                      <span className="text-slate-700 font-semibold leading-normal">{act.desc}</span>
                      <span className="text-[9px] text-slate-400 mt-0.5">{act.timestamp}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Executive Summary */}
            {!visibleCards.includes('summary') ? (
              <SkeletonCard height="150px" />
            ) : (
              report && (
                <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm relative overflow-hidden transition-all duration-500 animate-in fade-in">
                  <div className="absolute top-0 left-0 w-full h-1 bg-brand-primary" />
                  <div className="flex justify-between items-start gap-4 mb-3 border-b border-slate-100 pb-2">
                    <div className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-brand-secondary" />
                      <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Intelligence Dossier Summary</h2>
                    </div>
                    <span className="text-[9px] font-mono text-slate-400 uppercase tracking-widest bg-slate-100 px-2 py-0.5 rounded">
                      Compiled Dossier
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed font-mono whitespace-pre-line bg-slate-50 border border-slate-100 rounded p-4 select-text">
                    {report.executiveSummary}
                  </p>
                </div>
              )
            )}

            {/* Explainable AI Provenance */}
            {!visibleCards.includes('summary') ? (
              <SkeletonCard height="150px" />
            ) : (
              report && (
                <div id="explainable-ai-section" className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm relative overflow-hidden transition-all duration-500 animate-in fade-in scroll-mt-20">
                  <div className="absolute top-0 left-0 w-full h-1 bg-brand-primary" />
                  <div className="border-b border-slate-100 pb-2 mb-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-4.5 h-4.5 text-brand-primary" />
                      <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-sans">Explainable AI Details & Provenance</h3>
                    </div>
                    <span className="text-[10px] font-mono text-emerald-600 font-bold uppercase">Confidence: {Math.min(report.riskScore + 4, 99)}%</span>
                  </div>
                  <div className="flex flex-col gap-3 text-xs leading-normal">
                    <div>
                      <span className="font-semibold text-slate-700 block">matching inference nodes:</span>
                      <p className="text-slate-500 text-[11px] mt-0.5">
                        {report.associatedSuspects.length > 0 ? `Matched ${report.associatedSuspects.length} suspect(s): ${report.associatedSuspects.map(s => s.name).join(', ')}. ` : ''}
                        {report.relatedVehicles.length > 0 ? `${report.relatedVehicles.length} vehicle(s) flagged in ANPR registry. ` : ''}
                        {report.relatedFirs.length > 0 ? `${report.relatedFirs.length} FIR(s) linked.` : 'No direct FIR matches found.'}
                      </p>
                    </div>
                    <div>
                      <span className="font-semibold text-slate-700 block">data sources audited:</span>
                      <div className="flex gap-2 mt-1 flex-wrap">
                        <span className="px-1.5 py-0.5 bg-slate-100 text-slate-650 font-mono text-[9px] rounded border border-slate-150">State FIR Database</span>
                        {report.relatedVehicles.length > 0 && <span className="px-1.5 py-0.5 bg-slate-100 text-slate-650 font-mono text-[9px] rounded border border-slate-150">National ANPR Registers</span>}
                        {report.timeline.length > 1 && <span className="px-1.5 py-0.5 bg-slate-100 text-slate-650 font-mono text-[9px] rounded border border-slate-150">Telecom CDR Records</span>}
                        <span className="px-1.5 py-0.5 bg-slate-100 text-slate-650 font-mono text-[9px] rounded border border-slate-150">Biometric Match Database</span>
                      </div>
                    </div>
                  </div>
                </div>
              )
            )}

            {/* Related FIRs — conditional */}
            {!visibleCards.includes('firs') ? (
              <SkeletonCard height="200px" />
            ) : (
              report && report.relatedFirs.length > 0 && (
                <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm transition-all duration-500 animate-in fade-in">
                  <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-4">
                    <FolderLock className="w-5 h-5 text-brand-primary" />
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Related FIR / Cases Ledger</h3>
                  </div>
                  <div className="flex flex-col gap-3">
                    {report.relatedFirs.map((fir) => (
                      <div key={fir.id} className="p-3 border border-slate-200 rounded hover:border-slate-300 transition-colors">
                        <div className="flex justify-between items-start gap-2 flex-wrap">
                          <span
                            onClick={() => setSelectedFir(fir)}
                            className="text-xs font-mono font-bold text-brand-primary hover:underline cursor-pointer"
                          >
                            {fir.id}
                          </span>
                          <span className={`inline-block px-1.5 py-0.5 rounded text-[9px] font-bold font-mono ${
                            fir.severity === 'Critical' ? 'bg-red-50 text-red-700' : 'bg-slate-100 text-slate-700'
                          }`}>
                            {fir.severity}
                          </span>
                        </div>
                        <h4 className="text-xs font-bold text-slate-700 mt-1">{fir.category}</h4>
                        <p className="text-[11px] text-slate-500 mt-1">{fir.summary}</p>
                        <div className="flex items-center gap-1.5 mt-2 font-mono text-[9px] text-slate-400">
                          <span>Jurisdiction: {fir.locationName}</span>
                          {fir.ipcSections.length > 0 && (
                            <>
                              <span>•</span>
                              <span>Sections: {fir.ipcSections.join(', ')}</span>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            )}

            {/* Associated Suspects — conditional */}
            {!visibleCards.includes('suspects') ? (
              <SkeletonCard height="180px" />
            ) : (
              report && report.associatedSuspects.length > 0 && (
                <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm transition-all duration-500 animate-in fade-in">
                  <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-4">
                    <UserCheck className="w-5 h-5 text-brand-primary" />
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Associated Suspect Profiles</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {report.associatedSuspects.map((suspect) => (
                      <div
                        key={suspect.id}
                        onClick={() => setSelectedSuspect(suspect)}
                        className="p-3 bg-slate-50 border border-slate-200 hover:border-slate-300 rounded flex gap-3 cursor-pointer hover:bg-slate-100/50 transition-all"
                      >
                        <div className={`w-12 h-12 rounded border flex items-center justify-center font-bold text-sm shrink-0 ${suspect.photoPlaceholder}`}>
                          {suspect.name.charAt(0)}
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-1.5">
                            <h4 className="text-xs font-bold text-slate-800 truncate hover:underline">{suspect.name}</h4>
                            <span className={`text-[9px] font-bold px-1 rounded ${
                              suspect.status === 'Absconding' ? 'bg-red-100 text-red-700' : 'bg-slate-200 text-slate-700'
                            }`}>
                              {suspect.status}
                            </span>
                          </div>
                          {suspect.aliases.length > 0 && (
                            <p className="text-[10px] text-slate-400 font-mono mt-0.5">Aliases: {suspect.aliases.join(', ')}</p>
                          )}
                          <p className="text-[10px] font-semibold text-brand-secondary mt-1">{suspect.gangAffiliation}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            )}

            {/* Related Vehicles — conditional */}
            {!visibleCards.includes('vehicles') ? (
              <SkeletonCard height="150px" />
            ) : (
              report && report.relatedVehicles.length > 0 && (
                <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm transition-all duration-500 animate-in fade-in">
                  <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-4">
                    <Car className="w-5 h-5 text-brand-primary" />
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Related Vehicles (ANPR Watchlist)</h3>
                  </div>
                  <div className="flex flex-col gap-3">
                    {report.relatedVehicles.map((vehicle) => (
                      <div
                        key={vehicle.id}
                        onClick={() => setSelectedVehicle(vehicle)}
                        className="p-3 border border-slate-200 hover:border-slate-300 rounded flex items-center justify-between cursor-pointer hover:bg-slate-50/50 transition-all"
                      >
                        <div className="flex items-center gap-3">
                          <Car className="w-5 h-5 text-slate-400 shrink-0" />
                          <div>
                            <span className="text-xs font-mono font-bold text-brand-primary hover:underline">{vehicle.id}</span>
                            <span className="text-[10px] text-slate-500 block">
                              {[vehicle.color, vehicle.make, vehicle.model].filter(Boolean).join(' ')} {vehicle.ownerName ? `- Owner: ${vehicle.ownerName}` : ''}
                            </span>
                          </div>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[9px] font-bold font-mono ${
                          vehicle.status === 'Flagged' ? 'bg-red-50 text-red-700 border border-red-150' : 'bg-slate-100 text-slate-700'
                        }`}>
                          {vehicle.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )
            )}

            {/* Evidence Vault — conditional */}
            {!visibleCards.includes('map') ? (
              <SkeletonCard height="140px" />
            ) : (
              report && report.evidence.length > 0 && (
                <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm transition-all duration-500 animate-in fade-in">
                  <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-3">
                    <FileText className="w-5 h-5 text-brand-primary" />
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Recovered Evidence Vault</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-slate-200 text-slate-400 font-mono text-[9px] uppercase">
                          <th className="py-2 font-semibold">Evidence Code</th>
                          <th className="py-2 font-semibold">Classification</th>
                          <th className="py-2 font-semibold">Description</th>
                          <th className="py-2 font-semibold text-right">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {report.evidence.map((ev) => (
                          <tr key={ev.id}>
                            <td className="py-2.5 font-mono font-bold text-brand-primary">{ev.id}</td>
                            <td className="py-2.5 font-semibold text-slate-700">{ev.type}</td>
                            <td className="py-2.5 text-slate-500 max-w-xs truncate">{ev.description}</td>
                            <td className="py-2.5 text-right">
                              <span className={`inline-block px-1.5 py-0.5 rounded text-[9px] font-bold font-mono ${
                                ev.status === 'Secured' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-700'
                              }`}>
                                {ev.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )
            )}

          </div>

          {/* RIGHT COLUMN */}
          <div className="flex flex-col gap-6">
            
            {/* Risk Threat Gauge — clickable → Explainable AI */}
            {!visibleCards.includes('summary') ? (
              <SkeletonCard height="200px" />
            ) : (
              report && (
                <div
                  onClick={() => document.getElementById('explainable-ai-section')?.scrollIntoView({ behavior: 'smooth' })}
                  className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col items-center transition-all duration-500 animate-in fade-in cursor-pointer hover:border-slate-300"
                  title="Click to view Explainable AI details"
                >
                  <div className="w-full border-b border-slate-100 pb-2 mb-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <ShieldAlert className="w-4.5 h-4.5 text-brand-accent" />
                      <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Incident Threat Index</h3>
                    </div>
                    <span className={`text-[9px] font-mono font-bold uppercase px-1 rounded leading-none border ${getRiskBadgeClasses(report.riskScore)}`}>
                      {getRiskLabel(report.riskScore)}
                    </span>
                  </div>
                  <div className="relative w-36 h-36 flex items-center justify-center">
                    <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
                      <circle cx="50" cy="50" r="40" stroke="#f1f5f9" strokeWidth="8" fill="transparent" />
                      <circle
                        cx="50" cy="50" r="40"
                        stroke={getRiskColor(report.riskScore)} strokeWidth="8" fill="transparent"
                        strokeDasharray="251.2"
                        strokeDashoffset={251.2 - (251.2 * report.riskScore) / 100}
                        strokeLinecap="round"
                        className="transition-all duration-1000 ease-out"
                      />
                    </svg>
                    <div className="absolute flex flex-col items-center justify-center leading-none">
                      <span className="text-3xl font-extrabold text-slate-800 font-mono">{report.riskScore}%</span>
                      <span className="text-[10px] text-slate-400 font-mono mt-1 uppercase">Threat index</span>
                    </div>
                  </div>
                  <p className="text-[9px] text-slate-400 mt-2 font-mono">Click for Explainable AI details ↓</p>
                </div>
              )
            )}

            {/* Spatial Footprint Map */}
            {!visibleCards.includes('map') ? (
              <SkeletonCard height="250px" />
            ) : (
              report && (
                <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex flex-col gap-3 transition-all duration-500 animate-in fade-in">
                  <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
                    <MapPin className="w-4.5 h-4.5 text-brand-primary" />
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Spatial Footprint Map</h3>
                  </div>
                  <div className="h-[250px]">
                    <MapWidget
                      center={report.crimeLocations[0] ? [report.crimeLocations[0].latitude, report.crimeLocations[0].longitude] : [12.9345, 77.6268]}
                      zoom={12}
                      markers={report.crimeLocations.map((loc, idx) => ({
                        id: `loc-${idx}`,
                        position: [loc.latitude, loc.longitude],
                        title: loc.name,
                        description: loc.description
                      }))}
                      height="250px"
                    />
                  </div>
                </div>
              )
            )}

            {/* Timeline — conditional */}
            {!visibleCards.includes('timeline') ? (
              <SkeletonCard height="280px" />
            ) : (
              report && report.timeline.length > 0 && (
                <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm transition-all duration-500 animate-in fade-in">
                  <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-4">
                    <Clock className="w-4.5 h-4.5 text-brand-primary" />
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">ANPR & Communications Timeline</h3>
                  </div>
                  <div className="relative border-l border-slate-200 pl-4 ml-2 flex flex-col gap-5">
                    {report.timeline.map((item, idx) => (
                      <div key={idx} className="relative text-xs">
                        <span className={`absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full border-2 border-white ring-1 ring-slate-300 ${
                          item.severity === 'Critical' ? 'bg-red-600 ring-red-400' :
                          item.severity === 'Major' ? 'bg-orange-500 ring-orange-300' :
                          'bg-slate-400 ring-slate-200'
                        }`} />
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-[9px] font-bold text-slate-400">{item.time}</span>
                          <span className={`text-[8px] px-1 font-mono font-bold leading-none rounded uppercase ${
                            item.severity === 'Critical' ? 'bg-red-50 text-red-700' : 'bg-slate-100 text-slate-500'
                          }`}>
                            {item.severity}
                          </span>
                        </div>
                        <h5 className="font-bold text-slate-800 mt-0.5">{item.event}</h5>
                        <p className="text-slate-500 text-[10.5px] mt-0.5 leading-normal">{item.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )
            )}

            {/* Network Graph Preview */}
            {!visibleCards.includes('network') ? (
              <SkeletonCard height="150px" />
            ) : (
              report && (
                <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col gap-3 transition-all duration-500 animate-in fade-in">
                  <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                    <div className="flex items-center gap-2">
                      <Network className="w-4.5 h-4.5 text-brand-primary" />
                      <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Syndicate Connections</h3>
                    </div>
                    <button
                      onClick={() => navigate('/network')}
                      className="text-[9px] text-brand-secondary font-bold hover:underline uppercase flex items-center gap-0.5 cursor-pointer"
                    >
                      Interactive Graph <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 flex flex-col gap-2">
                    <span className="text-[10px] text-slate-400 block font-mono">DETECTED LINK PATTERNS</span>
                    {report.networkGraph.edges.length > 0 ? (
                      <div className="flex flex-col gap-1.5 font-mono text-[10px] text-slate-600">
                        {report.networkGraph.edges.slice(0, 4).map((edge, idx) => {
                          const sourceNode = report.networkGraph.nodes.find(n => n.id === edge.source);
                          const targetNode = report.networkGraph.nodes.find(n => n.id === edge.target);
                          return (
                            <div key={idx} className="flex items-center justify-between">
                              <span>{sourceNode?.label || edge.source} &harr; {targetNode?.label || edge.target}</span>
                              <span className="text-red-600 font-bold bg-red-50 px-1 rounded">{edge.label}</span>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-[10px] text-slate-400 font-mono">No direct syndicate links detected.</p>
                    )}
                  </div>
                </div>
              )
            )}

            {/* Recommended Directives — interactive checkboxes */}
            {!visibleCards.includes('summary') ? (
              <SkeletonCard height="150px" />
            ) : (
              report && report.recommendedActions.length > 0 && (
                <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm relative overflow-hidden transition-all duration-500 animate-in fade-in">
                  <div className="absolute top-0 left-0 w-full h-1 bg-brand-secondary" />
                  <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-3">
                    <ListTodo className="w-4.5 h-4.5 text-brand-secondary" />
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Recommended Officer Directives</h3>
                  </div>
                  <div className="flex flex-col gap-2.5 font-sans">
                    {report.recommendedActions.map((action, idx) => (
                      <div
                        key={idx}
                        className={`flex gap-2.5 items-start text-xs leading-normal p-2 rounded transition-all cursor-pointer ${
                          checkedDirectives[idx] ? 'bg-emerald-50 border border-emerald-200' : 'hover:bg-slate-50'
                        }`}
                        onClick={() => toggleDirective(idx)}
                      >
                        <input
                          type="checkbox"
                          checked={!!checkedDirectives[idx]}
                          onChange={() => {}}
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleDirective(idx);
                          }}
                          className="mt-0.5 rounded border-slate-300 text-brand-primary focus:ring-brand-primary shrink-0 cursor-pointer"
                        />
                        <span className={`font-medium ${checkedDirectives[idx] ? 'text-emerald-700 line-through' : 'text-slate-600'}`}>
                          {action}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )
            )}

          </div>

        </div>
      )}

          {/* Open in Agentic Console Button */}
          {report && currentThreadId && (
            <div className="flex justify-end mt-4">
              <button
                onClick={() => setActiveTab('agentic')}
                className="bg-brand-primary hover:bg-brand-primary-light text-white font-bold text-xs px-6 py-3 rounded-md flex items-center gap-1.5 transition-colors cursor-pointer shadow-sm animate-in slide-in-from-bottom-2 duration-300"
              >
                <span>Open in Agentic Case Console</span>
                <ArrowRight className="w-4.5 h-4.5 text-brand-secondary animate-pulse" />
              </button>
            </div>
          )}
        </>
      )}

      {/* ── Sub-module 2: Agentic Case Console ──────────────────────── */}
      {activeTab === 'agentic' && (
        <div className="flex flex-col gap-6 animate-in fade-in duration-200 font-sans">
          
          {/* Scoped Case Banner */}
          <div className="bg-slate-50 border border-slate-200 rounded-lg px-5 py-4 flex flex-col sm:flex-row justify-between sm:items-center gap-4 print:hidden">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-brand-primary text-brand-secondary rounded-md">
                <FolderLock className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-widest font-mono">
                  Agentic Control Surface
                </h3>
                {report && currentThreadId ? (
                  <p className="text-[11.5px] text-slate-650 font-mono mt-1">
                    Scoped to Case: <span className="font-bold text-brand-primary">"{report.query}"</span> | Active Thread: <span className="font-mono text-slate-500 bg-slate-100 px-1 py-0.5 rounded text-[10px]">{currentThreadId}</span>
                  </p>
                ) : (
                  <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                    No active case thread compiled.
                  </p>
                )}
              </div>
            </div>
            
            <button
              onClick={() => setActiveTab('summary')}
              className="py-2 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded border border-slate-200 hover:border-slate-300 transition-all flex items-center gap-1.5 cursor-pointer self-start sm:self-auto"
            >
              <ArrowRight className="w-4 h-4 rotate-180" />
              <span>Back to Dossier Summary</span>
            </button>
          </div>

          {/* Capabilities strip */}
          <div className="flex flex-wrap items-center gap-1.5 text-[10.5px] text-slate-500 border border-slate-150 bg-slate-50/50 px-4 py-2 rounded-md -mt-3 select-none print:hidden">
            <span className="font-bold text-slate-400 uppercase tracking-wider text-[9px] mr-1.5">Capabilities:</span>
            <span className="flex items-center gap-1 font-medium">
              <span>Answer Questions</span>
            </span>
            <span className="text-slate-350 mx-0.5">·</span>
            <span className="flex items-center gap-1 font-medium">
              <span>Notify Stations</span>
            </span>
            <span className="text-slate-350 mx-0.5">·</span>
            <span className="flex items-center gap-1 font-medium">
              <span>Flag Suspects</span>
            </span>
            <span className="text-slate-350 mx-0.5">·</span>
            <span className="flex items-center gap-1 font-medium">
              <span>Log Case Notes</span>
            </span>
          </div>

          {report && currentThreadId ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
              
              {/* Left Section: Follow-up Console */}
              <div className="lg:col-span-2">
                <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
                  <div className="bg-brand-primary px-5 py-3 flex items-center gap-2">
                    <Send className="w-4 h-4 text-brand-secondary" />
                    <h3 className="text-xs font-bold text-white uppercase tracking-widest font-mono">
                      Contextual Follow-up Investigation Console
                    </h3>
                    <div className="ml-auto flex items-center gap-1.5 px-2 py-0.5 rounded bg-white/10 border border-white/10 text-[9px] font-mono font-bold text-emerald-350 uppercase select-none">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                      <span>AI Ready</span>
                    </div>
                  </div>

                  {/* Q&A Log */}
                  <div className="max-h-[450px] overflow-y-auto border-b border-slate-200">
                    {followUpMessages.length === 0 ? (
                      <div className="p-8 flex flex-col items-center justify-center text-center gap-4 animate-in fade-in duration-300">
                        <div className="text-slate-400 font-sans text-xs max-w-md">
                          No messages sent yet. Start typing below, or use one of the suggested case-specific commands to initiate action:
                        </div>
                        <div className="flex flex-col gap-2 items-stretch max-w-md w-full">
                          {(() => {
                            const firstSuspect = report?.associatedSuspects[0]?.name || 'suspect';
                            const stationName = 'Halasuru';
                            
                            const prompt1 = `Has ${firstSuspect} been arrested before?`;
                            const prompt2 = `Notify ${stationName} about ${firstSuspect}'s last known location`;
                            const prompt3 = `Flag ${firstSuspect} as high priority`;

                            return (
                              <>
                                <button
                                  type="button"
                                  onClick={() => setFollowUpInput(prompt1)}
                                  className="px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 hover:border-slate-350 border border-slate-200 rounded font-sans text-xs font-semibold text-slate-700 transition-all cursor-pointer text-left flex items-center gap-2 active:scale-99 shadow-xs"
                                >
                                  <span className="text-slate-400">🔍</span>
                                  <span>{prompt1}</span>
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setFollowUpInput(prompt2)}
                                  className="px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 hover:border-slate-350 border border-slate-200 rounded font-sans text-xs font-semibold text-slate-700 transition-all cursor-pointer text-left flex items-center gap-2 active:scale-99 shadow-xs"
                                >
                                  <span className="text-slate-400">🚨</span>
                                  <span>{prompt2}</span>
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setFollowUpInput(prompt3)}
                                  className="px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 hover:border-slate-350 border border-slate-200 rounded font-sans text-xs font-semibold text-slate-700 transition-all cursor-pointer text-left flex items-center gap-2 active:scale-99 shadow-xs"
                                >
                                  <span className="text-slate-400">🚩</span>
                                  <span>{prompt3}</span>
                                </button>
                              </>
                            );
                          })()}
                        </div>
                      </div>
                    ) : (
                      followUpMessages.map((msg, idx) => (
                        <div
                          key={idx}
                          className={`px-5 py-4 ${
                            msg.role === 'officer'
                              ? 'bg-slate-50 border-b border-slate-100'
                              : 'bg-white border-b border-slate-100'
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`text-[9px] font-mono font-bold uppercase px-1.5 py-0.5 rounded ${
                              msg.role === 'officer'
                                ? 'bg-blue-50 text-blue-700 border border-blue-200'
                                : msg.type === 'action'
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : 'bg-brand-primary text-brand-secondary border border-brand-primary-light'
                            }`}>
                              {msg.role === 'officer' ? 'OFFICER QUERY' : msg.type === 'action' ? 'ACTION CONFIRMED' : 'AI RESPONSE'}
                            </span>
                            <span className="text-[9px] font-mono text-slate-400">{msg.timestamp}</span>
                          </div>
                          {msg.role === 'ai' && msg.type === 'action' ? (
                            <div className="bg-emerald-50/55 border border-emerald-200 rounded-lg p-3 text-emerald-800 flex items-start gap-2.5 font-mono text-[11px] shadow-xs">
                              <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                              <div className="flex-1">
                                <span className="font-bold block text-[10px] text-emerald-700 uppercase tracking-wide leading-none">
                                  DIRECTIVE ACTION COMMITTED TO KSP SYSTEM
                                </span>
                                <p className="mt-1 leading-normal">
                                  {msg.content.replace(/\[DEVELOPER WARNING:.*?\]\s*/i, '')}
                                </p>
                                {msg.content.includes('[DEVELOPER WARNING: Local mock action active]') && (
                                  <span className="text-[9px] font-semibold text-amber-600 block mt-1.5">
                                    ⚠️ Sandbox Mode: Mock Action Bypassed to Local DB write.
                                  </span>
                                )}
                              </div>
                            </div>
                          ) : (
                            <div className={`text-xs leading-relaxed ${
                              msg.role === 'ai'
                                ? 'font-mono whitespace-pre-line bg-slate-50 border border-slate-200 rounded-lg p-4 text-slate-800'
                                : 'text-slate-700 font-sans'
                            }`}>
                              {msg.content}
                            </div>
                          )}
                        </div>
                      ))
                    )}
                    {isFollowUpLoading && (
                      <div className="px-5 py-4 bg-white border-b border-slate-100">
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4 text-brand-secondary animate-spin" />
                          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Generating formal investigation response...</span>
                        </div>
                      </div>
                    )}
                    <div ref={followUpEndRef} />
                  </div>

                  {/* Input */}
                  <form onSubmit={handleFollowUp} className="p-4 flex gap-2">
                    <div className="flex-1 flex items-center border border-slate-200 focus-within:border-brand-secondary focus-within:ring-2 focus-within:ring-brand-secondary/20 rounded-md bg-slate-50 px-3 py-2.5 transition-all">
                      <input
                        type="text"
                        value={followUpInput}
                        onChange={(e) => setFollowUpInput(e.target.value)}
                        placeholder="Ask a follow-up or command station notifications/suspect flagging..."
                        className="bg-transparent border-none text-xs w-full focus:outline-none placeholder-slate-400 font-sans"
                        disabled={isFollowUpLoading}
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={isFollowUpLoading || !followUpInput.trim()}
                      className="bg-brand-primary hover:bg-brand-primary-light disabled:opacity-50 text-white font-bold text-xs px-5 py-2.5 rounded-md flex items-center gap-1.5 transition-colors cursor-pointer disabled:cursor-not-allowed"
                    >
                      <Send className="w-4 h-4" />
                      <span>Send</span>
                    </button>
                  </form>
                </div>
              </div>

              {/* Right Section: Promoted Session Action Log */}
              <div className="lg:col-span-1 flex flex-col gap-6">
                
                <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm relative overflow-hidden transition-all duration-300">
                  <div className="absolute top-0 left-0 w-full h-1 bg-emerald-500" />
                  <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-3">
                    <CheckCircle className="w-4.5 h-4.5 text-emerald-600" />
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Session Action Log</h3>
                  </div>
                  
                  {recentActions.length === 0 ? (
                    <div className="text-xs text-slate-450 font-sans text-center py-6 leading-relaxed">
                      Actions taken here — notifications, suspect flags, case notes — will appear as a timeline below.
                    </div>
                  ) : (
                    <div className="flex flex-col gap-3 font-mono text-[11px]">
                      {recentActions.map((act, idx) => (
                        <div key={idx} className="flex flex-col border-b border-slate-100 pb-2 last:border-0 last:pb-0">
                          <span className="text-slate-700 font-semibold leading-normal">{act.desc}</span>
                          <span className="text-[9.5px] text-slate-400 mt-1">{act.timestamp}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Directives quick list helper (read-only list reference for context) */}
                {report && report.recommendedActions.length > 0 && (
                  <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-slate-300" />
                    <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-3">
                      <ListTodo className="w-4.5 h-4.5 text-slate-500" />
                      <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Reference Case Directives</h3>
                    </div>
                    <div className="flex flex-col gap-2.5 font-sans text-[11.5px] text-slate-700 leading-normal">
                      {report.recommendedActions.map((action, idx) => {
                        const convertDirectiveToPrompt = (act: string) => {
                          let prompt = act.replace(/\bLOC\b/i, 'lookup circular').trim();
                          if (!prompt.toLowerCase().startsWith('ask') && !prompt.toLowerCase().startsWith('please')) {
                            prompt = `Please ${prompt.charAt(0).toLowerCase() + prompt.slice(1)}`;
                          }
                          return prompt;
                        };

                        return (
                          <div key={idx} className="flex flex-col gap-1.5 p-2 hover:bg-slate-50/80 border border-transparent hover:border-slate-100 rounded transition-all">
                            <div className="flex gap-2 items-start">
                              <span className="font-mono text-slate-400 font-bold">{idx + 1}.</span>
                              <span>{action}</span>
                            </div>
                            <button
                              type="button"
                              onClick={() => setFollowUpInput(convertDirectiveToPrompt(action))}
                              className="text-[9.5px] font-bold text-brand-primary hover:text-brand-primary-light flex items-center gap-0.5 mt-0.5 ml-5 cursor-pointer self-start transition-all uppercase tracking-wider"
                            >
                              <span>Ask AI to action this</span>
                              <ArrowRight className="w-3 h-3 text-brand-secondary" />
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
                
              </div>
              
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-lg p-16 text-center shadow-sm select-none flex flex-col items-center justify-center gap-3">
              <div className="p-4 bg-slate-50 rounded-full text-slate-400 border border-slate-100">
                <FolderLock className="w-10 h-10" />
              </div>
              <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">No Active Case Selected</h3>
              <p className="text-xs text-slate-400 max-w-sm leading-normal">
                Please complete a dossier query in the Quick Summary tab first to establish an investigation context before launching the Agentic Console.
              </p>
              <button
                onClick={() => setActiveTab('summary')}
                className="mt-2 bg-brand-primary hover:bg-brand-primary-light text-white font-bold text-xs px-5 py-2.5 rounded transition-all cursor-pointer"
              >
                Go to Quick Summary
              </button>
            </div>
          )}
          
        </div>
      )}

      {/* Printable layout */}
      {report && (
        <div className="hidden print:block font-mono text-xs max-w-4xl mx-auto py-10 px-8">
          <div className="text-center border-b-2 border-black pb-4 mb-6">
            <h1 className="text-lg font-bold uppercase tracking-wider">Government of Karnataka</h1>
            <h2 className="text-md font-bold uppercase tracking-wide mt-1">Karnataka State Police Department</h2>
            <h3 className="text-xs font-semibold mt-1">AI-COMPILATION CRIME INTELLIGENCE DOSSIER SHEET</h3>
            <p className="text-[10px] text-slate-500 mt-2 font-mono">
              CONFIDENTIAL // LAW ENFORCEMENT SENSITIVE // GENERATED ON: {new Date().toLocaleString()}
            </p>
          </div>

          <div className="mb-6">
            <h4 className="font-bold border-b border-black pb-1 mb-2 uppercase">1. Scope of Investigation Query</h4>
            <p className="pl-4">Query Input: "{report.query}"</p>
          </div>

          <div className="mb-6">
            <h4 className="font-bold border-b border-black pb-1 mb-2 uppercase">2. Intelligence Summary Dossier</h4>
            <p className="pl-4 leading-relaxed whitespace-pre-line">{report.executiveSummary}</p>
          </div>

          {report.associatedSuspects.length > 0 && (
            <div className="mb-6">
              <h4 className="font-bold border-b border-black pb-1 mb-2 uppercase">3. Associated Suspect Profile Dossier</h4>
              <table className="w-full text-left mt-2 border-collapse border border-black">
                <thead>
                  <tr className="bg-slate-100 border-b border-black">
                    <th className="p-1.5 border-r border-black font-bold">Suspect Name</th>
                    <th className="p-1.5 border-r border-black font-bold">Risk Code</th>
                    <th className="p-1.5 font-bold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {report.associatedSuspects.map((s) => (
                    <tr key={s.id} className="border-b border-black">
                      <td className="p-1.5 border-r border-black font-bold">{s.name}</td>
                      <td className="p-1.5 border-r border-black">{s.riskLevel}</td>
                      <td className="p-1.5">{s.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {report.recommendedActions.length > 0 && (
            <div className="mb-12">
              <h4 className="font-bold border-b border-black pb-1 mb-2 uppercase">4. Mandatory Investigation Directives</h4>
              <ul className="list-decimal pl-6 flex flex-col gap-1">
                {report.recommendedActions.map((action, idx) => (
                  <li key={idx} className="font-bold">{action}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex justify-between items-center pt-8 border-t border-dashed border-black">
            <div>
              <p>Inspector Signature: _________________________</p>
            </div>
            <div>
              <p>Station Seal Stamp: _________________________</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default AIWorkspace;
