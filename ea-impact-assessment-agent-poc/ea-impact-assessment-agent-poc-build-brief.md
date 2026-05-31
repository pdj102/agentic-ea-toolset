# EA Impact Assessment Agent — PoC Build Brief

## Overview
Build a proof-of-concept EA (Enterprise Architecture) Impact Assessment tool using a
multi-agent architecture. The tool takes a design document and EA catalogue files as
input, validates them against EA object schemas, assesses consistency between the
design and the EA model, and recommends structured options for alignment.

## Core Architecture
Implement an orchestrator + specialist agents pattern:

1. **Orchestrator Agent** — loads schemas at startup, parses the design document, extracts entities against schema field definitions, coordinates specialist agents, synthesises findings
2. **Specialist Agents** (one per catalogue type):
   - Application Architecture Agent
   - Data Architecture Agent
   - Technology Architecture Agent
   - Integration Architecture Agent
3. **Consistency Checker Agent** — runs programmatic relationship rule checks then LLM-based cross-catalogue reasoning
4. **Options Generator Agent** — produces tiered remediation options per finding, including schema-valid draft catalogue entries where applicable

## Tech Stack
- Language: Python 3.11+
- LLM: Anthropic Claude API (claude-sonnet-4-6)
- File handling: Support .md and .json catalogue files, .pdf and .md design docs
- Output: Structured markdown report + JSON findings file
- No vector store required for PoC — use file-based context with selective file passing per agent

## Input Files (user provides at runtime)
The tool should accept the following via CLI arguments or a config file:
  --design-doc        Path to design document (.pdf or .md)
  --catalogue-dir     Path to directory containing catalogue files
  --schema-dir        Path to directory containing EA schema files
  --output-dir        Path for report output

Catalogue files in the catalogue directory should follow this naming convention:
  ea_catalogue_applications.json
  ea_catalogue_data_entities.json
  ea_catalogue_technologies.json
  ea_catalogue_integrations.json
  ea_catalogue_relationships.json

Schema files in the schema directory:
  ea_meta_schema.json
  application_schema.json
  data_entity_schema.json
  technology_schema.json
  integration_schema.json
  relationship_rules.json

## EA Schema Layer

### Schema File Definitions

Each schema file defines the structure for one EA object type. Schemas specify field names, types, required/optional status, allowed enum values, ID patterns, and cross-object reference types.

**application_schema.json**
```json
{
  "object_type": "application",
  "version": "1.0",
  "fields": {
    "id":               { "type": "string",  "required": true,  "pattern": "APP-[0-9]{4}" },
    "name":             { "type": "string",  "required": true },
    "alias":            { "type": "array",   "required": false, "items": "string" },
    "status":           { "type": "enum",    "required": true,"values": ["proposed", "live", "deprecated", "retired"] },
    "owner_domain":     { "type": "string",  "required": true },
    "technology_refs":  { "type": "array",   "required": true, "items": "ref:technology", "min_items": 1 },
    "data_entity_refs": { "type": "array",   "required": false, "items": "ref:data_entity" },
    "integration_refs": { "type": "array",   "required": false, "items": "ref:integration" },
    "lifecycle_end_date": { "type": "date",  "required": false },
    "tags":             { "type": "array",   "required": false, "items": "string" },
    "description":      { "type": "string",  "required": true }
  }
}
```

**data_entity_schema.json**
```json
{
  "object_type": "data_entity",
  "version": "1.0",
  "fields": {
    "id":               { "type": "string",  "required": true,  "pattern": "DE-[0-9]{4}" },
    "name":             { "type": "string",  "required": true },
    "status":           { "type": "enum",    "required": true, "values": ["active", "deprecated", "retired"] },
    "owning_application": { "type": "string", "required": true, "items": "ref:application", "comment": "Only one owning application permitted" },
    "data_classification": { "type": "enum", "required": true, "values": ["public", "internal", "confidential", "restricted"] },
    "owner_domain":     { "type": "string",  "required": true }, 
    "description":      { "type": "string",  "required": true },
    "tags":             { "type": "array",   "required": false, "items": "string" }
  }
}
```

**technology_schema.json**
```json
{
  "object_type": "technology",
  "version": "1.0",
  "fields": {
    "id":               { "type": "string",  "required": true,  "pattern": "TECH-[0-9]{4}" },
    "name":             { "type": "string",  "required": true },
    "category":         { "type": "enum",    "required": true, "values": ["language", "framework", "platform", "database", "cloud_service", "protocol", "tool"] },
    "status":           { "type": "enum",    "required": true, "values": ["approved", "conditional", "unapproved", "retired"] },
    "vendor":           { "type": "string",  "required": false }, 
    "version_in_use":   { "type": "string",  "required": false },
    "approved_domains": { "type": "array",   "required": false, "items": "string", "comment": "If empty, approved for all domains" },
    "condition_notes":  { "type": "string",  "required": false, "comment": "Required if status is conditional" },
    "lifecycle_end_date": { "type": "date",  "required": false },
    "description":      { "type": "string",  "required": true }
  }
}
```

