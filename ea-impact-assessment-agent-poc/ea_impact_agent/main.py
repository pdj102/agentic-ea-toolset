"""EA Impact Assessment Agent — CLI entry point."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from ea_impact_agent.agents.consistency import run_llm_consistency_check, run_programmatic_checks
from ea_impact_agent.agents.options_generator import generate_options
from ea_impact_agent.agents.orchestrator import extract_entities
from ea_impact_agent.agents.specialist import run_specialist
from ea_impact_agent.utils.file_loader import load_all_catalogues, load_design_doc
from ea_impact_agent.utils.models import FullAssessmentOutput
from ea_impact_agent.utils.report_builder import build_markdown_report, compute_rag_status
from ea_impact_agent.utils.schema_loader import (
    get_rules_for_type,
    load_all_schemas,
    load_meta_schema,
    load_relationship_rules,
)
from ea_impact_agent.utils.schema_validator import validate_all_catalogues


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="EA Impact Assessment Agent — assess a design document against the EA catalogue."
    )
    parser.add_argument("--design-doc", required=True, help="Path to design document (.pdf or .md)")
    parser.add_argument("--catalogue-dir", required=True, help="Directory containing catalogue JSON files")
    parser.add_argument("--schema-dir", required=True, help="Directory containing EA schema files")
    parser.add_argument("--output-dir", default="output", help="Directory for output files (default: ./output)")
    return parser.parse_args()


async def run(args: argparse.Namespace) -> None:
    design_doc_path = Path(args.design_doc)
    catalogue_dir = Path(args.catalogue_dir)
    schema_dir = Path(args.schema_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Startup: load schemas ───────────────────────────────────────────────
    print("Loading schemas...")
    meta_schema = load_meta_schema(schema_dir)
    schemas = load_all_schemas(schema_dir)
    rules = load_relationship_rules(schema_dir)
    print(f"  Loaded {len(schemas)} schema type(s), {len(rules)} relationship rule(s)")

    print("Loading catalogues...")
    catalogues = load_all_catalogues(catalogue_dir, meta_schema)
    print(f"  Loaded {len(catalogues)} catalogue(s): {', '.join(catalogues.keys())}")

    print("Validating catalogues at startup...")
    validation_results = validate_all_catalogues(catalogues, schemas, meta_schema)
    total_pre_existing = sum(vr.error_count for vr in validation_results)
    if total_pre_existing:
        print(f"  ⚠ {total_pre_existing} pre-existing catalogue issue(s) found — see Executive Summary")
    else:
        print("  ✓ All catalogues are schema-valid")

    # ── Load design document ────────────────────────────────────────────────
    print(f"Loading design document: {design_doc_path}")
    design_doc_text = load_design_doc(design_doc_path)

    # ── Stage 1: Extract entities ───────────────────────────────────────────
    print("\n[Stage 1] Extracting entities from design document...")
    extraction_result = await extract_entities(design_doc_text, schemas)
    print(
        f"  Extracted: {len(extraction_result.systems)} system(s), "
        f"{len(extraction_result.data_entities)} data entit(ies), "
        f"{len(extraction_result.technologies)} technolog(ies), "
        f"{len(extraction_result.integrations)} integration(s)"
    )

    # ── Stage 2: Specialist agents (parallel) ───────────────────────────────
    print("\n[Stage 2] Running specialist agents in parallel...")
    catalogue_types = list(catalogues.keys())
    specialist_tasks = [
        run_specialist(
            catalogue_type=ctype,
            extraction_result=extraction_result,
            catalogue=catalogues[ctype],
            schema=schemas.get(ctype, {}),
            relevant_rules=get_rules_for_type(rules, ctype),
        )
        for ctype in catalogue_types
    ]
    specialist_findings = list(await asyncio.gather(*specialist_tasks))

    for sf in specialist_findings:
        status = "⚠ agent-error" if sf.error else "✓"
        print(
            f"  {status} {sf.catalogue_type}: "
            f"{len(sf.matches)} match(es), {len(sf.gaps)} gap(s), "
            f"{len(sf.conflicts)} conflict(s), {len(sf.catalogue_quality_issues)} quality issue(s)"
        )

    # ── Stage 3: Consistency checks ─────────────────────────────────────────
    print("\n[Stage 3] Running consistency checks...")
    programmatic_findings = run_programmatic_checks(extraction_result, catalogues, specialist_findings, rules)
    print(f"  Programmatic: {len(programmatic_findings)} rule violation(s) found")

    llm_findings = await run_llm_consistency_check(extraction_result, specialist_findings, programmatic_findings)
    print(f"  LLM reasoning: {len(llm_findings)} additional issue(s) found")

    all_consistency_findings = programmatic_findings + llm_findings

    # ── Stage 4: Options generation ─────────────────────────────────────────
    print("\n[Stage 4] Generating remediation options...")
    remediation_options = await generate_options(specialist_findings, all_consistency_findings, schemas)
    print(f"  Generated options for {len(remediation_options)} finding(s)")

    # ── Assemble output ─────────────────────────────────────────────────────
    output = FullAssessmentOutput(
        extraction_result=extraction_result,
        specialist_findings=specialist_findings,
        consistency_findings=all_consistency_findings,
        remediation_options=remediation_options,
        catalogue_validation_results=validation_results,
        rag_status="Green",
    )
    output.rag_status = compute_rag_status(output)

    # ── Write outputs ───────────────────────────────────────────────────────
    report_path = output_dir / "ea_impact_assessment_report.md"
    findings_path = output_dir / "ea_impact_findings.json"

    report_md = build_markdown_report(output)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"\nReport written: {report_path}")

    findings_json = output.model_dump_json(indent=2)
    findings_path.write_text(findings_json, encoding="utf-8")
    print(f"Findings JSON written: {findings_path}")

    print(f"\nOverall status: {output.rag_status}")


def main() -> None:
    load_dotenv()
    args = _parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
