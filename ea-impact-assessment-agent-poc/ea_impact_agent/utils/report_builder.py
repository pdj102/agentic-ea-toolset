from __future__ import annotations

from datetime import datetime

from ea_impact_agent.utils.models import (
    CatalogueValidationResult,
    ConsistencyFinding,
    FindingWithOptions,
    FullAssessmentOutput,
    SpecialistFindings,
)


def compute_rag_status(output: FullAssessmentOutput) -> str:
    all_findings = (
        [f for sf in output.specialist_findings for f in sf.gaps + sf.conflicts]
        + list(output.consistency_findings)
    )
    severities = {f.severity for f in all_findings}
    if "high" in severities:
        return "Red"
    if "medium" in severities:
        return "Amber"
    return "Green"


def _rag_badge(status: str) -> str:
    return {"Red": "🔴 Red", "Amber": "🟡 Amber", "Green": "🟢 Green"}.get(status, status)


def _count_findings(output: FullAssessmentOutput) -> dict:
    counts: dict[str, int] = {"gaps": 0, "conflicts": 0, "quality_issues": 0, "consistency": 0}
    for sf in output.specialist_findings:
        counts["gaps"] += len(sf.gaps)
        counts["conflicts"] += len(sf.conflicts)
        counts["quality_issues"] += len(sf.catalogue_quality_issues)
    counts["consistency"] = len(output.consistency_findings)
    return counts


def _pre_existing_quality_issues(output: FullAssessmentOutput) -> list:
    issues = []
    for sf in output.specialist_findings:
        issues.extend(sf.catalogue_quality_issues)
    return issues


