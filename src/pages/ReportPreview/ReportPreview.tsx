import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Printer, FileText } from 'lucide-react';
import logo from '../../assets/ksp-logo.jpeg';
import type { IntelligenceReport } from '../../services/mockDb';
import { FIRs, POLICE_STATIONS, DISTRICTS } from '../../services/mockDb';
import './report-print.css';

/* ─── Helpers ─── */
function generateReportId(): string {
  const d = new Date();
  const seq = String(Math.floor(Math.random() * 9000) + 1000);
  return `KSP/CIB/${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${seq}`;
}

function fmt(d: Date): string {
  return d.toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
}

function riskColor(level: string): string {
  switch (level) { case 'Critical': return '#b91c1c'; case 'High': return '#c2410c'; case 'Medium': return '#b45309'; case 'Low': return '#15803d'; default: return '#333'; }
}

function severityLabel(s: string): string {
  switch (s) { case 'Critical': return '■ CRITICAL'; case 'Major': return '■ MAJOR'; case 'Moderate': return '■ MODERATE'; case 'Minor': return '■ MINOR'; default: return s; }
}

/* ═══════════════════════════════════════════════════════
   REPORT PREVIEW — Two-tier system
   Level 1: Executive AI Brief (default, 1-page)
   Level 2: Full Investigation Dossier (multi-page)
   ═══════════════════════════════════════════════════════ */
export const ReportPreview: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [view, setView] = useState<'brief' | 'full'>('brief');

  const report = location.state?.report as IntelligenceReport | undefined;
  const now = new Date();
  const reportId = React.useMemo(() => generateReportId(), []);

  const primaryFir = report?.relatedFirs?.[0] ?? FIRs[0];
  const primaryStation = POLICE_STATIONS.find((s) => s.id === primaryFir.stationId);
  const primaryDistrict = primaryStation ? DISTRICTS.find((d) => d.id === primaryStation.districtId) : DISTRICTS[0];

  if (!report) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: "'Inter', sans-serif", gap: 16 }}>
        <p style={{ fontSize: 14, color: '#64748b' }}>No report data available.</p>
        <button onClick={() => navigate(-1)} style={{ padding: '8px 20px', background: '#0f1e36', color: '#fff', border: 'none', fontSize: 12, fontWeight: 700, cursor: 'pointer' }}>
          ← Return to Intelligence Workspace
        </button>
      </div>
    );
  }

  return (
    <div className="report-page" style={{ background: '#f4f5f7', minHeight: '100vh' }}>
      {/* ── ACTION BAR ── */}
      <div className="report-action-bar" style={{ position: 'sticky', top: 0, zIndex: 100, background: '#0f1e36', padding: '10px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid #b89020' }}>
        <button onClick={() => navigate(-1)} style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#e2e8f0', background: 'transparent', border: '1px solid #334155', padding: '6px 14px', fontSize: 11, fontWeight: 700, fontFamily: "'Inter', sans-serif", cursor: 'pointer', letterSpacing: '0.05em' }}>
          <ArrowLeft size={14} /> BACK TO WORKSPACE
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <button
            onClick={() => setView('brief')}
            style={{ padding: '6px 14px', fontSize: 10, fontWeight: 800, fontFamily: "'Inter', sans-serif", cursor: 'pointer', letterSpacing: '0.06em', border: view === 'brief' ? '1px solid #b89020' : '1px solid #334155', background: view === 'brief' ? '#1e3a5f' : 'transparent', color: view === 'brief' ? '#b89020' : '#94a3b8' }}
          >
            EXECUTIVE BRIEF
          </button>
          <button
            onClick={() => setView('full')}
            style={{ padding: '6px 14px', fontSize: 10, fontWeight: 800, fontFamily: "'Inter', sans-serif", cursor: 'pointer', letterSpacing: '0.06em', border: view === 'full' ? '1px solid #b89020' : '1px solid #334155', background: view === 'full' ? '#1e3a5f' : 'transparent', color: view === 'full' ? '#b89020' : '#94a3b8' }}
          >
            FULL DOSSIER
          </button>
        </div>
        <button onClick={() => window.print()} style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#fff', background: '#b89020', border: 'none', padding: '8px 20px', fontSize: 11, fontWeight: 800, fontFamily: "'Inter', sans-serif", cursor: 'pointer', letterSpacing: '0.06em' }}>
          <Printer size={14} /> PRINT TO PDF
        </button>
      </div>

      {view === 'brief'
        ? <ExecutiveBrief report={report} reportId={reportId} now={now} primaryFir={primaryFir} primaryStation={primaryStation} primaryDistrict={primaryDistrict} onViewFull={() => setView('full')} />
        : <FullDossier report={report} reportId={reportId} now={now} primaryFir={primaryFir} primaryStation={primaryStation} primaryDistrict={primaryDistrict} />
      }
    </div>
  );
};

