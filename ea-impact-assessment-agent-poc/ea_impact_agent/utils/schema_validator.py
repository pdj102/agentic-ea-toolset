"""
Standalone catalogue validator and importable module.

CLI usage:
    python schema_validator.py --catalogue path/to/catalogue.json \
                               --schema path/to/schema.json \
                               [--catalogue-dir path/to/catalogues/]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from ea_impact_agent.utils.models import CatalogueValidationResult, ValidationError


def validate_catalogue(
    catalogue: list[dict],
    schema: dict,
    all_catalogues: dict[str, list[dict]] | None = None,
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    fields = schema.get("fields", {})
    all_catalogues = all_catalogues or {}

    for entry in catalogue:
        entry_id = entry.get("id", "<no-id>")

        for field_name, field_def in fields.items():
            required = field_def.get("required", False)
            value = entry.get(field_name)

            if required and (value is None or value == "" or value == []):
                errors.append(ValidationError(
                    catalogue_entry_id=entry_id,
                    field=field_name,
                    issue=f"Missing required field: {field_name}",
                    severity="high",
                ))
                continue

            if value is None:
                continue

            field_type = field_def.get("type")

            if field_type == "enum":
                allowed = field_def.get("values", [])
                if value not in allowed:
                    errors.append(ValidationError(
                        catalogue_entry_id=entry_id,
                        field=field_name,
                        issue=f"Invalid enum value '{value}'. Allowed: {allowed}",
                        severity="high",
                    ))

            if field_type == "string" and "pattern" in field_def:
                pattern = field_def["pattern"]
                if not re.fullmatch(pattern, str(value)):
                    errors.append(ValidationError(
                        catalogue_entry_id=entry_id,
                        field=field_name,
                        issue=f"ID '{value}' does not match required pattern '{pattern}'",
                        severity="high",
                    ))

            if field_type == "array" and isinstance(value, list):
                items_type = field_def.get("items", "")
                min_items = field_def.get("min_items", 0)
                if len(value) < min_items:
                    errors.append(ValidationError(
                        catalogue_entry_id=entry_id,
                        field=field_name,
                        issue=f"Array has {len(value)} items but requires at least {min_items}",
                        severity="medium",
                    ))
                if items_type.startswith("ref:"):
                    ref_type = items_type[4:]
                    ref_catalogue = all_catalogues.get(ref_type, [])
                    ref_ids = {e.get("id") for e in ref_catalogue}
                    for ref_val in value:
                        if ref_val not in ref_ids:
                            errors.append(ValidationError(
                                catalogue_entry_id=entry_id,
                                field=field_name,
                                issue=f"Broken reference: '{ref_val}' not found in {ref_type} catalogue",
                                severity="medium",
                            ))

            if field_type == "string" and field_def.get("items", "").startswith("ref:"):
                ref_type = field_def["items"][4:]
                ref_catalogue = all_catalogues.get(ref_type, [])
                ref_ids = {e.get("id") for e in ref_catalogue}
                if value not in ref_ids:
                    errors.append(ValidationError(
                        catalogue_entry_id=entry_id,
                        field=field_name,
                        issue=f"Broken reference: '{value}' not found in {ref_type} catalogue",
                        severity="medium",
                    ))

    return errors


def validate_all_catalogues(
    catalogues: dict[str, list[dict]],
    schemas: dict[str, dict],
    meta_schema: dict,
) -> list[CatalogueValidationResult]:
    results: list[CatalogueValidationResult] = []
    for obj_type_info in meta_schema.get("object_types", []):
        type_name = obj_type_info["type"]
        catalogue_file = obj_type_info["catalogue_file"]
        catalogue = catalogues.get(type_name)
        schema = schemas.get(type_name)
        if catalogue is None or schema is None:
            continue
        errors = validate_catalogue(catalogue, schema, catalogues)
        results.append(CatalogueValidationResult(
            catalogue_type=type_name,
            catalogue_file=catalogue_file,
            errors=errors,
            entry_count=len(catalogue),
            error_count=len(errors),
        ))
    return results


def _main() -> None:
    parser = argparse.ArgumentParser(description="Validate an EA catalogue file against its schema.")
    parser.add_argument("--catalogue", required=True, help="Path to catalogue JSON file")
    parser.add_argument("--schema", required=True, help="Path to schema JSON file")
    parser.add_argument("--catalogue-dir", default=None, help="Directory containing all catalogue files for ref checks")
    args = parser.parse_args()

    catalogue_path = Path(args.catalogue)
    schema_path = Path(args.schema)

    with open(catalogue_path, encoding="utf-8") as f:
        catalogue = json.load(f)
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    all_catalogues: dict[str, list[dict]] = {}
    if args.catalogue_dir:
        catalogue_dir = Path(args.catalogue_dir)
        for json_file in catalogue_dir.glob("ea_catalogue_*.json"):
            type_name = json_file.stem.replace("ea_catalogue_", "")
            with open(json_file, encoding="utf-8") as f:
                all_catalogues[type_name] = json.load(f)

    errors = validate_catalogue(catalogue, schema, all_catalogues)

    if not errors:
        print(f"✓ {catalogue_path.name}: No validation errors found ({len(catalogue)} entries checked).")
        sys.exit(0)
    else:
        print(f"✗ {catalogue_path.name}: {len(errors)} validation error(s) found:\n")
        for err in errors:
            print(f"  [{err.severity.upper()}] {err.catalogue_entry_id} — {err.field}: {err.issue}")
        sys.exit(1)


if __name__ == "__main__":
    _main()
