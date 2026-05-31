from __future__ import annotations

import json

import anthropic

from ea_impact_agent.utils.models import (
    ExtractionResult,
    ExtractedDataEntity,
    ExtractedIntegration,
    ExtractedSystem,
    ExtractedTechnology,
)

_EXTRACTION_TOOL = {
    "name": "extract_entities",
    "description": "Extract all EA-relevant entities from the design document into structured JSON.",
    "input_schema": {
        "type": "object",
        "properties": {
            "systems": {
                "type": "array",
                "description": "Named systems, applications, or services mentioned in the design document.",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "owner_domain": {"type": "string"},
                        "technology_refs": {"type": "array", "items": {"type": "string"}},
                        "integration_refs": {"type": "array", "items": {"type": "string"}},
                        "data_entity_refs": {"type": "array", "items": {"type": "string"}},
                        "status_implied": {"type": "string", "enum": ["proposed", "live", "deprecated", "retired"]},
                    },
                    "required": ["name"],
                },
            },
            "data_entities": {
                "type": "array",
                "description": "Data entities, data stores, or datasets mentioned.",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "owner_domain": {"type": "string"},
                        "owning_application": {"type": "string"},
                        "data_classification": {"type": "string"},
                    },
                    "required": ["name"],
                },
            },
            "technologies": {
                "type": "array",
                "description": "Technology choices mentioned (languages, frameworks, databases, platforms).",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "category": {"type": "string"},
                        "version": {"type": "string"},
                        "used_by": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["name"],
                },
            },
            "integrations": {
                "type": "array",
                "description": "Integration points and data flows between systems.",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "source_app": {"type": "string"},
                        "target_app": {"type": "string"},
                        "pattern_type": {"type": "string"},
                        "technology": {"type": "string"},
                        "data_entities": {"type": "array", "items": {"type": "string"}},
                        "description": {"type": "string"},
                    },
                    "required": ["source_app", "target_app"],
                },
            },
        },
        "required": ["systems", "data_entities", "technologies", "integrations"],
    },
}


def _build_system_prompt(schemas: dict[str, dict]) -> str:
    field_summaries = []
    for type_name, schema in schemas.items():
        fields = list(schema.get("fields", {}).keys())
        field_summaries.append(f"  {type_name}: {', '.join(fields)}")
    fields_text = "\n".join(field_summaries)

    return (
        "You are an Enterprise Architecture analyst. Your task is to extract all EA-relevant "
        "entities from the provided design document.\n\n"
        "Extract:\n"
        "- Systems/applications (new and existing)\n"
        "- Data entities and data stores\n"
        "- Technology choices\n"
        "- Integration points and data flows\n\n"
        "Map extracted information to these EA schema fields where possible:\n"
        f"{fields_text}\n\n"
        "Be comprehensive — include all systems mentioned, even existing ones referenced as integration targets. "
        "For status_implied, use 'proposed' for new systems and infer from context for existing ones."
    )


async def extract_entities(design_doc_text: str, schemas: dict[str, dict]) -> ExtractionResult:
    client = anthropic.AsyncAnthropic()
    system_prompt = _build_system_prompt(schemas)

    for attempt in range(2):
        try:
            response = await client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": f"Extract EA entities from this design document:\n\n{design_doc_text}"}],
                tools=[_EXTRACTION_TOOL],
                tool_choice={"type": "auto"},
                timeout=60.0,
            )
            for block in response.content:
                if block.type == "tool_use" and block.name == "extract_entities":
                    data = block.input
                    return ExtractionResult(
                        systems=[ExtractedSystem(**s) for s in data.get("systems", [])],
                        data_entities=[ExtractedDataEntity(**d) for d in data.get("data_entities", [])],
                        technologies=[ExtractedTechnology(**t) for t in data.get("technologies", [])],
                        integrations=[ExtractedIntegration(**i) for i in data.get("integrations", [])],
                    )
        except Exception as exc:
            if attempt == 0:
                print(f"  [orchestrator] Extraction attempt 1 failed: {exc}. Retrying...")
                continue
            print(f"  [orchestrator] Extraction failed after 2 attempts: {exc}")

    return ExtractionResult()
