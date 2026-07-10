export interface District {
  id: string;
  name: string;
  region: string;
  code: string;
}

export interface PoliceStation {
  id: string;
  name: string;
  districtId: string;
  latitude: number;
  longitude: number;
  inCharge: string;
}

export interface Officer {
  id: string;
  name: string;
  rank: string;
  badgeNo: string;
  stationId: string;
  shift: string;
  status: 'Active' | 'On Leave' | 'On Field';
  avatarUrl: string;
}

export interface Suspect {
  id: string;
  name: string;
  aliases: string[];
  age: number;
  biometricId: string;
  riskLevel: 'Critical' | 'High' | 'Medium' | 'Low';
  gangAffiliation: string;
  status: 'Absconding' | 'Under Surveillance' | 'Detained' | 'In Custody' | 'Acquitted';
  associatedVehicleId?: string;
  phoneNo: string;
  aadhaarNo: string;
  bio: string;
  photoPlaceholder: string; // Tailwind color class or initial
}

export interface Vehicle {
  id: string; // License plate
  model: string;
  make: string;
  color: string;
  ownerName: string;
  ownerAadhaar: string;
  status: 'Flagged' | 'Under Investigation' | 'Seized' | 'Clean';
  anprLogs: ANPRLog[];
}

export interface ANPRLog {
  timestamp: string;
  cctvId: string;
  locationName: string;
  latitude: number;
  longitude: number;
  confidence: number;
}

export interface FIR {
  id: string; // e.g., FIR 104/2026
  stationId: string;
  category: string;
  ipcSections: string[];
  incidentDate: string;
  registrationDate: string;
  severity: 'Critical' | 'Major' | 'Moderate' | 'Minor';
  status: 'Active' | 'Under Review' | 'Closed (Charge Sheeted)' | 'Suspended';
  summary: string;
  suspectIds: string[];
  vehicleIds: string[];
  evidenceIds: string[];
  witnessIds: string[];
  reporterName: string;
  locationName: string;
  latitude: number;
  longitude: number;
}

export interface Evidence {
  id: string;
  type: 'Physical' | 'Digital' | 'Circumstantial' | 'Forensic';
  description: string;
  source: string;
  dateSecured: string;
  status: 'Secured' | 'In Lab' | 'Presented in Court' | 'Missing';
  storageLocation: string;
}

export interface Witness {
  id: string;
  name: string;
  statement: string;
  credibility: 'High' | 'Medium' | 'Low';
  contact: string;
}

export interface CallLog {
  id: string;
  fromNo: string;
  fromName: string;
  toNo: string;
  toName: string;
  timestamp: string;
  durationSeconds: number;
  cellTowerId: string;
}

export interface CCTVRecord {
  id: string;
  locationName: string;
  latitude: number;
  longitude: number;
  status: 'Operational' | 'Maintenance' | 'Faulty';
  feedUrl?: string;
}

// -----------------------------------------
// STATIC CENTRAL DATABASE INSTANCE
// -----------------------------------------

export const DISTRICTS: District[] = [
  { id: 'blr', name: 'Bengaluru City', region: 'South', code: 'KA-01' },
  { id: 'mys', name: 'Mysuru City', region: 'South', code: 'KA-09' },
  { id: 'mng', name: 'Mangaluru City', region: 'Coastal', code: 'KA-19' },
  { id: 'hub', name: 'Hubballi-Dharwad', region: 'North', code: 'KA-25' },
  { id: 'bel', name: 'Belagavi District', region: 'North', code: 'KA-22' },
  { id: 'klb', name: 'Kalaburagi', region: 'Northeast', code: 'KA-32' },
];

export const POLICE_STATIONS: PoliceStation[] = [
  { id: 'ps-km', name: 'Koramangala Police Station', districtId: 'blr', latitude: 12.9345, longitude: 77.6268, inCharge: 'Inspector Rajesh Kumar' },
  { id: 'ps-in', name: 'Indiranagar Police Station', districtId: 'blr', latitude: 12.9719, longitude: 77.6412, inCharge: 'Inspector Asha Gowda' },
  { id: 'ps-mj', name: 'Majestic Metro PS', districtId: 'blr', latitude: 12.9779, longitude: 77.5721, inCharge: 'Inspector Girish S.' },
  { id: 'ps-wf', name: 'Whitefield Police Station', districtId: 'blr', latitude: 12.9698, longitude: 77.7500, inCharge: 'Inspector Mahesh M.' },
  { id: 'ps-jn', name: 'Jayanagar Police Station', districtId: 'blr', latitude: 12.9308, longitude: 77.5802, inCharge: 'Inspector Venkatesh D.' },
];