def build_markdown_report(output: FullAssessmentOutput) -> str:
    lines: list[str] = []
    counts = _count_findings(output)
    rag = output.rag_status
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines += [
        "# EA Impact Assessment Report",
        f"*Generated: {now}*",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"**Overall Status:** {_rag_badge(rag)}",
        "",
        "| Finding Type | Count |",
        "|---|---|",
        f"| Gaps (missing catalogue entries) | {counts['gaps']} |",
        f"| Conflicts (rule violations) | {counts['conflicts']} |",
        f"| Catalogue quality issues | {counts['quality_issues']} |",
        f"| Cross-catalogue consistency issues | {counts['consistency']} |",
        "",
    ]

    pre_existing = _pre_existing_quality_issues(output)
    if pre_existing:
        lines += ["### Pre-existing Catalogue Quality Issues", ""]
        lines += ["The following issues were found in the EA catalogue files at startup:", ""]
        for qi in pre_existing:
            lines.append(f"- **[{qi.severity.upper()}]** `{qi.catalogue_entry}` — {qi.issue}")
        lines.append("")
    else:
        lines += ["*No pre-existing catalogue quality issues detected.*", ""]

    lines += [
        "---",
        "",
        "## Design Document Summary",
        "",
        "### Extracted Systems / Applications",
        "",
    ]
    for s in output.extraction_result.systems:
        lines.append(f"- **{s.name}** (domain: {s.owner_domain or 'unknown'}, status: {s.status_implied})")
        if s.technology_refs:
            lines.append(f"  - Technologies: {', '.join(s.technology_refs)}")
        if s.integration_refs:
            lines.append(f"  - Integrations with: {', '.join(s.integration_refs)}")
    lines.append("")

    lines += ["### Extracted Data Entities", ""]
    for de in output.extraction_result.data_entities:
        lines.append(f"- **{de.name}** (domain: {de.owner_domain or 'unknown'}, classification: {de.data_classification or 'unknown'})")
    lines.append("")

    lines += ["### Extracted Technologies", ""]
    for t in output.extraction_result.technologies:
        lines.append(f"- **{t.name}** (category: {t.category or 'unknown'})")
    lines.append("")

    lines += ["### Extracted Integrations", ""]
    for i in output.extraction_result.integrations:
        lines.append(f"- **{i.source_app}** → **{i.target_app}** (pattern: {i.pattern_type or 'unknown'}, tech: {i.technology or 'unknown'})")
    lines.append("")

    lines += ["---", "", "## Findings by Catalogue Domain", ""]

    for sf in output.specialist_findings:
        lines += [f"### {sf.catalogue_type.replace('_', ' ').title()}", ""]

        if sf.matches:
            lines += ["**Matches**", ""]
            lines += ["| Design Entity | Catalogue Entry | Confidence | Notes |", "|---|---|---|---|"]
            for m in sf.matches:
                confidence_pct = f"{m.confidence:.0%}"
                lines.append(f"| {m.design_entity} | `{m.catalogue_entry}` | {confidence_pct} | {m.match_notes} |")
            lines.append("")

        if sf.gaps:
            lines += ["**Gaps** *(no catalogue entry found)*", ""]
            for g in sf.gaps:
                lines.append(f"- **[{g.severity.upper()}]** `{g.design_entity}` — {g.issue}")
                if g.draft_catalogue_entry:
                    lines.append("  ```json")
                    import json
                    lines.append("  " + json.dumps(g.draft_catalogue_entry, indent=2).replace("\n", "\n  "))
                    lines.append("  ```")
            lines.append("")

        if sf.conflicts:
            lines += ["**Conflicts**", ""]
            for c in sf.conflicts:
                rule_ref = f" *(Violates {c.violated_rule})*" if c.violated_rule else ""
                lines.append(f"- **[{c.severity.upper()}]** `{c.design_entity}` vs `{c.catalogue_entry}` — {c.issue}{rule_ref}")
            lines.append("")

        if sf.catalogue_quality_issues:
            lines += ["**Catalogue Quality Issues**", ""]
            for qi in sf.catalogue_quality_issues:
                lines.append(f"- **[{qi.severity.upper()}]** `{qi.catalogue_entry}` — {qi.issue}")
                if qi.schema_rule:
                    lines.append(f"  *Schema rule: {qi.schema_rule}*")
            lines.append("")

        if not (sf.matches or sf.gaps or sf.conflicts or sf.catalogue_quality_issues):
            lines += ["*No findings for this catalogue type.*", ""]

    lines += ["---", "", "## Cross-Catalogue Consistency Issues", ""]

    prog = [f for f in output.consistency_findings if f.finding_source == "programmatic"]
    llm_findings = [f for f in output.consistency_findings if f.finding_source == "llm"]

    if prog:
        lines += ["### Programmatic Rule Violations", ""]
        for f in prog:
            rule_ref = f" (Rule: {f.violated_rule})" if f.violated_rule else ""
            lines.append(f"- **[{f.severity.upper()}]** {f.issue}{rule_ref}")
            if f.source or f.target:
                lines.append(f"  *Entities: {f.source} → {f.target}*")
        lines.append("")
    else:
        lines += ["*No programmatic rule violations detected.*", ""]

    if llm_findings:
        lines += ["### LLM-Identified Issues", ""]
        for f in llm_findings:
            lines.append(f"- **[{f.severity.upper()}]** {f.issue}")
            if f.violated_rule:
                lines.append(f"  *Related rule: {f.violated_rule}*")
        lines.append("")
    else:
        lines += ["*No additional LLM-identified consistency issues.*", ""]

    lines += ["---", "", "## Recommended Options", ""]

    if output.remediation_options:
        for fwo in output.remediation_options:
            lines += [f"### Finding: {fwo.finding_summary}", ""]
            lines.append(f"*Type: {fwo.finding_type} | Severity: {fwo.severity}*")
            lines.append("")
            for opt in fwo.options:
                lines.append(f"**Option: {opt.option_type}**")
                lines.append(f"- *{opt.description}*")
                lines.append(f"- Effort: {opt.effort_estimate} | Risk: {opt.risk_level}")
                lines.append(f"- Rationale: {opt.rationale}")
                if opt.draft_catalogue_entry:
                    import json
                    lines.append("- Draft catalogue entry:")
                    lines.append("  ```json")
                    lines.append("  " + json.dumps(opt.draft_catalogue_entry, indent=2).replace("\n", "\n  "))
                    lines.append("  ```")
                lines.append("")
    else:
        lines += ["*No remediation options generated.*", ""]

    lines += ["---", "", "## Appendix A: Full Entity Match Table", ""]
    lines += ["| Catalogue Type | Design Entity | Catalogue Entry | Confidence |", "|---|---|---|---|"]
    for sf in output.specialist_findings:
        for m in sf.matches:
            lines.append(f"| {sf.catalogue_type} | {m.design_entity} | `{m.catalogue_entry}` | {m.confidence:.0%} |")
    lines.append("")

    lines += ["## Appendix B: Schema Validation Results", ""]
    for vr in output.catalogue_validation_results:
        status = "✓ PASS" if vr.error_count == 0 else f"✗ FAIL ({vr.error_count} error(s))"
        lines.append(f"**{vr.catalogue_file}** — {status} ({vr.entry_count} entries)")
        for err in vr.errors:
            lines.append(f"  - [{err.severity.upper()}] `{err.catalogue_entry_id}` — {err.field}: {err.issue}")
    lines.append("")

    return "\n".join(lines)
