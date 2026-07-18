import json
from collections.abc import Sequence
from typing import Any

import httpx

from app.investigation.dto import (
    EntityType,
    EvidenceCandidate,
    ExtractedEntity,
    InvestigationQuery,
    Recommendation,
    RecommendationPriority,
    RiskAssessment,
)
from app.utils.exceptions import AppError


class GeminiProviderNotConfiguredError(AppError):
    status_code = 503
    error_code = "AI_PROVIDER_NOT_CONFIGURED"


KSP_INVESTIGATION_SYSTEM_PROMPT = """You are an AI assistant for Karnataka Police investigators.

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
- Keep AI ASSESSMENT and RECOMMENDED ACTION to 1-2 sentences each.

RESPONSE FORMAT (always use this structure):

INVESTIGATION QUERY RESPONSE

Query Reference: [restate the officer's question formally]

FINDINGS
[Formal, factual findings based on the retrieved data - bullet points
or short paragraphs]

RELATED RECORDS
[Any linked cases, suspects, vehicles, or districts found]

AI ASSESSMENT
[1-2 sentence formal observation on risk/pattern]

RECOMMENDED ACTION
[1 formal sentence]

- If confirming that an action has been successfully taken (e.g. following a function call/tool execution), you MUST respond ONLY in the following exact format:
  ACTION TAKEN: [one-line description of what happened], [timestamp].
  Do not include any other sections (no FINDINGS, no AI ASSESSMENT, no RECOMMENDED ACTION).
"""



INVESTIGATION_TOOLS = [
    {
        "functionDeclarations": [
            {
                "name": "notify_station",
                "description": "Notify a specific police station (e.g. Nazarbad PS, Cubbon Park PS) with an alert or tip message regarding a suspect or case.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "station_name": {
                            "type": "STRING",
                            "description": "Name of the police station to notify. Must match unit_name exactly, e.g. 'Nazarbad PS'."
                        },
                        "message": {
                            "type": "STRING",
                            "description": "Detailed investigative message to send."
                        }
                    },
                    "required": ["station_name", "message"]
                }
            },
            {
                "name": "flag_suspect",
                "description": "Flag a suspect (accused) in the database with a specific reason representing threat or sighting update.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "suspect_id": {
                            "type": "INTEGER",
                            "description": "The AccusedMasterID (integer ID) of the suspect."
                        },
                        "reason": {
                            "type": "STRING",
                            "description": "Reason for flagging the suspect."
                        }
                    },
                    "required": ["suspect_id", "reason"]
                }
            },
            {
                "name": "add_case_note",
                "description": "Add an official case note detailing case progress or evidence discovery directives.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "case_id": {
                            "type": "INTEGER",
                            "description": "The CaseMasterID (integer ID) of the case."
                        },
                        "note": {
                            "type": "STRING",
                            "description": "The case note content to add."
                        }
                    },
                    "required": ["case_id", "note"]
                }
            }
        ]
    }
]