export const OFFICERS: Officer[] = [
  { id: 'off-01', name: 'Rajesh Kumar', rank: 'Inspector of Police', badgeNo: 'KSP-9432', stationId: 'ps-km', shift: 'Night Shift (20:00 - 08:00)', status: 'Active', avatarUrl: 'RK' },
  { id: 'off-02', name: 'Asha Gowda', rank: 'Inspector of Police', badgeNo: 'KSP-7741', stationId: 'ps-in', status: 'On Field', shift: 'Day Shift (08:00 - 20:00)', avatarUrl: 'AG' },
  { id: 'off-03', name: 'Girish S.', rank: 'Inspector of Police', badgeNo: 'KSP-3211', stationId: 'ps-mj', status: 'Active', shift: 'Day Shift (08:00 - 20:00)', avatarUrl: 'GS' },
];

export const SUSPECTS: Suspect[] = [
  {
    id: 'susp-01',
    name: 'Vikram Hegde',
    aliases: ['Vicky', 'Hegde Bhai'],
    age: 39,
    biometricId: 'BIO-7729-KA',
    riskLevel: 'Critical',
    gangAffiliation: 'Central-East Syndicate',
    status: 'Absconding',
    associatedVehicleId: 'KA05MJ4421',
    phoneNo: '+91 9845012345',
    aadhaarNo: '4839 2038 9012',
    bio: 'Primary coordinator for illegal supply lines across southern districts. Known to employ heavy modifiers on vehicles to avoid local detection. Flagged in multiple extortion and motor vehicle theft cases.',
    photoPlaceholder: 'bg-red-50 text-red-700 border-red-200'
  },
  {
    id: 'susp-02',
    name: 'Kiran "Kulla" Kumar',
    aliases: ['Kulla', 'Shorty'],
    age: 28,
    biometricId: 'BIO-1920-KA',
    riskLevel: 'High',
    gangAffiliation: 'Central-East Syndicate',
    status: 'Detained',
    associatedVehicleId: 'KA05MJ4421',
    phoneNo: '+91 9900223344',
    aadhaarNo: '9920 1823 8840',
    bio: 'Associate of Vikram Hegde. Specialized driver and logician for heavy transports. Detained during recent checkpoint sweep at Silk Board Junction.',
    photoPlaceholder: 'bg-orange-50 text-orange-700 border-orange-200'
  },
  {
    id: 'susp-03',
    name: 'Suresh Gowda',
    aliases: ['Yajamana', 'Gowdru'],
    age: 51,
    biometricId: 'BIO-0092-KA',
    riskLevel: 'High',
    gangAffiliation: 'Gowda Network',
    status: 'Under Surveillance',
    phoneNo: '+91 9448011223',
    aadhaarNo: '1092 3840 9182',
    bio: 'Local financier of smuggling rackets. Investigated for money laundering under cover of real estate operations in Bengaluru East. Direct phone ties to Vikram Hegde.',
    photoPlaceholder: 'bg-amber-50 text-amber-700 border-amber-200'
  },
  {
    id: 'susp-04',
    name: 'Ramesh Adiga',
    aliases: ['Punda', 'Vidyaranyapura Ramesh'],
    age: 34,
    biometricId: 'BIO-4439-KA',
    riskLevel: 'Medium',
    gangAffiliation: 'Independent',
    status: 'In Custody',
    phoneNo: '+91 9880192837',
    aadhaarNo: '7238 9918 2039',
    bio: 'Sub-broker for hijacked automobile parts. Arrested during a raid in Majestic scrap market. Frequently purchased from the Central-East Syndicate.',
    photoPlaceholder: 'bg-emerald-50 text-emerald-700 border-emerald-200'
  }
];

