from __future__ import annotations

import anthropic

from ea_impact_agent.utils.models import (
    ConsistencyFinding,
    ExtractionResult,
    SpecialistFindings,
)

_CONSISTENCY_TOOL = {
    "name": "report_consistency_findings",
    "description": "Report cross-catalogue consistency issues found by reasoning across all specialist findings.",
    "input_schema": {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "issue": {"type": "string"},
                        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                        "violated_rule": {"type": "string"},
                    },
                    "required": ["issue", "severity"],
                },
            }
        },
        "required": ["findings"],
    },
}


def _build_id_index(catalogues: dict[str, list[dict]]) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for entries in catalogues.values():
        for entry in entries:
            eid = entry.get("id")
            if eid:
                index[eid] = entry
    return index


def run_programmatic_checks(
    extraction_result: ExtractionResult,
    all_catalogues: dict[str, list[dict]],
    specialist_findings: list[SpecialistFindings],
    rules: list[dict],
) -> list[ConsistencyFinding]:
    findings: list[ConsistencyFinding] = []
    id_index = _build_id_index(all_catalogues)
    app_catalogue = all_catalogues.get("application", [])
    tech_catalogue = all_catalogues.get("technology", [])

    app_by_name = {a["name"].lower(): a for a in app_catalogue}
    tech_by_name = {t["name"].lower(): t for t in tech_catalogue}

    def find_app(name: str) -> dict | None:
        return app_by_name.get(name.lower()) or id_index.get(name)

    def find_tech(name: str) -> dict | None:
        return tech_by_name.get(name.lower()) or id_index.get(name)

    # REL-001: Applications may only integrate with live applications
    for integration in extraction_result.integrations:
        target_entry = find_app(integration.target_app)
        if target_entry:
            blocked = ["retired", "deprecated"]
            if target_entry.get("status") in blocked:
                findings.append(ConsistencyFinding(
                    source=integration.source_app,
                    target=integration.target_app,
                    issue=(
                        f"Integration target '{integration.target_app}' has status "
                        f"'{target_entry['status']}'. Only 'live' applications may be integration targets."
                    ),
                    severity="high",
                    violated_rule="REL-001",
                    finding_source="programmatic",
                ))

    # REL-002: A data entity may only have one owning application
    owner_map: dict[str, list[str]] = {}
    for de in extraction_result.data_entities:
        if de.owning_application:
            owner_map.setdefault(de.name, []).append(de.owning_application)
    data_catalogue = all_catalogues.get("data_entity", [])
    for cat_de in data_catalogue:
        de_name = cat_de.get("name", "")
        existing_owner = cat_de.get("owning_application")
        design_owners = owner_map.get(de_name, [])
        for design_owner in design_owners:
            if existing_owner and design_owner and existing_owner != design_owner:
                findings.append(ConsistencyFinding(
                    source=design_owner,
                    target=de_name,
                    issue=(
                        f"Data entity '{de_name}' is owned by '{existing_owner}' in the catalogue "
                        f"but the design claims ownership for '{design_owner}'. "
                        "A data entity may only have one owning application."
                    ),
                    severity="high",
                    violated_rule="REL-002",
                    finding_source="programmatic",
                ))

    # REL-003: Applications may only use approved or conditional technologies
    for system in extraction_result.systems:
        for tech_name in system.technology_refs:
            tech_entry = find_tech(tech_name)
            if tech_entry:
                blocked_statuses = ["unapproved", "retired"]
                if tech_entry.get("status") in blocked_statuses:
                    findings.append(ConsistencyFinding(
                        source=system.name,
                        target=tech_name,
                        issue=(
                            f"'{system.name}' uses technology '{tech_name}' which has status "
                            f"'{tech_entry['status']}'. Only 'approved' or 'conditional' technologies may be used."
                        ),
                        severity="high",
                        violated_rule="REL-003",
                        finding_source="programmatic",
                    ))

    # REL-004: Integrations must use an approved pattern
    # Check: proposed integrations use a pattern_type not present among approved integrations in that domain
    int_catalogue = all_catalogues.get("integration", [])
    approved_patterns = {i.get("pattern_type") for i in int_catalogue if i.get("status") in ("approved", "conditional")}
    for integration in extraction_result.integrations:
        if integration.pattern_type and integration.pattern_type not in approved_patterns:
            findings.append(ConsistencyFinding(
                source=integration.source_app,
                target=integration.target_app,
                issue=(
                    f"Integration '{integration.source_app}' → '{integration.target_app}' uses pattern "
                    f"'{integration.pattern_type}' which is not among approved patterns in the catalogue "
                    f"({', '.join(sorted(approved_patterns))})."
                ),
                severity="high",
                violated_rule="REL-004",
                finding_source="programmatic",
            ))

    # REL-005: A proposed application must reference at least one approved technology
    for system in extraction_result.systems:
        if system.status_implied == "proposed" and system.technology_refs:
            has_approved = any(
                (find_tech(t) or {}).get("status") == "approved"
                for t in system.technology_refs
            )
            if not has_approved:
                findings.append(ConsistencyFinding(
                    source=system.name,
                    target="",
                    issue=(
                        f"Proposed application '{system.name}' does not reference any approved technology. "
                        "At least one approved technology is required."
                    ),
                    severity="high",
                    violated_rule="REL-005",
                    finding_source="programmatic",
                ))

    return findings


async def run_llm_consistency_check(
    extraction_result: ExtractionResult,
    specialist_findings: list[SpecialistFindings],
    programmatic_findings: list[ConsistencyFinding],
) -> list[ConsistencyFinding]:
    import json

    client = anthropic.AsyncAnthropic()

    prompt = (
        "You are an Enterprise Architecture Consistency Checker. "
        "Review all specialist findings and programmatic rule violations to identify additional "
        "cross-catalogue consistency issues not already captured.\n\n"
        "Focus on:\n"
        "- Data entity ownership conflicts across domain boundaries\n"
        "- Circular dependencies introduced by the design\n"
        "- EA anti-patterns not covered by explicit rules\n"
        "- Domain boundary violations\n\n"
        f"EXTRACTION RESULT:\n{json.dumps(extraction_result.model_dump(), indent=2)}\n\n"
        f"SPECIALIST FINDINGS:\n{json.dumps([sf.model_dump() for sf in specialist_findings], indent=2)}\n\n"
        f"PROGRAMMATIC RULE VIOLATIONS (already captured, do not duplicate):\n"
        f"{json.dumps([f.model_dump() for f in programmatic_findings], indent=2)}\n\n"
        "Report only NEW issues not already listed in the programmatic violations above."
    )

    for attempt in range(2):
        try:
            response = await client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
                tools=[_CONSISTENCY_TOOL],
                tool_choice={"type": "auto"},
                timeout=120.0,
            )
            for block in response.content:
                if block.type == "tool_use" and block.name == "report_consistency_findings":
                    data = block.input
                    return [
                        ConsistencyFinding(finding_source="llm", **f)
                        for f in data.get("findings", [])
                    ]
        except Exception as exc:
            if attempt == 0:
                print(f"  [consistency] LLM pass attempt 1 failed: {exc}. Retrying...")
                continue
            print(f"  [consistency] LLM pass failed after 2 attempts: {exc}")

    return []
