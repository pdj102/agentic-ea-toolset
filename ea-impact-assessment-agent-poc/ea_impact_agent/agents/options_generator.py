from __future__ import annotations

import json

import anthropic

from ea_impact_agent.utils.models import (
    CatalogueQualityIssue,
    ConflictFinding,
    ConsistencyFinding,
    FindingWithOptions,
    GapFinding,
    RemediationOption,
    SpecialistFindings,
)

_OPTIONS_TOOL = {
    "name": "report_remediation_options",
    "description": "Report tiered remediation options for an EA finding.",
    "input_schema": {
        "type": "object",
        "properties": {
            "options": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "option_type": {"type": "string", "enum": ["CONFORM", "EXTEND", "EXCEPTION", "RETIRE"]},
                        "description": {"type": "string"},
                        "effort_estimate": {"type": "string", "enum": ["low", "medium", "high"]},
                        "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
                        "rationale": {"type": "string"},
                        "draft_catalogue_entry": {"type": "object"},
                    },
                    "required": ["option_type", "description", "effort_estimate", "risk_level", "rationale"],
                },
            }
        },
        "required": ["options"],
    },
}


def _finding_to_prompt_text(finding: GapFinding | ConflictFinding | ConsistencyFinding | CatalogueQualityIssue) -> tuple[str, str, str]:
    if isinstance(finding, GapFinding):
        finding_type = "gap"
        summary = f"Gap: {finding.design_entity} — {finding.issue}"
        severity = finding.severity
        draft_hint = ""
        if finding.draft_catalogue_entry:
            draft_hint = f"\nA draft catalogue entry was already produced:\n{json.dumps(finding.draft_catalogue_entry, indent=2)}\nRefine this draft for EXTEND options — do not regenerate from scratch."
        extra = draft_hint
    elif isinstance(finding, ConflictFinding):
        finding_type = "conflict"
        summary = f"Conflict: {finding.design_entity} vs {finding.catalogue_entry} — {finding.issue}"
        severity = finding.severity
        extra = f"\nViolated rule: {finding.violated_rule}" if finding.violated_rule else ""
    elif isinstance(finding, ConsistencyFinding):
        finding_type = "consistency"
        summary = f"Consistency issue: {finding.issue}"
        severity = finding.severity
        extra = f"\nViolated rule: {finding.violated_rule}" if finding.violated_rule else ""
    else:
        finding_type = "catalogue_quality"
        summary = f"Catalogue quality: {finding.catalogue_entry} — {finding.issue}"
        severity = finding.severity
        extra = f"\nSchema rule: {finding.schema_rule}" if finding.schema_rule else ""
    return finding_type, summary, extra


async def _generate_options_for_finding(
    finding: GapFinding | ConflictFinding | ConsistencyFinding | CatalogueQualityIssue,
    schemas: dict[str, dict],
    client: anthropic.AsyncAnthropic,
    semaphore: "asyncio.Semaphore",
) -> FindingWithOptions:
    import asyncio
    async with semaphore:
        finding_type, summary, extra = _finding_to_prompt_text(finding)
        severity = finding.severity

        prompt = (
            "You are an EA Options Generator. For the following EA finding, generate 2-4 tiered "
            "remediation options using the option types: CONFORM, EXTEND, EXCEPTION, RETIRE.\n\n"
            f"FINDING TYPE: {finding_type}\n"
            f"FINDING: {summary}\n"
            f"SEVERITY: {severity}\n"
            f"{extra}\n\n"
            f"RELEVANT SCHEMAS:\n{json.dumps(schemas, indent=2)}\n\n"
            "Option guidance:\n"
            "- CONFORM: Change the design to use existing EA-approved components\n"
            "- EXTEND: Add a new entry to the EA catalogue. For EXTEND, include a schema-valid "
            "  draft_catalogue_entry (use schema fields; mark unknown values as 'REQUIRED - TO BE CONFIRMED')\n"
            "- EXCEPTION: Document a governed deviation with rationale and conditions\n"
            "- RETIRE: Trigger a review of an outdated EA catalogue entry\n\n"
            "Each option must have a specific, actionable description. Not all option types may be applicable."
        )

        for attempt in range(2):
            try:
                response = await client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}],
                    tools=[_OPTIONS_TOOL],
                    tool_choice={"type": "auto"},
                    timeout=120.0,
                )
                for block in response.content:
                    if block.type == "tool_use" and block.name == "report_remediation_options":
                        data = block.input
                        options = [RemediationOption(**o) for o in data.get("options", [])]
                        return FindingWithOptions(
                            finding_type=finding_type,
                            finding_summary=summary,
                            severity=severity,
                            options=options,
                        )
            except Exception as exc:
                if attempt == 0:
                    print(f"  [options] Attempt 1 failed for finding '{summary[:60]}': {exc}. Retrying...")
                    continue
                print(f"  [options] Failed after 2 attempts: {exc}")
                return FindingWithOptions(
                    finding_type=finding_type,
                    finding_summary=summary,
                    severity=severity,
                    error="agent-error",
                )

        return FindingWithOptions(
            finding_type=finding_type,
            finding_summary=summary,
            severity=severity,
            error="agent-error: no tool use response",
        )


async def generate_options(
    specialist_findings: list[SpecialistFindings],
    consistency_findings: list[ConsistencyFinding],
    schemas: dict[str, dict],
) -> list[FindingWithOptions]:
    import asyncio

    semaphore = asyncio.Semaphore(3)
    client = anthropic.AsyncAnthropic()
    tasks = []

    for sf in specialist_findings:
        for finding in sf.gaps + sf.conflicts + sf.catalogue_quality_issues:
            tasks.append(_generate_options_for_finding(finding, schemas, client, semaphore))

    for finding in consistency_findings:
        tasks.append(_generate_options_for_finding(finding, schemas, client, semaphore))

    if not tasks:
        return []

    results = await asyncio.gather(*tasks)
    return list(results)
