import React, { useState } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background
} from '@xyflow/react';
import type { Node, Edge } from '@xyflow/react';
import { useApp } from '../../context/AppContext';
import { SUSPECTS, VEHICLES } from '../../services/mockDb';
import {
  Network,
  ShieldAlert,
  Zap,
  Users,
  Info,
  Search,
  X,
  Compass,
  Link,
  ChevronRight,
  Phone,
  CreditCard,
  UserCheck,
  Car
} from 'lucide-react';

export const CriminalNetwork: React.FC = () => {
  const { setSelectedSuspect, setSelectedVehicle, setAiQuery, language, addToast } = useApp();
  const [searchTerm, setSearchTerm] = useState('');

  // Interactive pathfinder state
  const [startNodeId, setStartNodeId] = useState<string>('');
  const [endNodeId, setEndNodeId] = useState<string>('');
  const [shortestPath, setShortestPath] = useState<{ nodes: string[], edges: string[] } | null>(null);

  // Selected node detailed profile panel
  const [selectedNodeDetails, setSelectedNodeDetails] = useState<{
    type: 'suspect' | 'vehicle';
    id: string;
    name: string;
    status: string;
    gangAffiliation?: string;
    aliases?: string[];
    phoneNo?: string;
    aadhaarNo?: string;
    bio?: string;
    model?: string;
    make?: string;
    color?: string;
    ownerName?: string;
    ownerAadhaar?: string;
  } | null>(null);

  // Define nodes representing the syndicate components
  const initialNodes: Node[] = [
    {
      id: 'susp-01',
      position: { x: 250, y: 120 },
      data: { label: 'Vikram Hegde\n(Syndicate Leader)' },
      style: {
        background: '#fee2e2',
        border: '2px solid #ef4444',
        color: '#991b1b',
        borderRadius: '8px',
        fontSize: '11px',
        fontWeight: 'bold',
        padding: '10px',
        whiteSpace: 'pre-line',
        textAlign: 'center',
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        transition: 'all 0.3s ease'
      }
    },
    {
      id: 'susp-03',
      position: { x: 550, y: 120 },
      data: { label: 'Suresh Gowda\n(Financier)' },
      style: {
        background: '#fef3c7',
        border: '2px solid #f59e0b',
        color: '#92400e',
        borderRadius: '8px',
        fontSize: '11px',
        fontWeight: 'bold',
        padding: '10px',
        whiteSpace: 'pre-line',
        textAlign: 'center',
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        transition: 'all 0.3s ease'
      }
    },
    {
      id: 'susp-02',
      position: { x: 100, y: 300 },
      data: { label: 'Kiran Kumar\n(Transport Driver)' },
      style: {
        background: '#ffedd5',
        border: '2px solid #f97316',
        color: '#9a3412',
        borderRadius: '8px',
        fontSize: '11px',
        fontWeight: 'bold',
        padding: '10px',
        whiteSpace: 'pre-line',
        textAlign: 'center',
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        transition: 'all 0.3s ease'
      }
    },
    {
      id: 'susp-04',
      position: { x: 100, y: 480 },
      data: { label: 'Ramesh Adiga\n(Majestic Scrap Dealer)' },
      style: {
        background: '#ecfdf5',
        border: '2px solid #10b981',
        color: '#065f46',
        borderRadius: '8px',
        fontSize: '11px',
        fontWeight: 'bold',
        padding: '10px',
        whiteSpace: 'pre-line',
        textAlign: 'center',
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        transition: 'all 0.3s ease'
      }
    },
    {
      id: 'veh-ka4421',
      data: { label: 'Scorpio S11\n[KA05MJ4421]' },
      position: { x: 300, y: 300 },
      style: {
        background: '#f8fafc',
        border: '2px solid #0f1e36',
        color: '#0f1e36',
        borderRadius: '8px',
        fontSize: '11px',
        fontWeight: 'bold',
        padding: '10px',
        whiteSpace: 'pre-line',
        textAlign: 'center',
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        transition: 'all 0.3s ease'
      }
    },
    {
      id: 'veh-ka9876',
      data: { label: 'Bolero SUV\n[KA51MD9876]' },
      position: { x: 550, y: 300 },
      style: {
        background: '#f8fafc',
        border: '2px solid #64748b',
        color: '#1e293b',
        borderRadius: '8px',
        fontSize: '11px',
        fontWeight: 'bold',
        padding: '10px',
        whiteSpace: 'pre-line',
        textAlign: 'center',
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        transition: 'all 0.3s ease'
      }
    }
  ];

  // Define linkages and labels between nodes
  const initialEdges: Edge[] = [
    {
      id: 'e1-veh1',
      source: 'susp-01',
      target: 'veh-ka4421',
      label: 'Registered Owner',
      style: { stroke: '#475569', strokeWidth: 2 },
      labelStyle: { fill: '#334155', fontSize: 9, fontWeight: 600 }
    },
    {
      id: 'e2-veh1',
      source: 'susp-02',
      target: 'veh-ka4421',
      label: 'Logistics Driver',
      style: { stroke: '#475569', strokeWidth: 2 },
      labelStyle: { fill: '#334155', fontSize: 9, fontWeight: 600 }
    },
    {
      id: 'e1-e3',
      source: 'susp-01',
      target: 'susp-03',
      label: 'CDR Intercept (240s)',
      animated: true,
      style: { stroke: '#ef4444', strokeWidth: 2.5 },
      labelStyle: { fill: '#b91c1c', fontSize: 9, fontWeight: 700 }
    },
    {
      id: 'e1-e2',
      source: 'susp-01',
      target: 'susp-02',
      label: 'CDR Intercept (98s)',
      style: { stroke: '#ef4444', strokeWidth: 2 },
      labelStyle: { fill: '#b91c1c', fontSize: 9, fontWeight: 600 }
    },
    {
      id: 'e2-e4',
      source: 'susp-02',
      target: 'susp-04',
      label: 'Fenced Scrap (312s)',
      style: { stroke: '#10b981', strokeWidth: 2 },
      labelStyle: { fill: '#047857', fontSize: 9, fontWeight: 600 }
    },
    {
      id: 'e3-veh2',
      source: 'susp-03',
      target: 'veh-ka9876',
      label: 'Registered Owner',
      style: { stroke: '#475569', strokeWidth: 2 },
      labelStyle: { fill: '#334155', fontSize: 9, fontWeight: 600 }
    },
    {
      id: 'e3-e4',
      source: 'susp-03',
      target: 'susp-04',
      label: 'Financial Linkage',
      style: { stroke: '#eab308', strokeWidth: 2 },
      labelStyle: { fill: '#a16207', fontSize: 9, fontWeight: 600 }
    }
  ];

  // Map nodes with highlight logic
  const nodes = initialNodes.map((node) => {
    const hasSearch = searchTerm.trim().length > 0;
    const nodeLabel = typeof node.data?.label === 'string' ? node.data.label : '';
    const isMatch = hasSearch && nodeLabel.toLowerCase().includes(searchTerm.toLowerCase());
    const isPathNode = shortestPath && shortestPath.nodes.includes(node.id);
    const isSelected = selectedNodeDetails && selectedNodeDetails.id === node.id;

    const baseStyle = { ...node.style };

    if (isSelected) {
      return {
        ...node,
        style: {
          ...baseStyle,
          border: '3px solid #1e3a8a',
          boxShadow: '0 0 20px rgba(30, 58, 138, 0.8)',
          transform: 'scale(1.1)',
          zIndex: 20
        }
      };
    }

    if (isPathNode) {
      return {
        ...node,
        style: {
          ...baseStyle,
          border: '3px solid #f97316',
          boxShadow: '0 0 18px rgba(249, 115, 22, 0.9)',
          transform: 'scale(1.08)',
          zIndex: 10
        }
      };
    }

    if (hasSearch) {
      if (isMatch) {
        return {
          ...node,
          style: {
            ...baseStyle,
            border: '3px solid #b89020',
            boxShadow: '0 0 16px rgba(184, 144, 32, 0.8)',
            transform: 'scale(1.05)'
          }
        };
      } else {
        return {
          ...node,
          style: {
            ...baseStyle,
            opacity: 0.25,
            filter: 'grayscale(50%)'
          }
        };
      }
    }
    return node;
  });

  // Map edges with highlights
  const edges = initialEdges.map((edge) => {
    const isPathEdge = shortestPath && shortestPath.edges.includes(edge.id);
    if (isPathEdge) {
      return {
        ...edge,
        animated: true,
        style: { stroke: '#f97316', strokeWidth: 4 }
      };
    }
    return edge;
  });

  // BFS Shortest Path algorithm helper
  const findShortestPath = (startId: string, endId: string) => {
    if (startId === endId) return { nodes: [startId], edges: [] };

    const adj: Record<string, { target: string, edgeId: string }[]> = {};
    initialEdges.forEach(e => {
      const u = e.source;
      const v = e.target;
      if (!adj[u]) adj[u] = [];
      if (!adj[v]) adj[v] = [];
      adj[u].push({ target: v, edgeId: e.id });
      adj[v].push({ target: u, edgeId: e.id });
    });

    const queue: string[] = [startId];
    const visited = new Set<string>([startId]);
    const parent: Record<string, { parentId: string, edgeId: string }> = {};

    while (queue.length > 0) {
      const curr = queue.shift()!;
      if (curr === endId) {
        const pathNodes: string[] = [];
        const pathEdges: string[] = [];
        let temp = endId;
        while (temp !== startId) {
          pathNodes.push(temp);
          const pInfo = parent[temp];
          pathEdges.push(pInfo.edgeId);
          temp = pInfo.parentId;
        }
        pathNodes.push(startId);
        return { nodes: pathNodes.reverse(), edges: pathEdges };
      }

      const neighbors = adj[curr] || [];
      for (const n of neighbors) {
        if (!visited.has(n.target)) {
          visited.add(n.target);
          parent[n.target] = { parentId: curr, edgeId: n.edgeId };
          queue.push(n.target);
        }
      }
    }
    return null;
  };

  const handleCalculatePath = () => {
    if (!startNodeId || !endNodeId) {
      addToast('Please select two nodes to find connection.', 'warn');
      return;
    }
    const path = findShortestPath(startNodeId, endNodeId);
    if (path) {
      setShortestPath(path);
      addToast('Connecting path highlighted on syndicate map.', 'success');
    } else {
      setShortestPath(null);
      addToast('No direct connections found between these nodes.', 'error');
    }
  };

  const handleClearPath = () => {
    setStartNodeId('');
    setEndNodeId('');
    setShortestPath(null);
    addToast('Highlights cleared.', 'info');
  };

  // Capture node click to pop details drawers and sync context parameters
  const handleNodeClick = (_event: React.MouseEvent, node: Node) => {
    if (node.id.startsWith('susp-')) {
      const suspect = SUSPECTS.find((s) => s.id === node.id);
      if (suspect) {
        setSelectedSuspect(suspect);
        setAiQuery(`Find cases linked with suspect ${suspect.name}`);
        setSelectedNodeDetails({
          type: 'suspect',
          id: node.id,
          name: suspect.name,
          status: suspect.status,
          gangAffiliation: suspect.gangAffiliation,
          aliases: suspect.aliases,
          phoneNo: suspect.phoneNo,
          aadhaarNo: suspect.aadhaarNo,
          bio: suspect.bio
        });
        addToast(`Dossier loaded for suspect: ${suspect.name}`, 'success');
      }
    } else if (node.id.startsWith('veh-')) {
      const plate = node.id === 'veh-ka4421' ? 'KA05MJ4421' : 'KA51MD9876';
      const vehicle = VEHICLES.find((v) => v.id === plate);
      if (vehicle) {
        setSelectedVehicle(vehicle);
        setAiQuery(`Find all suspects connected with vehicle ${vehicle.id}`);
        setSelectedNodeDetails({
          type: 'vehicle',
          id: node.id,
          name: vehicle.id,
          status: vehicle.status,
          model: vehicle.model,
          make: vehicle.make,
          color: vehicle.color,
          ownerName: vehicle.ownerName,
          ownerAadhaar: vehicle.ownerAadhaar
        });
        addToast(`Vehicle watchlist record loaded: ${vehicle.id}`, 'success');
      }
    }
  };

  const mapStyle = {
    background: '#cbd5e1',
    borderRadius: '6px'
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col md:flex-row overflow-hidden select-none">
      {/* Network Workspace Canvas */}
      <div className="flex-1 h-full relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodeClick={handleNodeClick}
          fitView
          className="bg-slate-50"
        >
          <Controls />
          <MiniMap style={mapStyle} zoomable pannable />
          <Background color="#cbd5e1" gap={16} size={1} />
        </ReactFlow>

        {/* Floating Indicator banner */}
        <div className="absolute top-4 left-4 bg-white border border-slate-200 shadow-lg rounded-md px-3 py-2 z-10 flex items-center gap-2 text-xs font-semibold text-slate-800">
          <Info className="w-4 h-4 text-brand-secondary" />
          <span>Click any node element to expand official records</span>
        </div>
      </div>

      {/* Network analytics Sidebar */}
      <div className="w-full md:w-85 bg-white border-l border-slate-200 flex flex-col p-5 select-none shrink-0 overflow-y-auto">
        <div className="flex flex-col gap-6 flex-1">
          <div>
            <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
              <Network className="w-5 h-5 text-brand-primary" />
              <h2 className="text-xs font-bold text-brand-primary uppercase tracking-wider">
                {language === 'en' ? 'Syndicate Connection Map' : 'ಅಪರಾಧ ಜಾಲ ವಿಶ್ಲೇಷಣೆ'}
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Visualizes real-time cell tower links and vehicle associations between high-priority suspects.
            </p>
          </div>

          {/* ── INTERACTIVE NODE PROFILE DETAILED DRAWER ────────────────── */}
          {selectedNodeDetails && (
            <div className="border border-slate-200 rounded-lg p-4 bg-slate-50 relative animate-in slide-in-from-right duration-250">
              <button
                onClick={() => setSelectedNodeDetails(null)}
                className="absolute top-2.5 right-2.5 p-1 hover:bg-slate-200 rounded text-slate-400 hover:text-slate-650 transition-all cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2 mb-3">
                {selectedNodeDetails.type === 'suspect' ? (
                  <UserCheck className="w-4.5 h-4.5 text-red-600" />
                ) : (
                  <Car className="w-4.5 h-4.5 text-blue-800" />
                )}
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
                  {selectedNodeDetails.type === 'suspect' ? 'SUSPECT DOSSIER' : 'VEHICLE DOSSIER'}
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-800 leading-tight">{selectedNodeDetails.name}</h3>
              <div className="flex gap-1.5 items-center mt-1 flex-wrap">
                <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${
                  selectedNodeDetails.status === 'Absconding' || selectedNodeDetails.status === 'Flagged'
                    ? 'bg-red-50 text-red-700 border border-red-200'
                    : 'bg-slate-100 text-slate-700'
                }`}>
                  {selectedNodeDetails.status}
                </span>
                {selectedNodeDetails.gangAffiliation && (
                  <span className="text-[9px] font-mono font-bold bg-amber-50 text-amber-700 border border-amber-200 px-1.5 py-0.5 rounded">
                    {selectedNodeDetails.gangAffiliation}
                  </span>
                )}
              </div>

              <div className="mt-3 flex flex-col gap-2 text-xs">
                {selectedNodeDetails.aliases && selectedNodeDetails.aliases.length > 0 && (
                  <div>
                    <span className="text-[10px] text-slate-400 font-mono block">ALIASES</span>
                    <span className="font-semibold text-slate-700">{selectedNodeDetails.aliases.join(', ')}</span>
                  </div>
                )}
                {selectedNodeDetails.phoneNo && (
                  <div className="flex items-center gap-1.5 text-slate-650">
                    <Phone className="w-3.5 h-3.5 text-slate-400" />
                    <span className="font-mono text-[11px]">{selectedNodeDetails.phoneNo}</span>
                  </div>
                )}
                {selectedNodeDetails.aadhaarNo && (
                  <div className="flex items-center gap-1.5 text-slate-650">
                    <CreditCard className="w-3.5 h-3.5 text-slate-400" />
                    <span className="font-mono text-[11px]">{selectedNodeDetails.aadhaarNo}</span>
                  </div>
                )}
                {selectedNodeDetails.bio && (
                  <p className="text-[11px] text-slate-500 italic mt-1 leading-normal">
                    "{selectedNodeDetails.bio}"
                  </p>
                )}

                {/* Vehicle specifications */}
                {selectedNodeDetails.model && (
                  <div>
                    <span className="text-[10px] text-slate-400 font-mono block">VEHICLE DETAILS</span>
                    <span className="font-semibold text-slate-700">
                      {[selectedNodeDetails.color, selectedNodeDetails.make, selectedNodeDetails.model].filter(Boolean).join(' ')}
                    </span>
                  </div>
                )}
                {selectedNodeDetails.ownerName && (
                  <div>
                    <span className="text-[10px] text-slate-400 font-mono block">REGISTERED OWNER</span>
                    <span className="font-semibold text-slate-750 block">{selectedNodeDetails.ownerName}</span>
                    {selectedNodeDetails.ownerAadhaar && <span className="text-[10px] text-slate-400 font-mono">{selectedNodeDetails.ownerAadhaar}</span>}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Search/filter bar */}
          <div className="flex flex-col gap-1.5">
            <label className="text-[9px] text-slate-400 font-mono tracking-wider uppercase font-semibold">
              Filter Network Nodes
            </label>
            <div className="flex items-center border border-slate-200 focus-within:border-brand-secondary rounded bg-slate-50 px-2.5 py-1.5 transition-colors">
              <Search className="w-4 h-4 text-slate-400 mr-2 shrink-0" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Type name or plate..."
                className="bg-transparent border-none text-xs w-full focus:outline-none placeholder-slate-400 font-sans"
              />
            </div>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="text-[9px] text-slate-450 hover:text-slate-700 text-left font-mono underline cursor-pointer"
              >
                Clear Search Highlights
              </button>
            )}
          </div>

          {/* ── INTERACTIVE SHORTEST PATH FINDER ───────────────────────── */}
          <div className="border border-slate-250 rounded-lg p-4 bg-slate-50 flex flex-col gap-3">
            <div className="flex items-center gap-1.5 border-b border-slate-200 pb-1.5">
              <Compass className="w-4 h-4 text-brand-primary" />
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-650">
                Shortest Connection Path
              </span>
            </div>
            <div className="flex flex-col gap-2 text-xs">
              <div className="flex flex-col gap-1">
                <span className="text-[9px] font-mono text-slate-400 uppercase">Node A (Start)</span>
                <select
                  value={startNodeId}
                  onChange={(e) => setStartNodeId(e.target.value)}
                  className="p-1.5 bg-white border border-slate-200 rounded font-sans text-xs focus:outline-none"
                >
                  <option value="">Select node...</option>
                  {initialNodes.map(n => (
                    <option key={n.id} value={n.id}>{n.data?.label.toString().split('\n')[0]}</option>
                  ))}
                </select>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-[9px] font-mono text-slate-400 uppercase">Node B (End)</span>
                <select
                  value={endNodeId}
                  onChange={(e) => setEndNodeId(e.target.value)}
                  className="p-1.5 bg-white border border-slate-200 rounded font-sans text-xs focus:outline-none"
                >
                  <option value="">Select node...</option>
                  {initialNodes.map(n => (
                    <option key={n.id} value={n.id}>{n.data?.label.toString().split('\n')[0]}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex gap-2 mt-1">
              <button
                onClick={handleCalculatePath}
                className="flex-1 bg-brand-primary hover:bg-brand-primary-light text-white font-bold text-[10px] py-1.5 rounded uppercase cursor-pointer transition-all"
              >
                Highlight Link
              </button>
              {shortestPath && (
                <button
                  onClick={handleClearPath}
                  className="p-1.5 bg-slate-200 hover:bg-slate-300 rounded text-slate-600 cursor-pointer"
                  title="Clear Path highlights"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Path breakdown */}
            {shortestPath && (
              <div className="mt-2 text-[10px] text-slate-650 bg-white border border-slate-200 rounded p-2.5 font-mono flex flex-col gap-1">
                <span className="text-[8px] text-slate-400 uppercase">Path connection:</span>
                <div className="flex flex-wrap items-center gap-1">
                  {shortestPath.nodes.map((nodeId, idx) => {
                    const nodeObj = initialNodes.find(n => n.id === nodeId);
                    const name = nodeObj ? nodeObj.data?.label.toString().split('\n')[0] : nodeId;
                    return (
                      <React.Fragment key={nodeId}>
                        {idx > 0 && <ChevronRight className="w-3 h-3 text-slate-400 shrink-0" />}
                        <span className="font-bold text-slate-700 bg-slate-100 px-1 rounded">{name}</span>
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Legend */}
          <div className="flex flex-col gap-2.5 bg-slate-50 border border-slate-200 rounded-lg p-3">
            <span className="text-[10px] text-slate-450 font-mono tracking-wider block font-semibold uppercase leading-none mb-1">
              Relationship Types
            </span>
            <div className="flex flex-col gap-2 text-[10px] font-semibold text-slate-650">
              <div className="flex items-center gap-2">
                <span className="w-3 h-1 bg-red-500 rounded-full shrink-0" />
                <span>Call CDR (Crimson Edge)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-1 bg-amber-500 rounded-full shrink-0" />
                <span>Financial Transaction Flow</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-1 bg-[#10b981] rounded-full shrink-0" />
                <span>Logistics Intercept (Scrap)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-1 bg-slate-500 rounded-full shrink-0" />
                <span>Registered Asset Ownership</span>
              </div>
            </div>
          </div>

          {/* Network Indicators */}
          <div className="flex flex-col gap-4">
            <h3 className="text-[9px] text-slate-400 font-mono tracking-wider uppercase">Connection Indicators</h3>

            <div className="p-3 bg-red-50 border border-red-200 rounded flex items-center gap-3">
              <ShieldAlert className="w-5 h-5 text-red-700 shrink-0" />
              <div>
                <h4 className="text-xs font-bold text-red-800 leading-tight">Critical Links Intercepted</h4>
                <p className="text-[10px] text-red-600 leading-none mt-1">2 Direct Cell Intercepts</p>
              </div>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded flex items-center gap-3">
              <Zap className="w-5 h-5 text-brand-primary shrink-0" />
              <div>
                <h4 className="text-xs font-bold text-slate-800 leading-tight">ANPR Vehicle Association</h4>
                <p className="text-[10px] text-slate-500 leading-none mt-1">2 Tracked Carrier Assets</p>
              </div>
            </div>

            <div className="p-3 bg-amber-50 border border-amber-200 rounded flex items-center gap-3">
              <Users className="w-5 h-5 text-amber-700 shrink-0" />
              <div>
                <h4 className="text-xs font-bold text-amber-800 leading-tight font-sans">Active Financial Node</h4>
                <p className="text-[10px] text-amber-600 leading-none mt-1">Suresh Gowda (Central-East)</p>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-100 pt-4 text-center mt-6">
          <span className="text-[10px] text-slate-400 font-mono">
            KSP NETWORK GRAPH ENGINE V1.2
          </span>
        </div>
      </div>
    </div>
  );
};
export default CriminalNetwork;