export const VEHICLES: Vehicle[] = [
  {
    id: 'KA05MJ4421',
    model: 'Scorpio S11',
    make: 'Mahindra',
    color: 'White',
    ownerName: 'Vikram Hegde',
    ownerAadhaar: '4839 2038 9012',
    status: 'Flagged',
    anprLogs: [
      { timestamp: '2026-07-06T19:40:00Z', cctvId: 'cam-01', locationName: 'Koramangala 80ft Road Junction', latitude: 12.9345, longitude: 77.6268, confidence: 98.4 },
      { timestamp: '2026-07-06T18:15:00Z', cctvId: 'cam-02', locationName: 'Silk Board flyover entrance', latitude: 12.9176, longitude: 77.6244, confidence: 97.2 },
      { timestamp: '2026-07-05T10:30:00Z', cctvId: 'cam-03', locationName: 'Hosur Road Toll Plaza', latitude: 12.8499, longitude: 77.6749, confidence: 99.1 },
      { timestamp: '2026-07-04T22:05:00Z', cctvId: 'cam-05', locationName: 'Jayanagar 4th Block Circle', latitude: 12.9308, longitude: 77.5802, confidence: 94.8 }
    ]
  },
  {
    id: 'KA51MD9876',
    model: 'Bolero',
    make: 'Mahindra',
    color: 'Silver',
    ownerName: 'Suresh Gowda',
    ownerAadhaar: '1092 3840 9182',
    status: 'Under Investigation',
    anprLogs: [
      { timestamp: '2026-07-06T17:30:00Z', cctvId: 'cam-04', locationName: 'Indiranagar 100ft Road', latitude: 12.9719, longitude: 77.6412, confidence: 99.5 },
      { timestamp: '2026-07-05T14:22:00Z', cctvId: 'cam-02', locationName: 'Silk Board flyover entrance', latitude: 12.9176, longitude: 77.6244, confidence: 96.0 }
    ]
  },
  {
    id: 'KA03MH1122',
    model: 'Swift Dzire',
    make: 'Maruti Suzuki',
    color: 'White',
    ownerName: 'Sunil Rao (Taxi Operator)',
    ownerAadhaar: '2345 6789 0123',
    status: 'Clean',
    anprLogs: [
      { timestamp: '2026-07-06T19:55:00Z', cctvId: 'cam-01', locationName: 'Koramangala 80ft Road Junction', latitude: 12.9345, longitude: 77.6268, confidence: 99.8 }
    ]
  }
];

export const WITNESSES: Witness[] = [
  { id: 'wit-01', name: 'Naveen Swamy', statement: 'Saw the white Scorpio parking near the jewelry vault at 18:00. Two men wearing KSP-like jackets stepped out. One had a visible scar on his left hand.', credibility: 'High', contact: '+91 9008012345' },
  { id: 'wit-02', name: 'Sheela Raju', statement: 'Heard a loud argument near the container dock at 22:30. A white SUV sped away towards the Hosur main road shortly after.', credibility: 'Medium', contact: '+91 8899220033' },
];

export const EVIDENCE: Evidence[] = [
  { id: 'evid-01', type: 'Digital', description: 'CCTV footage segment capturing Vikram Hegde driving the Mahindra Scorpio (KA05MJ4421) near the crime scene.', source: 'Koramangala 80ft Road Cam-01', dateSecured: '2026-07-06', status: 'Secured', storageLocation: 'Koramangala PS Server / digital-vault' },
  { id: 'evid-02', type: 'Physical', description: 'Pry bar and lockpicker kit recovered from vehicle trunk during the checkpoint seizure.', source: 'KA05MJ4421 Seizure Report', dateSecured: '2026-07-06', status: 'In Lab', storageLocation: 'FSL Bengaluru - Ballistics & Toolmarks' },
  { id: 'evid-03', type: 'Circumstantial', description: 'Cell tower handshake matching Vikram Hegde\'s mobile number at the exact minute of the Koramangala retail vault breach.', source: 'Telecom Provider CDR Log', dateSecured: '2026-07-05', status: 'Presented in Court', storageLocation: 'Case Diary Exhibit A-4' }
];

