from __future__ import annotations

import anthropic

from ea_impact_agent.utils.models import (
    CatalogueQualityIssue,
    ConflictFinding,
    ExtractionResult,
    GapFinding,
    MatchFinding,
    SpecialistFindings,
)

_SPECIALIST_TOOL = {
    "name": "report_specialist_findings",
    "description": "Report findings from matching design entities against the EA catalogue.",
    "input_schema": {
        "type": "object",
        "properties": {
            "matches": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "design_entity": {"type": "string"},
                        "catalogue_entry": {"type": "string", "description": "Catalogue ID e.g. APP-0001"},
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "match_notes": {"type": "string"},
                    },
                    "required": ["design_entity", "catalogue_entry", "confidence"],
                },
            },
            "gaps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "design_entity": {"type": "string"},
                        "issue": {"type": "string"},
                        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                        "draft_catalogue_entry": {"type": "object"},
                    },
                    "required": ["design_entity", "issue", "severity"],
                },
            },
            "conflicts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "design_entity": {"type": "string"},
                        "catalogue_entry": {"type": "string"},
                        "issue": {"type": "string"},
                        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                        "violated_rule": {"type": "string"},
                    },
                    "required": ["design_entity", "catalogue_entry", "issue", "severity"],
                },
            },
            "catalogue_quality_issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "catalogue_entry": {"type": "string"},
                        "issue": {"type": "string"},
                        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                        "schema_rule": {"type": "string"},
                    },
                    "required": ["catalogue_entry", "issue", "severity"],
                },
            },
        },
        "required": ["matches", "gaps", "conflicts", "catalogue_quality_issues"],
    },
}


def _build_specialist_prompt(
    catalogue_type: str,
    extraction_result: ExtractionResult,
    catalogue: list[dict],
    schema: dict,
    relevant_rules: list[dict],
) -> str:
    import json

    type_map = {
        "application": extraction_result.systems,
        "technology": extraction_result.technologies,
        "data_entity": extraction_result.data_entities,
        "integration": extraction_result.integrations,
    }
    design_entities = type_map.get(catalogue_type, [])

    return (
        f"You are an EA {catalogue_type.replace('_', ' ').title()} Specialist. "
        f"Analyse the design document extracts against the {catalogue_type} catalogue.\n\n"
        f"DESIGN ENTITIES EXTRACTED:\n{json.dumps([e.model_dump() for e in design_entities], indent=2)}\n\n"
        f"CATALOGUE ENTRIES:\n{json.dumps(catalogue, indent=2)}\n\n"
        f"SCHEMA DEFINITION:\n{json.dumps(schema, indent=2)}\n\n"
        f"RELEVANT RELATIONSHIP RULES:\n{json.dumps(relevant_rules, indent=2)}\n\n"
        "Perform three tasks:\n"
        "1. MATCH: For each design entity, find the best matching catalogue entry. "
        "   Self-estimate a confidence score 0.0-1.0. Note name variants or aliases.\n"
        "2. GAP DETECT: For design entities with no catalogue match, flag as a gap. "
        "   For EXTEND options provide a draft catalogue entry (use schema fields; mark unknown fields as "
        "   'REQUIRED - TO BE CONFIRMED').\n"
        "3. CATALOGUE QUALITY: For matched catalogue entries, validate them against the schema. "
        "   Flag missing required fields or invalid enum values as catalogue_quality_issues.\n\n"
        "Severity guide: 'high' for blocking issues (retired/unapproved status, missing required fields), "
        "'medium' for gaps and quality issues, 'low' for informational findings."
    )


async def run_specialist(
    catalogue_type: str,
    extraction_result: ExtractionResult,
    catalogue: list[dict],
    schema: dict,
    relevant_rules: list[dict],
) -> SpecialistFindings:
    client = anthropic.AsyncAnthropic()
    prompt = _build_specialist_prompt(catalogue_type, extraction_result, catalogue, schema, relevant_rules)

    for attempt in range(2):
        try:
            response = await client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
                tools=[_SPECIALIST_TOOL],
                tool_choice={"type": "auto"},
                timeout=120.0,
            )
            for block in response.content:
                if block.type == "tool_use" and block.name == "report_specialist_findings":
                    data = block.input
                    return SpecialistFindings(
                        catalogue_type=catalogue_type,
                        matches=[MatchFinding(**m) for m in data.get("matches", [])],
                        gaps=[GapFinding(**g) for g in data.get("gaps", [])],
                        conflicts=[ConflictFinding(**c) for c in data.get("conflicts", [])],
                        catalogue_quality_issues=[CatalogueQualityIssue(**q) for q in data.get("catalogue_quality_issues", [])],
                    )
        except Exception as exc:
            if attempt == 0:
                print(f"  [specialist:{catalogue_type}] Attempt 1 failed: {exc}. Retrying...")
                continue
            print(f"  [specialist:{catalogue_type}] Failed after 2 attempts: {exc}")
            return SpecialistFindings(catalogue_type=catalogue_type, error=str(exc))

    return SpecialistFindings(catalogue_type=catalogue_type, error="agent-error: no tool use response")
