/**
 * Investigation API client.
 *
 * Calls the FastAPI backend's investigation pipeline and maps the response
 * into the frontend IntelligenceReport shape.  Falls back to the local
 * mockDb queryIntelligence() when the backend is unreachable.
 *
 * Thread-aware: sends/receives thread_id to distinguish fresh queries from
 * follow-ups.  Checks the `status` field (not string matching) to detect
 * zero-result / insufficient-data responses.
 */

import { queryIntelligence } from './mockDb';
import type { IntelligenceReport } from './mockDb';

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const API_BASE =
  import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api/v1';

// ---------------------------------------------------------------------------
// Backend response types  (mirrors backend/app/investigation/dto.py)
// ---------------------------------------------------------------------------

interface BackendEntity {
  value: string;
  entity_type: string;
  confidence: number;
  source: string;
  metadata: Record<string, unknown>;
}

interface BackendEvidence {
  id: string;
  evidence_type: string;
  title: string;
  summary: string;
  occurred_at: string | null;
  source: string;
  confidence: number;
  relevance_score: number;
  risk_weight: number;
  metadata: Record<string, unknown>;
}

interface BackendTimeline {
  title: string;
  occurred_at: string;
  description: string;
  evidence_ids: string[];
  confidence: number;
}

interface BackendRisk {
  score: number;
  level: string;
  factors: string[];
}

interface BackendRecommendation {
  title: string;
  description: string;
  priority: string;
  rationale: string;
  related_evidence_ids: string[];
}