export const FIRs: FIR[] = [
  {
    id: 'FIR 0142/2026',
    stationId: 'ps-km',
    category: 'Armed Robbery & Conspiracy',
    ipcSections: ['IPC 379 (Theft)', 'IPC 392 (Robbery)', 'IPC 120B (Criminal Conspiracy)'],
    incidentDate: '2026-07-06T18:00:00Z',
    registrationDate: '2026-07-06T20:10:00Z',
    severity: 'Critical',
    status: 'Active',
    summary: 'Complainant reports that a white Mahindra Scorpio (KA05MJ4421) blocked their supply truck, and two armed assailants hijacked the jewelry consignment. Value estimated at ₹1.2 Crores.',
    suspectIds: ['susp-01', 'susp-02'],
    vehicleIds: ['KA05MJ4421'],
    evidenceIds: ['evid-01', 'evid-02'],
    witnessIds: ['wit-01'],
    reporterName: 'Divya Jewellers Representative',
    locationName: 'Koramangala 80ft Road, near regional hub',
    latitude: 12.9340,
    longitude: 77.6262
  },
  {
    id: 'FIR 0138/2026',
    stationId: 'ps-jn',
    category: 'Organized Vehicle Theft',
    ipcSections: ['IPC 379 (Theft)', 'IPC 411 (Dishonestly receiving stolen property)'],
    incidentDate: '2026-07-04T21:30:00Z',
    registrationDate: '2026-07-05T09:00:00Z',
    severity: 'Major',
    status: 'Under Review',
    summary: 'Series of commercial SUV thefts registered. ANPR tracker tracked KA05MJ4421 in proximity of multiple thefts in Jayanagar area.',
    suspectIds: ['susp-01', 'susp-04'],
    vehicleIds: ['KA05MJ4421'],
    evidenceIds: ['evid-03'],
    witnessIds: ['wit-02'],
    reporterName: 'Owner of stolen Innova',
    locationName: 'Jayanagar 4th Block Parking Circle',
    latitude: 12.9308,
    longitude: 77.5802
  },
  {
    id: 'FIR 0121/2026',
    stationId: 'ps-in',
    category: 'Extortion & Smuggling',
    ipcSections: ['IPC 384 (Extortion)', 'IPC 506 (Criminal Intimidation)'],
    incidentDate: '2026-06-25T11:00:00Z',
    registrationDate: '2026-06-26T14:00:00Z',
    severity: 'Major',
    status: 'Active',
    summary: 'Extortion threat delivered to business owners in Indiranagar. Call details map calls back to cell towers controlled by Suresh Gowda and Vikram Hegde syndicate.',
    suspectIds: ['susp-01', 'susp-03'],
    vehicleIds: ['KA51MD9876'],
    evidenceIds: [],
    witnessIds: [],
    reporterName: 'Indiranagar Traders Association',
    locationName: 'Indiranagar 100ft Road',
    latitude: 12.9719,
    longitude: 77.6412
  }
];

export const CALL_LOGS: CallLog[] = [
  { id: 'call-01', fromNo: '+91 9845012345', fromName: 'Vikram Hegde', toNo: '+91 9448011223', toName: 'Suresh Gowda', timestamp: '2026-07-06T17:10:00Z', durationSeconds: 240, cellTowerId: 'TWR-KMR-01' },
  { id: 'call-02', fromNo: '+91 9845012345', fromName: 'Vikram Hegde', toNo: '+91 9900223344', toName: 'Kiran Kumar', timestamp: '2026-07-06T17:45:00Z', durationSeconds: 98, cellTowerId: 'TWR-KMR-02' },
  { id: 'call-03', fromNo: '+91 9900223344', fromName: 'Kiran Kumar', toNo: '+91 9880192837', toName: 'Ramesh Adiga', timestamp: '2026-07-05T12:00:00Z', durationSeconds: 312, cellTowerId: 'TWR-MJ-04' },
  { id: 'call-04', fromNo: '+91 9448011223', fromName: 'Suresh Gowda', toNo: '+91 9880192837', toName: 'Ramesh Adiga', timestamp: '2026-07-04T18:30:00Z', durationSeconds: 45, cellTowerId: 'TWR-WF-09' }
];

export const CCTV_RECORDS: CCTVRecord[] = [
  { id: 'cam-01', locationName: 'Koramangala 80ft Road Junction', latitude: 12.9345, longitude: 77.6268, status: 'Operational' },
  { id: 'cam-02', locationName: 'Silk Board Flyover Entrance', latitude: 12.9176, longitude: 77.6244, status: 'Operational' },
  { id: 'cam-03', locationName: 'Hosur Road Toll Plaza', latitude: 12.8499, longitude: 77.6749, status: 'Operational' },
  { id: 'cam-04', locationName: 'Indiranagar 100ft Road', latitude: 12.9719, longitude: 77.6412, status: 'Operational' },
  { id: 'cam-05', locationName: 'Jayanagar 4th Block Circle', latitude: 12.9308, longitude: 77.5802, status: 'Operational' },
];

