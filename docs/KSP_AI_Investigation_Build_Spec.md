# KSP Crime Intelligence Platform — AI Investigation Module
## Complete Build Specification

**Project:** Karnataka State Police Datathon 2026 — Problem Statement 1
**Document purpose:** Single reference doc for what to build, how to structure it, and in what order. Hand this directly to Claude Code, teammates, or another AI for review.

---

## 1. Project Goal (Non-Negotiable Framing)

We are **not** building a chatbot and **not** building a CRUD police records system.

We are building an **AI Investigation Assistant** where:
- The officer can type **anything, freely, in natural language** — like a normal chat.
- The AI's response **always comes back as a formal, structured investigation report** — never casual chatbot tone, never emojis, never conversational filler.
- The system visibly performs multi-step reasoning (entity extraction → database search → relationship analysis → summary) so it reads as **agentic**, not as "GPT wearing a police costume."

This single idea — free input, formal structured output — is the spine of the whole module. Every decision below serves it.

---

## 2. Data Layer

### 2.1 Real KSP schema (given, must use as-is)
Core tables already provided by KSP: `CaseMaster` (FIR), `Accused`, `Victim`, `ComplainantDetails`, `ArrestSurrender`, `Act`/`Section`, `CrimeHead`/`CrimeSubHead`, `ChargesheetDetails`, plus org hierarchy (`State`→`District`→`Unit`→`Employee`, `Rank`, `Designation`) and lookups (`CasteMaster`, `ReligionMaster`, `OccupationMaster`, `CaseStatusMaster`, `CaseCategory`, `GravityOffence`).

This schema does **not** include vehicles, CCTV, ANPR, call records (CDR), cell towers, or biometrics.

### 2.2 Extended tables (KSP explicitly permits extension — "you can create more if required, but follow the pattern")

Follow existing naming conventions exactly:
- PK: `{TableName}ID`
- FK: same name as parent PK
- Lookup/master tables end in `Master`
- Boolean flags: `Active BIT`

**New tables to add:**

| Table | Key Columns |
|---|---|
| `Vehicle` | `VehicleID PK`, `RegistrationNumber`, `OwnerAccusedID FK→Accused`, `VehicleTypeID FK`, `Active BIT` |
| `ANPRSighting` | `ANPRSightingID PK`, `VehicleID FK`, `CameraLocationID FK`, `SightingDateTime`, `latitude`, `longitude` |
| `CDRRecord` | `CDRRecordID PK`, `AccusedMasterID FK`, `CellTowerID FK`, `CallDateTime`, `DurationSeconds`, `ConnectedAccusedID FK` (self-ref) |
| `CellTower` | `CellTowerID PK`, `TowerCode`, `latitude`, `longitude`, `DistrictID FK` |
| `BiometricMatch` | `BiometricMatchID PK`, `AccusedMasterID FK`, `LocationID FK`, `MatchDateTime`, `MatchType`, `ConfidenceScore` |
| `FinancialTransaction` | `FinancialTransactionID PK`, `FromAccusedID FK`, `ToAccusedID FK`, `Amount`, `TransactionDate` |
| `AssociationEdge` | `AssociationEdgeID PK`, `SourceEntityType`, `SourceEntityID`, `TargetEntityType`, `TargetEntityID`, `RelationshipTypeID FK→RelationshipTypeMaster`, `Evidence`, `DurationSeconds` (nullable) |

`AssociationEdge` is the key table — it powers the Criminal Network graph generically instead of needing a separate query per relationship type.

