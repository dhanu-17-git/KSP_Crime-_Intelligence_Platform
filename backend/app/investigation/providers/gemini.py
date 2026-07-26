import json
import logging
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


logger = logging.getLogger(__name__)


class GeminiProviderNotConfiguredError(AppError):
    status_code = 503
    error_code = "AI_PROVIDER_NOT_CONFIGURED"


KSP_INVESTIGATION_SYSTEM_PROMPT = """You are an AI Police Intelligence Assistant for Karnataka State Police (KSP).

TONE & STYLE:
- Maintain a formal, professional, clear, and objective tone appropriate for law enforcement officers.
- Do NOT use casual internet slang, emojis, or conversational filler ("Sure!", "How can I help you today!", "Great question!").
- Present intelligence findings clearly using plain text paragraphs and bullet points. Do NOT use markdown formatting like asterisks (**bold**) or hashtags (#), as the frontend renders responses in plain text.
- Avoid forcing every response into a rigid static report card template. Format your output naturally to best answer the officer's specific query.

DATA INTEGRITY & RULES:
- Base all investigative findings ONLY on the evidence provided in the DATA CONTEXT. Do not invent unverified facts, names, dates, or figures.
- Never reference internal technology stack details (database names, ORM layers, backend frameworks, environment variables) — report only investigative facts.
- Explicitly highlight any cross-jurisdictional or cross-district patterns if a suspect or vehicle appears across multiple police stations or districts.
- If no records exist for a specific query, clearly state: "No matching records found in the KSP database for this query."
- OPERATIONAL ACTIONS: If the officer explicitly commands an operational action (such as notifying a police station, flagging a suspect, or adding a case note), you MUST issue the appropriate function call (notify_station, flag_suspect, or add_case_note).
- When confirming an operational action executed by a tool, respond ONLY in this exact format:
  ACTION TAKEN: [one-line description of what action was taken], [timestamp].
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
        self.model_name = model_name or "gemini-flash-latest"

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
            function_names: list[str] = []
            for tool in tools:
                for declaration in tool.get("functionDeclarations", []):
                    name = declaration.get("name")
                    if name:
                        function_names.append(name)
            if function_names:
                payload["toolConfig"] = {
                    "functionCallingConfig": {
                        "mode": "ANY",
                        "allowedFunctionNames": function_names,
                    }
                }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                candidate = data["candidates"][0]
                content = candidate.get("content", {})
                parts = content.get("parts", [])
                part_summaries: list[dict[str, Any]] = []
                first_text: str | None = None
                for index, part in enumerate(parts):
                    function_call = part.get("functionCall") or part.get("function_call")
                    part_summaries.append(
                        {
                            "index": index,
                            "keys": sorted(part.keys()),
                            "has_function_call": function_call is not None,
                            "has_text": "text" in part,
                        }
                    )
                    if function_call is not None:
                        logger.info(
                            "Gemini raw response included function call",
                            extra={
                                "details": {
                                    "query_text": query_text,
                                    "parts": part_summaries,
                                    "function_call": function_call,
                                    "finish_reason": candidate.get("finishReason"),
                                }
                            },
                        )
                        return function_call
                    if first_text is None and "text" in part:
                        first_text = part["text"]
                if first_text is not None:
                    logger.info(
                        "Gemini raw response returned text",
                        extra={
                            "details": {
                                "query_text": query_text,
                                "parts": part_summaries,
                                "finish_reason": candidate.get("finishReason"),
                            }
                        },
                    )
                    return first_text
                logger.info(
                    "Gemini raw response had no usable parts",
                    extra={
                        "details": {
                            "query_text": query_text,
                            "parts": part_summaries,
                            "finish_reason": candidate.get("finishReason"),
                        }
                    },
                )
                return ""
            except Exception as e:
                raise AppError(f"Failed to generate formal report from Gemini API: {str(e)}") from e