// -----------------------------------------
// QUERY INTELLIGENCE SYSTEM (AI COMPONENT)
// -----------------------------------------

export interface IntelligenceReport {
  query: string;
  executiveSummary: string;
  relatedFirs: FIR[];
  associatedSuspects: Suspect[];
  relatedVehicles: Vehicle[];
  crimeLocations: {
    name: string;
    latitude: number;
    longitude: number;
    description: string;
  }[];
  timeline: {
    time: string;
    event: string;
    description: string;
    severity: 'Critical' | 'Major' | 'Moderate' | 'Minor';
  }[];
  networkGraph: {
    nodes: { id: string; label: string; type: 'suspect' | 'vehicle' | 'location' | 'officer'; group: string; status?: string }[];
    edges: { source: string; target: string; label: string; relationType: string }[];
  };
  evidence: Evidence[];
  riskScore: number; // Out of 100
  recommendedActions: string[];
}

export function queryIntelligence(queryText: string): IntelligenceReport {
  const normQuery = queryText.toLowerCase();

  // Primary Check for Vehicle KA05MJ4421 or Vikram Hegde
  const matchesKA05MJ4421 = normQuery.includes('ka05mj4421') || normQuery.includes('4421') || normQuery.includes('vikram') || normQuery.includes('hegde');

  if (matchesKA05MJ4421) {
    return {
      query: queryText,
      executiveSummary: `AI-Synthesized Brief: Target vehicle KA05MJ4421 (White Mahindra Scorpio S11) is linked directly to a critical highway hijack and armed robbery (FIR 0142/2026) registered in Koramangala PS. Cellular triangulation and ANPR logging establish that the vehicle was driven by absconding suspect Vikram Hegde, who is highly connected to the Central-East Syndicate. A network analysis shows close phone communication links with financier Suresh Gowda and scrap broker Ramesh Adiga. The vehicle has been flagged by ANPR systems and is currently designated as absconding.`,
      relatedFirs: FIRs.filter(f => f.vehicleIds.includes('KA05MJ4421')),
      associatedSuspects: SUSPECTS.filter(s => s.associatedVehicleId === 'KA05MJ4421' || s.id === 'susp-03'),
      relatedVehicles: VEHICLES.filter(v => v.id === 'KA05MJ4421' || v.id === 'KA51MD9876'),
      crimeLocations: [
        { name: 'Koramangala 80ft Road, Bengaluru', latitude: 12.9345, longitude: 77.6268, description: 'Armed Robbery Location (FIR 0142/2026)' },
        { name: 'Jayanagar 4th Block Parking, Bengaluru', latitude: 12.9308, longitude: 77.5802, description: 'Secondary tracking location for SUV theft (FIR 0138/2026)' },
        { name: 'Silk Board Junction flyover, Bengaluru', latitude: 12.9176, longitude: 77.6244, description: 'Last known ANPR signature capture of target Scorpio' }
      ],
      timeline: [
        { time: '2026-07-06 20:10', event: 'FIR Registration', description: 'FIR 0142/2026 filed at Koramangala PS for Armed Robbery of consignment.', severity: 'Critical' },
        { time: '2026-07-06 19:40', event: 'ANPR Alert - Koramangala', description: 'KA05MJ4421 scanned traveling at 80km/h on Koramangala 80ft Road post-hijack.', severity: 'Major' },
        { time: '2026-07-06 18:15', event: 'ANPR Scan - Silk Board', description: 'Vehicle detected approaching Koramangala area from Silk Board Flyover.', severity: 'Moderate' },
        { time: '2026-07-06 17:45', event: 'Intercepted Call', description: 'Vikram Hegde dialed Kiran Kumar (Driver) duration 98s near Silk Board cell sector.', severity: 'Major' },
        { time: '2026-07-06 17:10', event: 'Coordinative Call', description: 'Vikram Hegde dialed Suresh Gowda (Financier) duration 240s planning consignment drop.', severity: 'Critical' },
        { time: '2026-07-05 10:30', event: 'ANPR Toll Log - Hosur', description: 'Scorpio entered Bengaluru limits through Hosur Road Toll Plaza.', severity: 'Minor' }
      ],
      networkGraph: {
        nodes: [
          { id: 'susp-01', label: 'Vikram Hegde', type: 'suspect', group: 'Syndicate Leader', status: 'Absconding' },
          { id: 'susp-02', label: 'Kiran Kumar', type: 'suspect', group: 'Driver / Transport', status: 'Detained' },
          { id: 'susp-03', label: 'Suresh Gowda', type: 'suspect', group: 'Financier', status: 'Under Watch' },
          { id: 'susp-04', label: 'Ramesh Adiga', type: 'suspect', group: 'Scrap Buyer', status: 'In Custody' },
          { id: 'veh-ka4421', label: 'KA05MJ4421 (Scorpio)', type: 'vehicle', group: 'Active Assets' },
          { id: 'veh-ka9876', label: 'KA51MD9876 (Bolero)', type: 'vehicle', group: 'Suspect Vehicles' },
          { id: 'loc-km', label: 'Koramangala PS', type: 'location', group: 'Jurisdiction' }
        ],
        edges: [
          { source: 'susp-01', target: 'veh-ka4421', label: 'Registered Owner / Driver', relationType: 'ownership' },
          { source: 'susp-02', target: 'veh-ka4421', label: 'Apprehended Driving', relationType: 'driver' },
          { source: 'susp-01', target: 'susp-03', label: 'Call Log (240s) / Financed By', relationType: 'finance' },
          { source: 'susp-01', target: 'susp-02', label: 'Call Log (98s) / Co-Accused', relationType: 'phone' },
          { source: 'susp-02', target: 'susp-04', label: 'Call Log (312s) / Fenced Parts', relationType: 'fence' },
          { source: 'susp-03', target: 'veh-ka9876', label: 'Registered Owner', relationType: 'ownership' },
          { source: 'veh-ka4421', target: 'loc-km', label: 'Last Logged CCTV Zone', relationType: 'location' }
        ]
      },
      evidence: EVIDENCE.filter(e => e.id === 'evid-01' || e.id === 'evid-02' || e.id === 'evid-03'),
      riskScore: 88,
      recommendedActions: [
        'Issue All-Stations Lookup Circular (LOC) for Vikram Hegde.',
        'Deploy intercept patrols at Koramangala / HSR Ring Road exits.',
        'Send formal requisition to Telecom Service Providers for real-time ping data of mobile +91 9845012345.',
        'Deploy forensics team to examine the lockpicker gear recovered from vehicle KA05MJ4421.',
        'Apply for formal police remand for driver Kiran Kumar to elicit drop coordinates.'
      ]
    };
  }

  // Fallback for general queries or empty
  return {
    query: queryText,
    executiveSummary: `AI-Synthesized Brief: Initial database lookup for "${queryText}" yielded sparse hits. Please verify the query format. Typical query axes include License Plates (e.g. KA05MJ4421), Suspect names (e.g. Vikram Hegde), or Specific Crime Zones. Showing global database status: 3 active cases, 4 suspects, and 3 monitored transport vehicles.`,
    relatedFirs: FIRs.slice(0, 1),
    associatedSuspects: SUSPECTS.slice(0, 2),
    relatedVehicles: VEHICLES.slice(0, 2),
    crimeLocations: [
      { name: 'Koramangala, Bengaluru', latitude: 12.9345, longitude: 77.6268, description: 'Koramangala Station Core Jurisdiction' }
    ],
    timeline: [
      { time: '2026-07-06 20:18', event: 'System Check', description: 'No direct vehicle alerts triggered for this query. Global database listening.', severity: 'Minor' }
    ],
    networkGraph: {
      nodes: [
        { id: 'node-sys', label: 'KSP Core DB', type: 'location', group: 'System' }
      ],
      edges: []
    },
    evidence: [],
    riskScore: 10,
    recommendedActions: [
      'Enter specific parameters like "KA05MJ4421" or "Vikram Hegde" to retrieve detailed intelligence dossiers.',
      'Check system logs for ANPR plate read mismatches.'
    ]
  };
}