class GeminiAIProvider:
    """Gemini adapter boundary using direct asynchronous REST requests."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        self.api_key = api_key
        self.model_name = model_name or "gemini-2.5-flash"

    async def extract_entities(self, query: InvestigationQuery) -> Sequence[ExtractedEntity]:
        if not self.api_key:
            raise GeminiProviderNotConfiguredError("Gemini entity extraction is not configured")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        prompt = (
            f"Analyze the following police investigation query and extract all relevant entities:\n"
            f"Query: \"{query.query_text}\"\n\n"
            f"Classify each entity as one of: person, vehicle, case, location, phone, organization, date, unknown."
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "entities": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "value": {"type": "STRING"},
                                    "entity_type": {
                                        "type": "STRING",
                                        "enum": ["person", "vehicle", "case", "location", "phone", "organization", "date", "unknown"],
                                    },
                                    "confidence": {"type": "NUMBER"},
                                },
                                "required": ["value", "entity_type", "confidence"],
                            },
                        }
                    },
                    "required": ["entities"],
                },
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_content)
                
                entities = []
                for item in parsed.get("entities", []):
                    entities.append(
                        ExtractedEntity(
                            value=item["value"],
                            entity_type=EntityType(item["entity_type"]),
                            confidence=float(item["confidence"]),
                            source="gemini-api",
                        )
                    )
                return entities
            except Exception as e:
                # Handle connection issues or payload failures gracefully
                raise AppError(f"Failed to extract entities from Gemini API: {str(e)}") from e

    async def generate_recommendations(
        self,
        query: InvestigationQuery,
        evidence: Sequence[EvidenceCandidate],
        risk: RiskAssessment,
    ) -> Sequence[Recommendation]:
        if not self.api_key:
            raise GeminiProviderNotConfiguredError("Gemini recommendations are not configured")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        evidence_str = "\n".join(
            [f"- ID: {ev.id}, Type: {ev.evidence_type.value}, Title: {ev.title}, Summary: {ev.summary}" for ev in evidence]
        )
        
        prompt = (
            f"You are a senior police intelligence advisor for Karnataka State Police.\n"
            f"Based on the investigation query, database evidence, and calculated risk level, generate actionable next-step recommendations.\n\n"
            f"Query: \"{query.query_text}\"\n"
            f"Calculated Risk Score: {risk.score} (Level: {risk.level.value})\n"
            f"Risk Drivers: {', '.join(risk.factors)}\n"
            f"Database Evidence Found:\n{evidence_str}\n\n"
            f"Provide professional tactical recommendations (e.g. Issue LOC, Request CDR, Intercept vehicle, Deploy patrol)."
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "recommendations": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "title": {"type": "STRING"},
                                    "description": {"type": "STRING"},
                                    "priority": {
                                        "type": "STRING",
                                        "enum": ["low", "medium", "high", "urgent"],
                                    },
                                    "rationale": {"type": "STRING"},
                                    "related_evidence_ids": {
                                        "type": "ARRAY",
                                        "items": {"type": "STRING"},
                                    },
                                },
                                "required": ["title", "description", "priority", "rationale", "related_evidence_ids"],
                            },
                        }
                    },
                    "required": ["recommendations"],
                },
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_content)
                
                recs = []
                for item in parsed.get("recommendations", []):
                    recs.append(
                        Recommendation(
                            title=item["title"],
                            description=item["description"],
                            priority=RecommendationPriority(item["priority"]),
                            rationale=item["rationale"],
                            related_evidence_ids=item["related_evidence_ids"],
                        )
                    )
                return recs
            except Exception as e:
                raise AppError(f"Failed to generate recommendations from Gemini API: {str(e)}") from e

    async def generate_formal_report(
        self,
        query_text: str,
        context_data: str,
        conversation_history: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        raw_contents: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Generate a formal investigation report using the KSP system prompt."""
        if not self.api_key:
            raise GeminiProviderNotConfiguredError("Gemini formal report generation is not configured")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        if raw_contents is not None:
            contents = raw_contents
        else:
            # Build conversation context from prior Q&A
            contents = []
            if conversation_history:
                # We map turns. First user turn contains system prompt + context
                first_user_text = (
                    f"{KSP_INVESTIGATION_SYSTEM_PROMPT}\n"
                    f"---\n"
                    f"DATA CONTEXT:\n{context_data}\n"
                    f"---\n"
                    f"OFFICER QUERY:\n{conversation_history[0].get('content', '')}"
                )
                contents.append({
                    "role": "user",
                    "parts": [{"text": first_user_text}]
                })
                for entry in conversation_history[1:]:
                    role = "user" if entry.get("role") == "officer" else "model"
                    contents.append({
                        "role": role,
                        "parts": [{"text": entry.get("content", "")}]
                    })
            else:
                full_prompt = (
                    f"{KSP_INVESTIGATION_SYSTEM_PROMPT}\n"
                    f"---\n"
                    f"DATA CONTEXT:\n{context_data}\n"
                    f"---\n"
                    f"OFFICER QUERY:\n{query_text}"
                )
                contents.append({
                    "role": "user",
                    "parts": [{"text": full_prompt}]
                })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
            },
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                candidate = data["candidates"][0]
                content = candidate.get("content", {})
                parts = content.get("parts", [])
                if parts:
                    part = parts[0]
                    if "functionCall" in part:
                        return part["functionCall"]
                    elif "text" in part:
                        return part["text"]
                return ""
            except Exception as e:
                raise AppError(f"Failed to generate formal report from Gemini API: {str(e)}") from e