**integration_schema.json**
```json
{
  "object_type": "integration",
  "version": "1.0",
  "fields": {
    "id":               { "type": "string",  "required": true,  "pattern": "INT-[0-9]{4}" },
    "name":             { "type": "string",  "required": true },
    "pattern_type":     { "type": "enum",    "required": true, "values": ["sync_api", "async_event", "batch_file", "database_link", "streaming"] },
    "status":           { "type": "enum",    "required": true, "values": ["approved", "conditional", "retired"] },
    "source_app":       { "type": "string",  "required": true,  "items": "ref:application" },
    "target_app":       { "type": "string",  "required": true,  "items": "ref:application" },
    "technology_ref":   { "type": "string",  "required": true,  "items": "ref:technology" },
    "data_entities_exchanged": { "type": "array", "required": false, "items": "ref:data_entity" },
    "description":      { "type": "string",  "required": true }
  }
}
```

**relationship_rules.json**
```json
{
  "relationship_rules": [
    {
      "rule_id": "REL-001",
      "description": "Applications may only integrate with live applications",
      "source_type": "application",
      "relationship": "INTEGRATES_WITH",
      "target_type": "application",
      "constraints": {
        "source_status_allowed": ["proposed", "live"],
        "target_status_allowed": ["live"],
        "blocked_if_target_status": ["retired", "deprecated"]
      }
    },
    {
      "rule_id": "REL-002",
      "description": "A data entity may only have one owning application",
      "source_type": "application",
      "relationship": "OWNS_DATA",
      "target_type": "data_entity",
      "constraints": {
        "max_owners": 1
      }
    },
    {
      "rule_id": "REL-003",
      "description": "Applications may only use approved or conditionally approved technologies",
      "source_type": "application",
      "relationship": "USES_TECHNOLOGY",
      "target_type": "technology",
      "constraints": {
        "target_status_allowed": ["approved", "conditional"],
        "blocked_if_target_status": ["unapproved", "retired"]
      }
    },
    {
      "rule_id": "REL-004",
      "description": "Integrations must use an approved integration pattern",
      "source_type": "integration",
      "relationship": "USES_PATTERN",
      "target_type": "integration",
      "constraints": {
        "source_status_allowed": ["approved", "conditional"],
        "blocked_if_source_status": ["retired"]
      }
    },
    {
      "rule_id": "REL-005",
      "description": "A proposed application must reference at least one approved technology",
      "source_type": "application",
      "relationship": "USES_TECHNOLOGY",
      "target_type": "technology",
      "constraints": {
        "min_approved_refs": 1
      }
    }
  ]
}
```

**ea_meta_schema.json**
```json
{
  "version": "1.0",
  "object_types": [
    { "type": "application",  "schema_file": "application_schema.json",
      "catalogue_file": "ea_catalogue_applications.json",  "id_prefix": "APP" },
    { "type": "data_entity",  "schema_file": "data_entity_schema.json",
      "catalogue_file": "ea_catalogue_data_entities.json", "id_prefix": "DE" },
    { "type": "technology",   "schema_file": "technology_schema.json",
      "catalogue_file": "ea_catalogue_technologies.json",  "id_prefix": "TECH" },
    { "type": "integration",  "schema_file": "integration_schema.json",
      "catalogue_file": "ea_catalogue_integrations.json",  "id_prefix": "INT" }
  ]
}
```

---

## Agent Implementation Detail

### Startup: Schema Loading
At startup, before any agent runs:
- Load ea_meta_schema.json to discover all object types
- Load each object schema file and parse field definitions
- Load relationship_rules.json into memory as a list of rule objects
- Run schema_validator.py against all catalogue files and report any pre-existing catalogue quality issues in the output report
- Pass the relevant schema field list to each agent so prompts are targeted to the correct attributes

### Stage 1: Orchestrator — Document Extraction
Load the schema field definitions first. Then prompt the model to extract from the design document, using the schema fields as the extraction target:
- Named systems, applications, services (map to application schema fields)
- Data entities or data stores (map to data_entity schema fields)
- Technology choices (map to technology schema fields)
- Integration points and data flows (map to integration schema fields)