/* ═══════════════════════════════════════════════════════════
   LEVEL 1 — EXECUTIVE AI BRIEF (single page, < 60 seconds)
   ═══════════════════════════════════════════════════════════ */
interface BriefProps {
  report: IntelligenceReport;
  reportId: string;
  now: Date;
  primaryFir: any;
  primaryStation: any;
  primaryDistrict: any;
  onViewFull: () => void;
}

const ExecutiveBrief: React.FC<BriefProps> = ({ report, reportId, now, primaryFir, primaryStation, primaryDistrict, onViewFull }) => {
  const riskLevel = report.riskScore >= 70 ? 'HIGH' : report.riskScore >= 40 ? 'MEDIUM' : 'LOW';
  const riskBg = report.riskScore >= 70 ? '#b91c1c' : report.riskScore >= 40 ? '#b45309' : '#15803d';

  return (
    <div id="official-report" style={{ maxWidth: 800, margin: '0 auto', background: '#fff', padding: '36px 44px 32px', minHeight: '100vh', fontFamily: "'Inter', 'Arial', sans-serif", color: '#111', fontSize: 11 }}>

      {/* Classification Band */}
      <div className="report-classification-band">CONFIDENTIAL — EXECUTIVE AI BRIEF — KARNATAKA STATE POLICE</div>

      {/* ── HEADER ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', padding: '20px 0 14px', borderBottom: '2px solid #0f1e36' }}>
        {/* Left: Emblem + titles */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <img src={logo} alt="KSP Emblem" style={{ width: 52, height: 52, objectFit: 'contain', border: '1px solid #e2e8f0' }} />
          <div>
            <div style={{ fontSize: 8, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase', color: '#64748b' }}>Government of Karnataka</div>
            <div style={{ fontSize: 13, fontWeight: 900, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#0f1e36', marginTop: 1 }}>Karnataka State Police</div>
            <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#475569', marginTop: 1 }}>Crime Intelligence Bureau — Executive AI Brief</div>
          </div>
        </div>
        {/* Right: Report metadata */}
        <div style={{ textAlign: 'right', fontSize: 9, color: '#64748b', lineHeight: 1.6 }}>
          <div><strong style={{ color: '#0f1e36' }}>{reportId}</strong></div>
          <div>{fmt(now)}</div>
          <div>{primaryStation?.inCharge ?? '—'}</div>
          <div>{primaryStation?.name ?? '—'}</div>
        </div>
      </div>

      {/* ── RISK INDICATOR + CASE ID BAR ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'stretch', marginTop: 14, border: '1px solid #cbd5e1', fontSize: 10 }}>
        {/* Case meta */}
        <div style={{ display: 'flex', flex: 1 }}>
          <MiniMeta label="FIR" value={primaryFir.id} />
          <MiniMeta label="Category" value={primaryFir.category} />
          <MiniMeta label="District" value={primaryDistrict?.name ?? '—'} />
          <MiniMeta label="Status" value={primaryFir.status} />
        </div>
        {/* Risk badge */}
        <div style={{ background: riskBg, color: '#fff', padding: '10px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minWidth: 100 }}>
          <div style={{ fontSize: 8, fontWeight: 700, letterSpacing: '0.1em', opacity: 0.85 }}>RISK LEVEL</div>
          <div style={{ fontSize: 18, fontWeight: 900, letterSpacing: '0.05em', lineHeight: 1 }}>{riskLevel}</div>
          <div style={{ fontSize: 9, fontWeight: 700, marginTop: 2 }}>{report.riskScore}/100</div>
        </div>
      </div>

      {/* ── EXECUTIVE SUMMARY ── */}
      <div style={{ marginTop: 18 }}>
        <SectionTitle>Case Summary</SectionTitle>
        <p style={{ fontSize: 10.5, lineHeight: 1.65, textAlign: 'justify', color: '#1e293b', margin: 0 }}>
          {report.executiveSummary}
        </p>
      </div>

      {/* ── TWO-COLUMN: SUSPECTS + KEY FINDINGS ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 16 }}>

        {/* Primary Suspects */}
        <div>
          <SectionTitle>Primary Suspects ({report.associatedSuspects.length})</SectionTitle>
          <table className="report-table" style={{ fontSize: 9.5 }}>
            <thead>
              <tr>
                <th>Name</th>
                <th>Risk</th>
                <th>Status</th>
                <th>Gang</th>
              </tr>
            </thead>
            <tbody>
              {report.associatedSuspects.map((s) => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 700 }}>
                    {s.name}
                    {s.aliases.length > 0 && <div style={{ fontSize: 8, color: '#64748b', fontWeight: 400 }}>a.k.a. {s.aliases[0]}</div>}
                  </td>
                  <td style={{ color: riskColor(s.riskLevel), fontWeight: 800, fontSize: 9 }}>{s.riskLevel.toUpperCase()}</td>
                  <td style={{ fontSize: 9 }}>{s.status}</td>
                  <td style={{ fontSize: 9 }}>{s.gangAffiliation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Key Findings & Metrics */}
        <div>
          <SectionTitle>Key Findings</SectionTitle>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            <StatBox label="FIRs Linked" value={String(report.relatedFirs.length)} color="#0f1e36" />
            <StatBox label="Vehicles Flagged" value={String(report.relatedVehicles.length)} color="#c2410c" />
            <StatBox label="Evidence Items" value={String(report.evidence.length)} color="#15803d" />
            <StatBox label="ANPR Hits" value={String(report.relatedVehicles.reduce((a, v) => a + v.anprLogs.length, 0))} color="#7c3aed" />
            <StatBox label="Crime Locations" value={String(report.crimeLocations.length)} color="#0369a1" />
            <StatBox label="AI Confidence" value={`${report.riskScore}%`} color={riskBg} />
          </div>
        </div>
      </div>

      {/* ── VEHICLES (compact) ── */}
      <div style={{ marginTop: 16 }}>
        <SectionTitle>Flagged Vehicles</SectionTitle>
        <table className="report-table" style={{ fontSize: 9.5 }}>
          <thead>
            <tr>
              <th>Registration</th>
              <th>Vehicle</th>
              <th>Owner</th>
              <th>Status</th>
              <th>Last ANPR</th>
              <th>Hits</th>
            </tr>
          </thead>
          <tbody>
            {report.relatedVehicles.map((v) => {
              const last = v.anprLogs[0];
              return (
                <tr key={v.id}>
                  <td style={{ fontWeight: 800, fontFamily: "'Courier New', monospace", fontSize: 10 }}>{v.id}</td>
                  <td>{v.color} {v.make} {v.model}</td>
                  <td>{v.ownerName}</td>
                  <td style={{ fontWeight: 700, color: v.status === 'Flagged' ? '#b91c1c' : '#333' }}>{v.status}</td>
                  <td style={{ fontSize: 9 }}>{last ? `${last.locationName}` : '—'}</td>
                  <td style={{ textAlign: 'center', fontWeight: 700 }}>{v.anprLogs.length}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* ── RECOMMENDED ACTIONS (compact) ── */}
      <div style={{ marginTop: 16 }}>
        <SectionTitle>Recommended Actions</SectionTitle>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px 24px', fontSize: 10, lineHeight: 1.9 }}>
          {report.recommendedActions.map((a, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 5 }}>
              <span className="report-checkbox" style={{ marginTop: 4, flexShrink: 0 }} />
              <span>{a}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── EVIDENCE SNAPSHOT ── */}
      {report.evidence.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <SectionTitle>Evidence Snapshot</SectionTitle>
          <table className="report-table" style={{ fontSize: 9.5 }}>
            <thead>
              <tr><th>ID</th><th>Type</th><th>Source</th><th>Status</th></tr>
            </thead>
            <tbody>
              {report.evidence.map((e) => (
                <tr key={e.id}>
                  <td style={{ fontFamily: "'Courier New', monospace", fontWeight: 700 }}>{e.id}</td>
                  <td>{e.type}</td>
                  <td style={{ fontSize: 9 }}>{e.source}</td>
                  <td style={{ fontWeight: 700 }}>{e.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── VIEW FULL DOSSIER BUTTON ── */}
      <div className="report-action-bar" style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid #cbd5e1', display: 'flex', justifyContent: 'center' }}>
        <button
          onClick={onViewFull}
          style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '10px 28px',
            background: '#0f1e36', color: '#fff',
            border: '1px solid #1e3a5f',
            fontSize: 11, fontWeight: 800, fontFamily: "'Inter', sans-serif",
            letterSpacing: '0.06em', cursor: 'pointer',
          }}
        >
          <FileText size={15} />
          VIEW FULL INVESTIGATION DOSSIER
        </button>
      </div>

      {/* ── FOOTER ── */}
      <div style={{ marginTop: 20, borderTop: '2px solid #0f1e36', paddingTop: 6 }}>
        <div className="report-classification-band">CONFIDENTIAL — KARNATAKA STATE POLICE — CRIME INTELLIGENCE PLATFORM</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 7.5, color: '#94a3b8', marginTop: 6, fontFamily: "'Inter', sans-serif", letterSpacing: '0.04em' }}>
          <span>Generated by Karnataka State Police Crime Intelligence Platform (AI Module v1.0)</span>
          <span>Report ID: {reportId}</span>
          <span>{fmt(now)}</span>
        </div>
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════════════════════
   LEVEL 2 — FULL INVESTIGATION DOSSIER (multi-page)
   ═══════════════════════════════════════════════════════════ */
interface DossierProps {
  report: IntelligenceReport;
  reportId: string;
  now: Date;
  primaryFir: any;
  primaryStation: any;
  primaryDistrict: any;
}

const FullDossier: React.FC<DossierProps> = ({ report, reportId, now, primaryFir, primaryStation, primaryDistrict }) => {
  return (
    <div id="official-report" style={{ maxWidth: 800, margin: '0 auto', background: '#fff', padding: '40px 48px', minHeight: '100vh', fontFamily: "'Times New Roman', 'Georgia', serif", color: '#111', fontSize: 12, lineHeight: 1.55 }}>

      {/* CLASSIFICATION BAND */}
      <div className="report-classification-band">CONFIDENTIAL — FOR OFFICIAL USE ONLY — GOVERNMENT OF KARNATAKA</div>

      {/* HEADER */}
      <div style={{ textAlign: 'center', padding: '24px 0 16px', borderBottom: '2px solid #0f1e36' }}>
        <img src={logo} alt="Karnataka State Emblem" style={{ width: 64, height: 64, objectFit: 'contain', margin: '0 auto 8px' }} />
        <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 9, fontWeight: 800, letterSpacing: '0.2em', textTransform: 'uppercase', color: '#64748b' }}>Government of Karnataka</div>
        <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 900, letterSpacing: '0.14em', textTransform: 'uppercase', color: '#0f1e36', marginTop: 4 }}>Karnataka State Police</div>
        <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 10, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#475569', marginTop: 2 }}>Crime Intelligence Bureau</div>
        <div style={{ marginTop: 20 }}>
          <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 900, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#0f1e36' }}>Official AI Investigation Report</div>
          <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 9, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#b91c1c', marginTop: 6, padding: '3px 12px', border: '1px solid #b91c1c', display: 'inline-block' }}>Confidential — For Official Use Only</div>
        </div>
      </div>

      {/* METADATA GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, border: '1px solid #cbd5e1', marginTop: 16, fontFamily: "'Inter', sans-serif", fontSize: 10 }}>
        <div style={{ borderRight: '1px solid #cbd5e1' }}>
          <MetaRow label="Case ID" value={primaryFir.id.replace('FIR ', 'CASE-')} />
          <MetaRow label="FIR Number" value={primaryFir.id} border />
          <MetaRow label="District" value={primaryDistrict?.name ?? '—'} border />
          <MetaRow label="Classification" value={primaryFir.severity.toUpperCase()} border />
        </div>
        <div>
          <MetaRow label="Report ID" value={reportId} />
          <MetaRow label="Generated" value={fmt(now)} border />
          <MetaRow label="Officer" value={primaryStation?.inCharge ?? 'Rajesh Kumar'} border />
          <MetaRow label="Police Station" value={primaryStation?.name ?? '—'} border />
        </div>
      </div>

      {/* SECTION 1: EXECUTIVE SUMMARY */}
      <div style={{ marginTop: 32 }} className="report-avoid-break">
        <div className="report-section-header">Section 1 &nbsp;|&nbsp; Executive Summary</div>
        <p style={{ textAlign: 'justify', fontSize: 11.5, lineHeight: 1.65 }}>{report.executiveSummary}</p>
        <div style={{ marginTop: 10, fontSize: 10, color: '#64748b', fontFamily: "'Inter', sans-serif" }}>
          <strong>AI Confidence Index:</strong> {report.riskScore}% &nbsp;&nbsp;|&nbsp;&nbsp;
          <strong>Data Sources:</strong> FIR Database, ANPR Registry, Telecom CDR, CCTV Network
        </div>
      </div>

      {/* SECTION 2: CASE DETAILS */}
      <div style={{ marginTop: 28 }} className="report-page-break report-avoid-break">
        <div className="report-section-header">Section 2 &nbsp;|&nbsp; Case Details</div>
        <table className="report-table">
          <thead><tr><th style={{ width: '30%' }}>Field</th><th>Value</th></tr></thead>
          <tbody>
            {report.relatedFirs.map((fir) => {
              const station = POLICE_STATIONS.find((s) => s.id === fir.stationId);
              return (
                <React.Fragment key={fir.id}>
                  <tr><td><strong>FIR Number</strong></td><td>{fir.id}</td></tr>
                  <tr><td><strong>Police Station</strong></td><td>{station?.name ?? '—'}</td></tr>
                  <tr><td><strong>IPC Sections</strong></td><td>{fir.ipcSections.join('; ')}</td></tr>
                  <tr><td><strong>Crime Type</strong></td><td>{fir.category}</td></tr>
                  <tr><td><strong>Incident Date</strong></td><td>{new Date(fir.incidentDate).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</td></tr>
                  <tr><td><strong>Incident Time</strong></td><td>{new Date(fir.incidentDate).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true })}</td></tr>
                  <tr><td><strong>Severity</strong></td><td style={{ color: riskColor(fir.severity), fontWeight: 700 }}>{severityLabel(fir.severity)}</td></tr>
                  <tr><td><strong>Status</strong></td><td>{fir.status}</td></tr>
                  <tr><td><strong>Investigating Officer</strong></td><td>{station?.inCharge ?? '—'}</td></tr>
                  <tr><td><strong>Location</strong></td><td>{fir.locationName}</td></tr>
                  <tr><td><strong>Complainant</strong></td><td>{fir.reporterName}</td></tr>
                  {report.relatedFirs.length > 1 && <tr><td colSpan={2} style={{ background: '#e2e8f0', height: 2, padding: 0, border: 'none' }}></td></tr>}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* SECTION 3: PRIMARY SUSPECTS */}
      <div style={{ marginTop: 28 }} className="report-page-break report-avoid-break">
        <div className="report-section-header">Section 3 &nbsp;|&nbsp; Primary Suspects</div>
        <table className="report-table">
          <thead><tr><th>Photo</th><th>Name</th><th>Alias(es)</th><th>Risk Level</th><th>Status</th><th>FIRs</th><th>Gang Affiliation</th></tr></thead>
          <tbody>
            {report.associatedSuspects.map((suspect) => {
              const linkedFirCount = report.relatedFirs.filter((f) => f.suspectIds.includes(suspect.id)).length;
              return (
                <tr key={suspect.id}>
                  <td>
                    <div style={{ width: 36, height: 36, background: '#f1f5f9', border: '1px solid #cbd5e1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700, fontFamily: "'Inter', sans-serif", color: '#0f1e36' }}>
                      {suspect.name.split(' ').map((n) => n[0]).join('')}
                    </div>
                  </td>
                  <td style={{ fontWeight: 700 }}>{suspect.name}</td>
                  <td>{suspect.aliases.join(', ') || '—'}</td>
                  <td style={{ color: riskColor(suspect.riskLevel), fontWeight: 700 }}>{suspect.riskLevel.toUpperCase()}</td>
                  <td>{suspect.status}</td>
                  <td style={{ textAlign: 'center' }}>{linkedFirCount}</td>
                  <td>{suspect.gangAffiliation}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* SECTION 4: RELATED VEHICLES */}
      <div style={{ marginTop: 28 }} className="report-avoid-break">
        <div className="report-section-header">Section 4 &nbsp;|&nbsp; Related Vehicles</div>
        <table className="report-table">
          <thead><tr><th>Registration No.</th><th>Owner</th><th>Vehicle Type</th><th>Status</th><th>Last Seen</th><th>ANPR Hits</th></tr></thead>
          <tbody>
            {report.relatedVehicles.map((v) => {
              const lastLog = v.anprLogs[0];
              return (
                <tr key={v.id}>
                  <td style={{ fontWeight: 700, fontFamily: "'Courier New', monospace" }}>{v.id}</td>
                  <td>{v.ownerName}</td>
                  <td>{v.color} {v.make} {v.model}</td>
                  <td style={{ fontWeight: 700, color: v.status === 'Flagged' ? '#b91c1c' : '#333' }}>{v.status}</td>
                  <td style={{ fontSize: 10 }}>{lastLog ? `${lastLog.locationName} (${new Date(lastLog.timestamp).toLocaleDateString('en-IN')})` : '—'}</td>
                  <td style={{ textAlign: 'center', fontWeight: 700 }}>{v.anprLogs.length}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* SECTION 5: EVIDENCE SUMMARY */}
      <div style={{ marginTop: 28 }} className="report-page-break report-avoid-break">
        <div className="report-section-header">Section 5 &nbsp;|&nbsp; Evidence Summary</div>
        {report.evidence.length > 0 ? (
          <table className="report-table">
            <thead><tr><th>Evidence ID</th><th>Type</th><th>Description</th><th>Source</th><th>Status</th></tr></thead>
            <tbody>
              {report.evidence.map((ev) => (
                <tr key={ev.id}>
                  <td style={{ fontFamily: "'Courier New', monospace", fontWeight: 700 }}>{ev.id}</td>
                  <td>{ev.type}</td>
                  <td style={{ fontSize: 10 }}>{ev.description}</td>
                  <td style={{ fontSize: 10 }}>{ev.source}</td>
                  <td style={{ fontWeight: 700 }}>{ev.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#64748b', fontStyle: 'italic' }}>No evidence entries linked to this investigation.</p>
        )}
      </div>

      {/* SECTION 6: TIMELINE */}
      <div style={{ marginTop: 28 }} className="report-page-break report-avoid-break">
        <div className="report-section-header">Section 6 &nbsp;|&nbsp; Investigation Timeline</div>
        <div style={{ paddingLeft: 20 }}>
          {report.timeline.map((entry, idx) => (
            <div key={idx} style={{ display: 'flex', gap: 16 }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: 20 }}>
                <div className="report-timeline-dot" />
                {idx < report.timeline.length - 1 && <div className="report-timeline-line" />}
              </div>
              <div style={{ paddingBottom: 18 }}>
                <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 9, fontWeight: 700, color: '#64748b', letterSpacing: '0.06em', textTransform: 'uppercase' }}>{entry.time}</div>
                <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 800, color: '#0f1e36', marginTop: 2 }}>
                  {entry.event}
                  <span style={{ marginLeft: 8, fontSize: 8, fontWeight: 700, color: riskColor(entry.severity), letterSpacing: '0.08em', textTransform: 'uppercase', border: `1px solid ${riskColor(entry.severity)}`, padding: '1px 5px' }}>{entry.severity}</span>
                </div>
                <div style={{ fontSize: 10.5, color: '#333', marginTop: 3, lineHeight: 1.5 }}>{entry.description}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SECTION 7: AI FINDINGS */}
      <div style={{ marginTop: 28 }} className="report-page-break report-avoid-break">
        <div className="report-section-header">Section 7 &nbsp;|&nbsp; AI Analytical Findings</div>
        <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, lineHeight: 1.7 }}>
          <div style={{ display: 'flex', gap: 24, marginBottom: 14 }}>
            <div>
              <span style={{ fontSize: 9, fontWeight: 700, color: '#64748b', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Risk Level</span>
              <div style={{ fontWeight: 800, fontSize: 14, color: report.riskScore >= 70 ? '#b91c1c' : report.riskScore >= 40 ? '#b45309' : '#15803d', marginTop: 2 }}>
                {report.riskScore >= 70 ? 'HIGH RISK' : report.riskScore >= 40 ? 'MEDIUM RISK' : 'LOW RISK'}
              </div>
            </div>
            <div>
              <span style={{ fontSize: 9, fontWeight: 700, color: '#64748b', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Confidence Score</span>
              <div style={{ fontWeight: 800, fontSize: 14, color: '#0f1e36', marginTop: 2 }}>{report.riskScore}%</div>
            </div>
          </div>
          <BulletItem title="AI Conclusion">
            {report.riskScore >= 70
              ? 'AI analysis confirms strong correlational links between the identified suspects, vehicles, and incident locations. Multiple independent data sources converge on the same suspects and vehicle assets.'
              : 'AI analysis identifies partial correlational links. Further investigation and data corroboration is recommended before drawing actionable conclusions.'}
          </BulletItem>
          <BulletItem title="Supporting Evidence">
            {report.evidence.length > 0
              ? report.evidence.map((e) => `${e.id} (${e.type} — ${e.status})`).join('; ')
              : 'No physical/digital evidence catalogued for this investigation.'}
          </BulletItem>
          <BulletItem title="Contradicting Evidence">No contradicting evidence identified in current dataset. Manual review recommended.</BulletItem>
          <BulletItem title="Data Sources Used">
            FIR Database ({report.relatedFirs.length} records); ANPR Registry ({report.relatedVehicles.reduce((a, v) => a + v.anprLogs.length, 0)} hits); Telecom CDR Logs; CCTV Camera Network ({report.crimeLocations.length} locations); Suspect Criminal Records Database.
          </BulletItem>
        </div>
      </div>

      {/* SECTION 8: OFFICER RECOMMENDATIONS */}
      <div style={{ marginTop: 28 }} className="report-avoid-break">
        <div className="report-section-header">Section 8 &nbsp;|&nbsp; Officer Recommendations</div>
        <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, lineHeight: 2.2 }}>
          {report.recommendedActions.map((action, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: 4 }}>
              <span className="report-checkbox" /><span>{action}</span>
            </div>
          ))}
          <div style={{ marginTop: 8, borderTop: '1px solid #e2e8f0', paddingTop: 8 }}>
            <div style={{ fontSize: 9, fontWeight: 700, color: '#64748b', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 6 }}>Standard Operational Directives</div>
            {['Issue Lookout Circular (LOC)', 'Deploy Intercept Patrol Units', 'Collect and Preserve CCTV Footage', 'Obtain Call Detail Records (CDR)', 'Interrogate Primary Suspect(s)', 'Search and Seize Flagged Vehicle(s)'].map((item, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: 4 }}>
                <span className="report-checkbox" /><span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SECTION 9: DIGITAL SIGNATURES */}
      <div style={{ marginTop: 36 }} className="report-page-break report-avoid-break">
        <div className="report-section-header">Section 9 &nbsp;|&nbsp; Digital Signatures &amp; Attestation</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 24, marginTop: 16, fontFamily: "'Inter', sans-serif", fontSize: 10 }}>
          <SigBlock title="Prepared By" name={primaryStation?.inCharge ?? '—'} designation={primaryStation?.name ?? '—'} />
          <SigBlock title="Reviewed By" name="Superintendent of Police" designation={`${primaryDistrict?.name ?? '—'} District`} />
          <SigBlock title="Approved By" name="Deputy Inspector General" designation="Crime Intelligence Bureau" />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginTop: 32, paddingTop: 16, borderTop: '1px solid #cbd5e1' }}>
          <div>
            <div style={{ fontSize: 8, fontWeight: 700, color: '#64748b', letterSpacing: '0.1em', textTransform: 'uppercase', fontFamily: "'Inter', sans-serif", marginBottom: 8 }}>Official Seal</div>
            <div style={{ width: 90, height: 90, border: '2px dashed #94a3b8', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94a3b8', fontSize: 9, fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>OFFICIAL<br/>SEAL</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 8, fontWeight: 700, color: '#64748b', letterSpacing: '0.1em', textTransform: 'uppercase', fontFamily: "'Inter', sans-serif", marginBottom: 8 }}>QR Verification</div>
            <div className="report-qr-placeholder">
              <svg viewBox="0 0 80 80" width="70" height="70">
                <rect x="4" y="4" width="24" height="24" fill="#0f1e36" rx="2" />
                <rect x="8" y="8" width="16" height="16" fill="#fff" rx="1" />
                <rect x="11" y="11" width="10" height="10" fill="#0f1e36" rx="1" />
                <rect x="52" y="4" width="24" height="24" fill="#0f1e36" rx="2" />
                <rect x="56" y="8" width="16" height="16" fill="#fff" rx="1" />
                <rect x="59" y="11" width="10" height="10" fill="#0f1e36" rx="1" />
                <rect x="4" y="52" width="24" height="24" fill="#0f1e36" rx="2" />
                <rect x="8" y="56" width="16" height="16" fill="#fff" rx="1" />
                <rect x="11" y="59" width="10" height="10" fill="#0f1e36" rx="1" />
                <rect x="34" y="4" width="6" height="6" fill="#0f1e36" />
                <rect x="34" y="16" width="6" height="6" fill="#0f1e36" />
                <rect x="44" y="34" width="6" height="6" fill="#0f1e36" />
                <rect x="34" y="34" width="6" height="6" fill="#0f1e36" />
                <rect x="54" y="34" width="6" height="6" fill="#0f1e36" />
                <rect x="64" y="34" width="6" height="6" fill="#0f1e36" />
                <rect x="34" y="44" width="6" height="6" fill="#0f1e36" />
                <rect x="54" y="54" width="6" height="6" fill="#0f1e36" />
                <rect x="64" y="54" width="6" height="6" fill="#0f1e36" />
                <rect x="54" y="64" width="6" height="6" fill="#0f1e36" />
                <rect x="64" y="64" width="6" height="6" fill="#0f1e36" />
                <rect x="34" y="64" width="6" height="6" fill="#0f1e36" />
                <rect x="4" y="34" width="6" height="6" fill="#0f1e36" />
                <rect x="16" y="34" width="6" height="6" fill="#0f1e36" />
                <rect x="4" y="44" width="6" height="6" fill="#0f1e36" />
                <rect x="16" y="44" width="6" height="6" fill="#0f1e36" />
              </svg>
            </div>
            <div style={{ fontSize: 7, color: '#94a3b8', fontFamily: "'Courier New', monospace", marginTop: 4 }}>{reportId}</div>
          </div>
        </div>
      </div>

      {/* FOOTER */}
      <div style={{ marginTop: 36, borderTop: '2px solid #0f1e36', paddingTop: 10 }}>
        <div className="report-classification-band">CONFIDENTIAL — KARNATAKA STATE POLICE — CRIME INTELLIGENCE PLATFORM</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 8, color: '#94a3b8', marginTop: 8, fontFamily: "'Inter', sans-serif", letterSpacing: '0.04em' }}>
          <span>Generated by Karnataka State Police Crime Intelligence Platform (AI Module v1.0)</span>
          <span>Report ID: {reportId}</span>
          <span>{fmt(now)}</span>
        </div>
      </div>
    </div>
  );
};

/* ─── SHARED SUB-COMPONENTS ─── */

const SectionTitle: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ fontFamily: "'Inter', 'Arial', sans-serif", fontSize: 10, fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#0f1e36', borderBottom: '1.5px solid #0f1e36', paddingBottom: 4, marginBottom: 10 }}>
    {children}
  </div>
);

const MiniMeta: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div style={{ padding: '8px 12px', borderRight: '1px solid #e2e8f0', flex: 1 }}>
    <div style={{ fontSize: 8, fontWeight: 700, color: '#94a3b8', letterSpacing: '0.08em', textTransform: 'uppercase' }}>{label}</div>
    <div style={{ fontSize: 10, fontWeight: 700, color: '#0f172a', marginTop: 2, lineHeight: 1.3 }}>{value}</div>
  </div>
);

const StatBox: React.FC<{ label: string; value: string; color: string }> = ({ label, value, color }) => (
  <div style={{ border: '1px solid #e2e8f0', padding: '8px 10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <span style={{ fontSize: 9, fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</span>
    <span style={{ fontSize: 16, fontWeight: 900, color, fontFamily: "'Inter', sans-serif" }}>{value}</span>
  </div>
);

const MetaRow: React.FC<{ label: string; value: string; border?: boolean }> = ({ label, value, border }) => (
  <div style={{ display: 'flex', borderTop: border ? '1px solid #e2e8f0' : 'none', padding: '6px 12px' }}>
    <span style={{ width: '40%', fontWeight: 700, fontSize: 9, color: '#64748b', letterSpacing: '0.06em', textTransform: 'uppercase' }}>{label}</span>
    <span style={{ fontWeight: 600, fontSize: 10, color: '#0f172a' }}>{value}</span>
  </div>
);

const BulletItem: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div style={{ marginBottom: 10 }}>
    <div style={{ fontWeight: 800, fontSize: 10, color: '#0f1e36', letterSpacing: '0.04em', textTransform: 'uppercase', marginBottom: 2 }}>▸ {title}</div>
    <div style={{ paddingLeft: 14, fontSize: 10.5, color: '#333', lineHeight: 1.55 }}>{children}</div>
  </div>
);

const SigBlock: React.FC<{ title: string; name: string; designation: string }> = ({ title, name, designation }) => (
  <div>
    <div style={{ fontSize: 8, fontWeight: 700, color: '#64748b', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 8 }}>{title}</div>
    <div className="report-sig-line" />
    <div style={{ marginTop: 6, fontWeight: 600 }}>{name}</div>
    <div style={{ color: '#64748b', fontSize: 9 }}>{designation}</div>
  </div>
);

export default ReportPreview;