### 2.3 Synthetic demo dataset
Build 5–10 fully interconnected investigation stories (matching the existing UI's Vikram Hegde / Suresh Gowda / Kiran Kumar / Ramesh Adiga storyline). Each story should have: FIR, accused, vehicle, ANPR pings, CDR calls, at least one cross-district link. This becomes both your seed data and your demo script.

---

## 3. Investigation Engine — Simplified Pipeline

Do **not** build 10+ separate "engines." Build 4 real stages; fake the rest as simple rule-based scoring inside the same flow.

```
Officer Query (free text)
      ↓
1. Entity Extraction        — pull name / case number / vehicle plate / district if present
      ↓
2. Database Retrieval       — SQL joins across real + extended schema
      ↓
3. Relationship Analysis    — cross-case / cross-district matching via AssociationEdge
      ↓
4. Gemini Formal Report     — structured JSON + free question → Gemini → formal report text
```

**Rule-based (not separate ML systems):**
- Risk/Threat Index = weighted formula (gravity offence + prior case count + arrest history)
- Pattern detection = simple flags (same accused in 2+ districts, repeat crime category)

---

## 4. AI Investigation Module — Two-Layer Design

### Layer 1: Global Search (entry point)
- Free-text search bar + quick-query chips (already built)
- Triggers full pipeline with visible step-by-step "Analysis Audit" animation:
  `Searching FIR Database → Matching Vehicle Registry → Checking Call Records → Finding Associated Suspects → Analyzing Crime Patterns → Building Criminal Network → Generating Investigation Report`
- This animated tracker is the single strongest "agentic AI" visual — always show it on first query, step-by-step, not all at once.

### Layer 2: Contextual Follow-up Chat (scoped to one case/dossier)
- Sticky input bar at the bottom of the dossier result page: *"Ask a follow-up about this investigation..."*
- Follow-ups reuse the same case context (no need to re-run the full audit animation — just a lightweight spinner)
- Gemini receives: case context + full Q&A history for this thread + new question
- New entities mentioned mid-thread trigger a small fresh retrieval; otherwise answer from existing context
- Responses append below input in the same formal report style — not chat bubbles
- Show a running Q&A log on the page so the demo visibly shows conversation depth by the end

### Why two layers, not one flat chat
- Keeps each conversation scoped to one case (mirrors real investigator workflow)
- Avoids mixing unrelated suspects/cases in one thread
- Directly satisfies the brief's "AI should maintain context" and "multi-turn investigation" requirements

---

## 5. System Prompt (Gemini) — copy-paste ready

```
You are an AI assistant for Karnataka Police investigators.

The officer may ask you anything, in casual or natural language, about
cases, suspects, vehicles, districts, or patterns. Regardless of how
casually the question is phrased, you must ALWAYS respond strictly in
formal police investigation report format using the structure below.

RULES:
- Never use casual language, emojis, or conversational filler
  (no "Sure!", "Great question!", "Here's what I found:").
- Base your findings ONLY on the data provided in the context below.
  Do not invent facts, names, dates, or figures not present in the data.
- If the provided data is insufficient to answer, state exactly:
  "Insufficient records found for this query." under FINDINGS, and stop.
- Keep AI ASSESSMENT and RECOMMENDED ACTION to 1–2 sentences each.

RESPONSE FORMAT (always use this structure):

INVESTIGATION QUERY RESPONSE

Query Reference: [restate the officer's question formally]

FINDINGS
[Formal, factual findings based on the retrieved data — bullet points
or short paragraphs]

RELATED RECORDS
[Any linked cases, suspects, vehicles, or districts found]

AI ASSESSMENT
[1–2 sentence formal observation on risk/pattern]

RECOMMENDED ACTION
[1 formal sentence]

---
DATA CONTEXT:
{retrieved_json_here}

---
OFFICER QUERY:
{officer_free_text_query}
```

For follow-up turns, append prior Q&A pairs from the thread above the new officer query, inside the same prompt, so Gemini retains context.

---

## 6. Frontend — What to Build/Improve, In Order

1. **Make result screen dynamic/template-driven** — currently hardcoded to one case (Vikram Hegde). Every card section (Dossier Summary, Related Suspects, Related Vehicles, Evidence Vault, Syndicate Connections, Directives) should conditionally render based on what the query actually returns.
2. **Animate the Analysis Audit step tracker** for every first-query-in-a-case (already exists visually — wire it to real backend timing/state).
3. **Add follow-up chat bar** at the bottom of the dossier page (Section 4, Layer 2).
4. **Add query history sidebar** — list of past queries/cases this session, clickable to reload.
5. **Add standalone "Official Investigation Report" block** — the clean formal-report text output, visually separated from dashboard-style cards, so there's one clear moment to point to during the pitch.
6. **Make Threat Index / Confidence numbers link to the "Explainable AI" section** below them.
7. **Make Recommended Officer Directives checkboxes interactive** (toggle state, maybe a toast confirmation).
8. **Criminal Network:** wire node-click to open a side profile panel; add a shortest-path highlight between two selected nodes.
9. **Cases/FIRs page:** list + status badges + "Related Investigations" section per case.
10. **Reports Builder:** two clearly separate buttons — "Generate Executive Brief" (one page) vs. "Generate Full Dossier" (multi-page).

**Do not touch / already good enough:**
- Dashboard stat cards and map (Image 1, earlier)
- Criminal Network visual design (colors, legend, minimap)
- Analytics charts — no prediction/forecasting additions
- Crime Map — markers + zoom only, no heatmap/prediction layers
- Settings page

---

## 7. What NOT to Build (explicitly cut, do not revisit)

- Voice input (English/Kannada)
- 5-tier RBAC (Constable→IGP) — use 2 roles only: Officer, Supervisor
- Heatmaps, crime prediction layers, movement/route tracking
- Timeline playback scrubber
- Financial/gang relationship graph types beyond what's already in `AssociationEdge`
- Separate "engines" for timeline building, pattern detection, risk scoring, recommendations — these are rules inside the 4-stage pipeline (Section 3), not standalone systems

---

## 8. Priority Order for Remaining Time

1. Resolve schema — build extended tables (Section 2.2) + synthetic dataset (Section 2.3)
2. Build the 4-stage Investigation Engine (Section 3) with the Gemini system prompt (Section 5)
3. Wire frontend result screen to be dynamic (Section 6, item 1)
4. Wire Analysis Audit step tracker to real state (item 2)
5. Add follow-up chat layer (item 3)
6. Add query history sidebar (item 4)
7. Deploy to Zoho Catalyst — do this early, not last night
8. Polish: Executive Brief/Full Dossier split, Criminal Network node click, everything else in Section 6

---

## 9. Demo Script (10–15 min)

1. Officer types a natural free-text query (e.g., "what's going on with Vikram Hegde") in the global search
2. Analysis Audit animates through its steps live
3. Full dossier renders: formal report block, related suspects/vehicles, threat index, evidence vault
4. Officer asks a natural follow-up in the chat bar scoped to this case (e.g., "has he been arrested before")
5. Formal, context-aware answer appears instantly below
6. Jump to Criminal Network — same suspect's graph, click a node to expand, highlight shortest path to a second suspect
7. Click "Generate Official Report" → show Executive Brief → drill into Full Dossier
8. Close with: this is deployed on Zoho Catalyst, schema extends KSP's official ER diagram, AI layer is provider-agnostic (Gemini today, swappable later)

**One sentence to remember while building:** one real, end-to-end flow (free question → agentic pipeline → formal report → contextual follow-up) done well beats twenty features done halfway.
