from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ─── Stage 1: Extraction ────────────────────────────────────────────────────

class ExtractedSystem(BaseModel):
    name: str
    description: str = ""
    owner_domain: str = ""
    technology_refs: list[str] = Field(default_factory=list)
    integration_refs: list[str] = Field(default_factory=list)
    data_entity_refs: list[str] = Field(default_factory=list)
    status_implied: str = "proposed"


class ExtractedDataEntity(BaseModel):
    name: str
    description: str = ""
    owner_domain: str = ""
    owning_application: str = ""
    data_classification: str = ""


class ExtractedTechnology(BaseModel):
    name: str
    category: str = ""
    version: str = ""
    used_by: list[str] = Field(default_factory=list)


class ExtractedIntegration(BaseModel):
    name: str = ""
    source_app: str
    target_app: str
    pattern_type: str = ""
    technology: str = ""
    data_entities: list[str] = Field(default_factory=list)
    description: str = ""


class ExtractionResult(BaseModel):
    systems: list[ExtractedSystem] = Field(default_factory=list)
    data_entities: list[ExtractedDataEntity] = Field(default_factory=list)
    technologies: list[ExtractedTechnology] = Field(default_factory=list)
    integrations: list[ExtractedIntegration] = Field(default_factory=list)


# ─── Stage 2: Specialist Findings ───────────────────────────────────────────

class MatchFinding(BaseModel):
    design_entity: str
    catalogue_entry: str
    confidence: float = Field(ge=0.0, le=1.0)
    match_notes: str = ""


class GapFinding(BaseModel):
    design_entity: str
    issue: str
    severity: Literal["high", "medium", "low"] = "medium"
    draft_catalogue_entry: dict | None = None


class ConflictFinding(BaseModel):
    design_entity: str
    catalogue_entry: str
    issue: str
    severity: Literal["high", "medium", "low"] = "high"
    violated_rule: str = ""


class CatalogueQualityIssue(BaseModel):
    catalogue_entry: str
    issue: str
    severity: Literal["high", "medium", "low"] = "medium"
    schema_rule: str = ""


class SpecialistFindings(BaseModel):
    catalogue_type: str
    matches: list[MatchFinding] = Field(default_factory=list)
    gaps: list[GapFinding] = Field(default_factory=list)
    conflicts: list[ConflictFinding] = Field(default_factory=list)
    catalogue_quality_issues: list[CatalogueQualityIssue] = Field(default_factory=list)
    error: str | None = None


# ─── Stage 3: Consistency Findings ──────────────────────────────────────────

class ConsistencyFinding(BaseModel):
    catalogue_type: str = "cross-catalogue"
    source: str = ""
    target: str = ""
    issue: str
    severity: Literal["high", "medium", "low"] = "high"
    violated_rule: str = ""
    finding_source: Literal["programmatic", "llm"] = "programmatic"


# ─── Stage 4: Options ────────────────────────────────────────────────────────

class RemediationOption(BaseModel):
    option_type: Literal["CONFORM", "EXTEND", "EXCEPTION", "RETIRE"]
    description: str
    effort_estimate: Literal["low", "medium", "high"]
    risk_level: Literal["low", "medium", "high"]
    rationale: str
    draft_catalogue_entry: dict | None = None


class FindingWithOptions(BaseModel):
    finding_type: str
    finding_summary: str
    severity: Literal["high", "medium", "low"] = "medium"
    options: list[RemediationOption] = Field(default_factory=list)
    error: str | None = None


# ─── Validation ──────────────────────────────────────────────────────────────

class ValidationError(BaseModel):
    catalogue_entry_id: str
    field: str
    issue: str
    severity: Literal["high", "medium", "low"] = "medium"


class CatalogueValidationResult(BaseModel):
    catalogue_type: str
    catalogue_file: str
    errors: list[ValidationError] = Field(default_factory=list)
    entry_count: int = 0
    error_count: int = 0


# ─── Full Output ──────────────────────────────────────────────────────────────

class FullAssessmentOutput(BaseModel):
    extraction_result: ExtractionResult
    specialist_findings: list[SpecialistFindings] = Field(default_factory=list)
    consistency_findings: list[ConsistencyFinding] = Field(default_factory=list)
    remediation_options: list[FindingWithOptions] = Field(default_factory=list)
    catalogue_validation_results: list[CatalogueValidationResult] = Field(default_factory=list)
    rag_status: Literal["Red", "Amber", "Green"] = "Green"