Return as a structured JSON intermediate representation:
```json
{
  "systems": [
    {
      "name": "Customer Loyalty Platform",
      "description": "...",
      "owner_domain": "Marketing",
      "technology_refs": ["MongoDB", "Python", "Kafka"],
      "integration_refs": ["CRM System", "E-Commerce Platform"],
      "data_entity_refs": ["Loyalty Points Transaction"],
      "status_implied": "proposed"
    }
  ],
  "data_entities": [...],
  "technologies": [...],
  "integrations": [...]
}
```

### Stage 2: Specialist Agents (run in parallel where possible, using asyncio.gather() with the async Anthropic SDK client)
Each specialist agent receives:
  - The extracted entities JSON from Stage 1
  - Only its relevant catalogue file
  - Its object type schema (so it knows required fields and valid values)
  - The relationship_rules relevant to its object type

Each agent performs three tasks:
  1. **Match** — map design entities to catalogue entries, with confidence score (LLM self-estimated, 0.0–1.0)
  2. **Gap detect** — identify design entities with no catalogue entry
  3. **Catalogue quality check** — validate matched entries against their schema, flagging missing required fields or invalid enum values

Each agent returns findings in this schema:
```json
{
  "catalogue_type": "applications",
  "matches": [
    {
      "design_entity": "Customer Portal",
      "catalogue_entry": "APP-0042",
      "confidence": 0.85,
      "match_notes": "Name variant — design uses 'Customer Portal', catalogue has 'CustPortal'"
    }
  ],
  "gaps": [
    {
      "design_entity": "Payment Gateway",
      "issue": "No matching entry found in applications catalogue",
      "severity": "high",
      "draft_catalogue_entry": {
        "id": "APP-PENDING",
        "name": "Payment Gateway",
        "status": "proposed",
        "owner_domain": "REQUIRED - TO BE CONFIRMED",
        "technology_refs": ["REQUIRED - TO BE CONFIRMED"],
        "description": "REQUIRED - TO BE CONFIRMED"
      }
    }
  ],
  "conflicts": [
    {
      "design_entity": "Legacy CRM",
      "catalogue_entry": "APP-0019",
      "issue": "Catalogue status is RETIRED. Design proposes new integration.",
      "severity": "high",
      "violated_rule": "REL-001"
    }
  ],
  "catalogue_quality_issues": [
    {
      "catalogue_entry": "APP-0031",
      "issue": "Missing required field: description",
      "severity": "medium",
      "schema_rule": "application_schema.json — description: required"
    }
  ]
}
```

Severity levels: "high", "medium", "low"
Confidence scores: 0.0 to 1.0

### Stage 3: Consistency Checker Agent
This stage runs in two passes:

**Pass 1 — Programmatic rule checks (no LLM)**
Iterate over all matched entities and run each relationship_rule programmatically against the entity graph. This is deterministic code, not an LLM prompt. For each rule violation, create a finding with the rule_id, the entities involved, and the specific constraint breached.

**Pass 2 — LLM reasoning pass**
Pass all specialist findings plus programmatic rule violations to the LLM for deeper cross-catalogue reasoning. The LLM checks for:
- Data entity ownership conflicts across domain boundaries
- Circular dependencies introduced by the design
- Patterns not covered by explicit rules that represent EA anti-patterns

Returns findings in the same schema as Stage 2 with catalogue_type: "cross-catalogue", including violated_rule where applicable.

### Stage 4: Options Generator Agent
For each finding (gap, conflict, cross-catalogue issue, or catalogue quality
issue), generate tiered options. Where a specialist agent already produced a
`draft_catalogue_entry` in Stage 2, the Options Generator should refine that
draft (adding rationale, effort, risk) rather than regenerating it from scratch.

Option types:
  - CONFORM: Change the design to match the existing EA model
  - EXTEND: Add new entries to EA model. Include a draft catalogue entry that is valid against the relevant schema, with unknown fields marked "REQUIRED - TO BE CONFIRMED"
  - EXCEPTION: Document a governed deviation with rationale
  - RETIRE: Trigger review of an outdated EA catalogue entry

Each option must include:
  - option_type
  - description (specific action to take)
  - effort_estimate ("low", "medium", "high")
  - risk_level ("low", "medium", "high")
  - rationale
  - draft_catalogue_entry (only for EXTEND options, schema-valid JSON)

---

## Utilities

### schema_validator.py
A standalone utility that:
- Accepts a catalogue file path and its schema file path as arguments
- Validates every entry in the catalogue against the schema
- Reports: missing required fields, invalid enum values, malformed ID patterns, broken cross-object references (ref: fields pointing to   non-existent IDs in the corresponding catalogue)
- Can be run independently: python schema_validator.py --catalogue ea_catalogue_applications.json --schema application_schema.json
- Returns a structured validation report and exit code 0 (pass) or 1 (fail)

---

## Output Format
Generate two output files:

