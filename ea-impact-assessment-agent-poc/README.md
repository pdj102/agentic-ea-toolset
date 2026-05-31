# EA Impact Assessment Agent — PoC

A multi-agent tool that takes a design document and EA catalogue files, validates them against
EA object schemas, assesses consistency, and recommends structured alignment options.

## Setup

**Requirements:** Python 3.11+

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=your-key-here
```

## Running Against Sample Data

From the project root:

```bash
python -m ea_impact_agent.main \
  --design-doc ea_impact_agent/sample_data/sample_design_doc.md \
  --catalogue-dir ea_impact_agent/sample_data \
  --schema-dir ea_impact_agent/schemas \
  --output-dir output
```

Output files will be written to `output/`:
- `ea_impact_assessment_report.md` — human-readable markdown report
- `ea_impact_findings.json` — full machine-readable findings

## Running the Schema Validator Standalone

Validate a single catalogue file against its schema:

```bash
python -m ea_impact_agent.utils.schema_validator \
  --catalogue ea_impact_agent/sample_data/ea_catalogue_applications.json \
  --schema ea_impact_agent/schemas/application_schema.json \
  --catalogue-dir ea_impact_agent/sample_data
```

Exit code `0` = clean. Exit code `1` = validation errors found.

The `--catalogue-dir` argument is optional but enables cross-object reference checks
(e.g. verifying that `technology_refs` point to real entries in the technology catalogue).

## CLI Arguments

| Argument | Description | Required |
|---|---|---|
| `--design-doc` | Path to design document (`.pdf` or `.md`) | Yes |
| `--catalogue-dir` | Directory containing catalogue JSON files | Yes |
| `--schema-dir` | Directory containing EA schema JSON files | Yes |
| `--output-dir` | Output directory for report files (default: `./output`) | No |

## Bringing Your Own Catalogues and Schemas

The tool is driven by `ea_meta_schema.json` which registers all EA object types.
To add your own data:

**Catalogue files** must be JSON arrays of objects, named as registered in `ea_meta_schema.json`.
Default names:
- `ea_catalogue_applications.json`
- `ea_catalogue_data_entities.json`
- `ea_catalogue_technologies.json`
- `ea_catalogue_integrations.json`

**Schema files** define the field structure for each object type. See `ea_impact_agent/schemas/`
for examples. Fields support types `string`, `enum`, `array`, `date`. Use `"required": true` to
enforce required fields. Use `"items": "ref:technology"` to declare cross-object references.

## Output Files

### `ea_impact_assessment_report.md`
A human-readable markdown report containing:
- **Executive Summary** — RAG status, finding counts, pre-existing catalogue issues
- **Design Document Summary** — extracted entities mapped to schema fields
- **Findings by Catalogue Domain** — matches, gaps, conflicts, quality issues per domain
- **Cross-Catalogue Consistency Issues** — programmatic rule violations and LLM-identified issues
- **Recommended Options** — CONFORM/EXTEND/EXCEPTION/RETIRE options per finding
- **Appendix A** — full entity match table with confidence scores
- **Appendix B** — schema validation results for all catalogue files

### `ea_impact_findings.json`
Full machine-readable output in Pydantic-serialised JSON including all intermediate agent
outputs, validation results, rule check results, and draft catalogue entries.

## Extending With a New Catalogue Type

1. Create a new schema file in `ea_impact_agent/schemas/`, e.g. `capability_schema.json`
2. Add an entry to `ea_meta_schema.json` registering the new type, schema file, and catalogue file
3. Create the corresponding catalogue file (e.g. `ea_catalogue_capabilities.json`)
4. The tool will automatically pick up the new type at startup — no code changes required

The specialist agent (`agents/specialist.py`) is parameterised by catalogue type and will
handle the new type generically. To teach it domain-specific matching logic, add relevant
entries to `relationship_rules.json`.

## Known PoC Limitations

- **No vector search:** Entity matching uses LLM reasoning over the full catalogue passed in
  context. For catalogues with hundreds of entries, performance and cost will degrade — a
  production version would use embedding-based similarity search.

- **Context window constraints:** All catalogue files are passed directly to each specialist
  agent. Very large catalogues may exceed the model's context window.

- **PDF support is best-effort:** PDF text extraction with `pypdf` works well for text-based
  PDFs but will produce poor results for scanned documents or heavily formatted files.
  Use Markdown design documents where possible.

- **LLM confidence scores are self-estimated:** Match confidence (0.0–1.0) is self-reported
  by the model and is not computed algorithmically. Treat it as a rough guide.

- **Sequential findings for options:** Stage 4 generates options per finding independently.
  It does not reason across multiple findings holistically (e.g. it won't notice that two
  EXTEND options could be combined).

- **No authentication/authorisation:** The tool runs with whatever permissions the filesystem
  allows. Do not point it at sensitive catalogues without appropriate access controls.