interface BackendInvestigationResponse {
  thread_id: string;
  is_follow_up: boolean;
  status: 'success' | 'insufficient_data';
  query: { query_text: string; requested_by: string };
  entities: BackendEntity[];
  evidence: BackendEvidence[];
  timeline: BackendTimeline[];
  risk: BackendRisk;
  recommendations: BackendRecommendation[];
  report_text: string;
  type: 'report' | 'action';
  metadata: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Follow-up chat types
// ---------------------------------------------------------------------------

export interface FollowUpMessage {
  role: 'officer' | 'ai';
  content: string;
  timestamp: string;
  type?: 'report' | 'action';
}

// ---------------------------------------------------------------------------
// Investigation result — extends IntelligenceReport with thread metadata
// ---------------------------------------------------------------------------

export interface InvestigationResult {
  report: IntelligenceReport;
  source: 'backend' | 'mock';
  threadId: string;
  isFollowUp: boolean;
  status: 'success' | 'insufficient_data';
  reportText: string;
  type?: 'report' | 'action';
}

// ---------------------------------------------------------------------------
// Severity mapping helpers
// ---------------------------------------------------------------------------

function mapSeverity(riskWeight: number): 'Critical' | 'Major' | 'Moderate' | 'Minor' {
  if (riskWeight >= 0.8) return 'Critical';
  if (riskWeight >= 0.6) return 'Major';
  if (riskWeight >= 0.3) return 'Moderate';
  return 'Minor';
}

function mapEvidenceType(type: string): 'Physical' | 'Digital' | 'Circumstantial' | 'Forensic' {
  switch (type) {
    case 'fir': return 'Physical';
    case 'suspect': return 'Circumstantial';
    case 'vehicle': return 'Physical';
    case 'cctv': return 'Digital';
    case 'call_log': return 'Digital';
    case 'report': return 'Forensic';
    default: return 'Circumstantial';
  }
}

// ---------------------------------------------------------------------------
// Map backend response → frontend IntelligenceReport
// ---------------------------------------------------------------------------

function mapToIntelligenceReport(
  queryText: string,
  data: BackendInvestigationResponse,
): IntelligenceReport {
  // Build executive summary from evidence titles + risk factors
  const topEvidence = data.evidence.slice(0, 5);
  const summaryLines = topEvidence.map(e => `• ${e.title}: ${e.summary}`).join('\n');
  const riskFactors = data.risk.factors.join(', ');

  const executiveSummary =
    `AI-Synthesized Brief: Investigation query "${queryText}" returned ${data.evidence.length} evidence items ` +
    `across ${data.entities.length} extracted entities. Risk assessment: ${data.risk.level.toUpperCase()} ` +
    `(Score: ${data.risk.score}/100). Key risk drivers: ${riskFactors || 'None identified'}.\n\n` +
    `Key findings:\n${summaryLines || 'No detailed findings available.'}`;

  // Map FIR evidence items
  const relatedFirs = data.evidence
    .filter(e => e.evidence_type === 'fir')
    .map(e => ({
      id: e.title || e.id,
      stationId: 'ps-km',
      category: (e.metadata.crime_group as string) || 'General',
      ipcSections: [] as string[],
      incidentDate: e.occurred_at || '',
      registrationDate: e.occurred_at || '',
      severity: mapSeverity(e.risk_weight),
      status: 'Active' as const,
      summary: e.summary,
      suspectIds: ((e.metadata.accused_names as string[]) || []).map((_, i) => `susp-${i}`),
      vehicleIds: [] as string[],
      evidenceIds: [e.id],
      witnessIds: [] as string[],
      reporterName: 'KSP Investigation System',
      locationName: (e.metadata.crime_group as string) || 'Karnataka',
      latitude: (e.metadata.latitude as number) || 12.9345,
      longitude: (e.metadata.longitude as number) || 77.6268,
    }));

  // Map suspect evidence items
  const associatedSuspects = data.evidence
    .filter(e => e.evidence_type === 'suspect')
    .map(e => ({
      id: e.id,
      name: (e.metadata.name as string) || e.title.replace('Accused: ', ''),
      aliases: [] as string[],
      age: 0,
      biometricId: '',
      riskLevel: mapSeverity(e.risk_weight) === 'Critical' ? 'Critical' as const : 'High' as const,
      gangAffiliation: 'Under Investigation',
      status: 'Under Surveillance' as const,
      phoneNo: '',
      aadhaarNo: '',
      bio: e.summary,
      photoPlaceholder: e.risk_weight >= 0.8
        ? 'bg-red-50 text-red-700 border-red-200'
        : 'bg-orange-50 text-orange-700 border-orange-200',
    }));

  // Map vehicle evidence items
  const relatedVehicles = data.evidence
    .filter(e => e.evidence_type === 'vehicle')
    .map(e => ({
      id: e.id,
      model: '',
      make: '',
      color: '',
      ownerName: (e.metadata.name as string) || 'Unknown',
      ownerAadhaar: '',
      status: 'Flagged' as const,
      anprLogs: [],
    }));

  // Crime locations from evidence metadata
  const crimeLocations = data.evidence
    .filter(e => e.metadata.latitude && e.metadata.longitude)
    .slice(0, 5)
    .map(e => ({
      name: (e.metadata.crime_group as string) || e.title,
      latitude: e.metadata.latitude as number,
      longitude: e.metadata.longitude as number,
      description: e.summary.slice(0, 100),
    }));

  // Timeline
  const timeline = data.timeline.map(t => ({
    time: t.occurred_at,
    event: t.title,
    description: t.description,
    severity: (t.confidence >= 0.8 ? 'Critical' : t.confidence >= 0.5 ? 'Major' : 'Minor') as 'Critical' | 'Major' | 'Moderate' | 'Minor',
  }));

  // Evidence vault
  const evidence = data.evidence.slice(0, 8).map(e => ({
    id: e.id,
    type: mapEvidenceType(e.evidence_type),
    description: e.summary.slice(0, 120),
    source: e.source,
    dateSecured: e.occurred_at || new Date().toISOString(),
    status: 'Secured' as const,
    storageLocation: 'KSP Digital Evidence Vault',
  }));

  // Network graph
  const nodes = [
    ...associatedSuspects.map(s => ({
      id: s.id,
      label: s.name,
      type: 'suspect' as const,
      group: s.gangAffiliation,
      status: s.status,
    })),
    ...relatedVehicles.map(v => ({
      id: v.id,
      label: v.id,
      type: 'vehicle' as const,
      group: 'Vehicles',
    })),
  ];

  const edges = associatedSuspects
    .filter((_, i) => i > 0)
    .map(s => ({
      source: associatedSuspects[0]?.id || '',
      target: s.id,
      label: 'Co-accused (Case link)',
      relationType: 'co-accused',
    }));

  return {
    query: queryText,
    executiveSummary,
    relatedFirs,
    associatedSuspects,
    relatedVehicles,
    crimeLocations: crimeLocations.length > 0
      ? crimeLocations
      : [{ name: 'Karnataka', latitude: 12.9345, longitude: 77.6268, description: 'Default jurisdiction' }],
    timeline: timeline.length > 0
      ? timeline
      : [{ time: new Date().toISOString(), event: 'Investigation Initiated', description: 'Query submitted to KSP AI Investigation Engine.', severity: 'Minor' as const }],
    networkGraph: { nodes, edges },
    evidence,
    riskScore: data.risk.score,
    recommendedActions: data.recommendations.map(r => `[${r.priority.toUpperCase()}] ${r.title}: ${r.description}`),
  };
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Run the investigation pipeline.  Tries the real backend first, falls back
 * to the local mock when the backend is unreachable.
 *
 * @param threadId  Pass an existing thread_id to make this a follow-up query.
 * @param conversationHistory  Prior Q&A turns for follow-up context.
 */
export async function runInvestigation(
  queryText: string,
  threadId?: string,
  conversationHistory?: { role: string; content: string }[],
): Promise<InvestigationResult> {
  try {
    const res = await fetch(`${API_BASE}/investigation/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query_text: queryText,
        requested_by: 'officer-demo',
        thread_id: threadId || null,
        is_follow_up: !!threadId,
        conversation_history: conversationHistory || [],
      }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data: BackendInvestigationResponse = await res.json();
    return {
      report: mapToIntelligenceReport(queryText, data),
      source: 'backend',
      threadId: data.thread_id,
      isFollowUp: data.is_follow_up,
      status: data.status,
      reportText: data.report_text,
      type: data.type || 'report',
    };
  } catch {
    // Backend unreachable — fall back to local mock
    return {
      report: queryIntelligence(queryText),
      source: 'mock',
      threadId: `mock-${Date.now()}`,
      isFollowUp: false,
      status: 'success',
      reportText: '',
      type: 'report',
    };
  }
}

/**
 * Send a follow-up question via the thread-aware /query endpoint.
 * Returns the formal report text and status flag.
 */
export async function sendFollowUp(
  queryText: string,
  threadId: string,
  conversationHistory: { role: string; content: string }[],
): Promise<{ text: string; status: 'success' | 'insufficient_data'; source: 'backend' | 'mock'; type: 'report' | 'action' }> {
  try {
    const res = await fetch(`${API_BASE}/investigation/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query_text: queryText,
        requested_by: 'officer-demo',
        thread_id: threadId,
        is_follow_up: true,
        conversation_history: conversationHistory,
      }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data: BackendInvestigationResponse = await res.json();
    return {
      text: data.report_text,
      status: data.status,
      source: 'backend',
      type: data.type || 'report',
    };
  } catch {
    const isAction = queryText.toLowerCase().includes('notify station') || 
                     queryText.toLowerCase().includes('flag suspect') || 
                     queryText.toLowerCase().includes('flag accused') || 
                     queryText.toLowerCase().includes('case note') ||
                     queryText.toLowerCase().includes('add note');
    
    let reportText = '';
    if (isAction) {
      let desc = 'Action executed';
      if (queryText.toLowerCase().includes('notify station')) {
        desc = 'Notified station Nazarbad PS regarding suspect alert';
      } else if (queryText.toLowerCase().includes('flag suspect') || queryText.toLowerCase().includes('flag accused')) {
        desc = 'Flagged suspect as active threat';
      } else if (queryText.toLowerCase().includes('case note') || queryText.toLowerCase().includes('add note')) {
        desc = 'Added official case note';
      }
      reportText = `[DEVELOPER WARNING: Local mock action active]\n\nACTION TAKEN: ${desc}, ${new Date().toISOString()}.`;
    } else {
      reportText = `SYSTEM EXCEPTION: Connection to the central intelligence database (backend) is currently unavailable.\n\nUnable to process real-time query for: "${queryText}". Please ensure the backend server is running and network connectivity is active.`;
    }

    return {
      text: reportText,
      status: 'success',
      source: 'mock',
      type: isAction ? 'action' : 'report',
    };
  }
}