### 1. ea_impact_assessment_report.md
Sections:
  - Executive Summary
    - Overall RAG status (Red/Amber/Green)
    - Finding counts by type and severity
    - Pre-existing catalogue quality issues found at startup
  - Design Document Summary (extracted entities with schema field mapping)
  - Findings by Catalogue Domain
    - Matches (with confidence scores)
    - Gaps (with draft catalogue entries)
    - Conflicts (with rule references e.g. "Violates REL-001")
    - Catalogue Quality Issues
  - Cross-Catalogue Consistency Issues
    - Programmatic rule violations (listed with rule ID and entities)
    - LLM-identified issues
  - Recommended Options (grouped by finding)
    - Each option labelled CONFORM / EXTEND / EXCEPTION / RETIRE
    - EXTEND options include the draft schema-valid catalogue entry
  - Appendix A: Full entity match table with confidence scores
  - Appendix B: Schema validation results for all catalogue files

### 2. ea_impact_findings.json
Complete machine-readable output including all intermediate agent outputs,
schema validation results, relationship rule check results, and all draft
catalogue entries. Structured for future integration with EA tooling.

---

## Code Structure

ea_impact_agent/
main.py                        # CLI entry point
agents/
orchestrator.py              # Schema-aware document extraction + coordination
specialist.py                # Reusable specialist agent (parameterised by type)
consistency.py               # Programmatic rule checks + LLM cross-catalogue
options_generator.py         # Remediation options with draft catalogue entries
utils/
file_loader.py               # Design doc + catalogue + schema file ingestion
schema_loader.py             # Loads and parses EA schema files at startup
schema_validator.py          # Standalone catalogue validation utility
report_builder.py            # Markdown report assembly
models.py                    # Pydantic models for all intermediate data
schemas/
ea_meta_schema.json
application_schema.json
data_entity_schema.json
technology_schema.json
integration_schema.json
relationship_rules.json
sample_data/
sample_design_doc.md
ea_catalogue_applications.json
ea_catalogue_data_entities.json
ea_catalogue_technologies.json
ea_catalogue_integrations.json


---

## Sample Data Requirements
Create realistic sample data for a fictional retail company ("RetailCo").

**Design document:** A proposal for a new "Customer Loyalty Platform" that:
  - Integrates with an existing CRM and e-commerce platform (matched in catalogue)
  - Introduces a new data entity for loyalty points transactions (gap — not in catalogue)
  - Uses MongoDB, which is not in the approved technology catalogue (REL-003 violation)
  - References a system marked RETIRED in the catalogue (REL-001 violation)
  - Proposes a database_link integration pattern where only async_event is
    approved for that domain (REL-004 violation)
  - Includes one fully compliant component as a control case
  - Implies data entity ownership across two domain boundaries (cross-catalogue issue)

**EA Catalogues:** ~10-15 entries per catalogue with varied statuses including:
  - Applications: mix of live, deprecated, retired, proposed
  - Technologies: mix of approved, conditional, unapproved, retired
  - At least one catalogue entry with a deliberately missing required field
    (to exercise catalogue_quality_issue finding type)
  - Enough cross-references between catalogues to make relationship
    rule checking meaningful

---

## Error Handling
- If a schema file is missing, warn and skip validation for that object type;
  do not abort the run
- If a catalogue file is missing, warn but continue with available catalogues
- If the design document cannot be parsed, exit with a clear error message
- If an agent call fails, retry once then mark that finding as "agent-error"
  and continue
- If schema validation finds errors in catalogue files, report them in the
  Executive Summary as pre-existing issues but continue the assessment
- All API calls should have a timeout of 60 seconds

## API Key
Read the Anthropic API key from environment variable ANTHROPIC_API_KEY.
Do not hardcode keys. Include a .env.example file.

## Dependencies

anthropic
pydantic
pypdf
python-dotenv
asyncio (stdlib)
jsonschema

## README
Include a README.md with:
  - Setup instructions
  - How to run with the sample data
  - How to run schema_validator.py standalone
  - How to bring your own catalogue and schema files (format guide)
  - Description of all output files
  - How to extend the tool with a new catalogue type
  - Known limitations of the PoC vs production approach

## Definition of Done
The PoC is complete when:
  - Schema files load and validate correctly at startup
  - Running against sample data produces a coherent impact report
  - All 4 agent stages complete without errors
  - Programmatic relationship rule checks fire correctly for REL-001,
    REL-002, REL-003 and REL-004 violations in the sample data
  - At least one EXTEND option includes a schema-valid draft catalogue entry
  - The catalogue quality issue from the deliberately incomplete entry is
    reported in the Executive Summary
  - schema_validator.py runs standalone and correctly identifies the
    deliberate schema error in sample data
  - The JSON output is valid and matches the defined Pydantic schemas