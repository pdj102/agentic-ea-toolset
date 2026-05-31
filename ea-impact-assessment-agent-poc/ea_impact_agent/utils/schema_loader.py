import json
import warnings
from pathlib import Path


def load_meta_schema(schema_dir: Path) -> dict:
    path = schema_dir / "ea_meta_schema.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_all_schemas(schema_dir: Path) -> dict[str, dict]:
    meta = load_meta_schema(schema_dir)
    schemas: dict[str, dict] = {}
    for obj_type in meta.get("object_types", []):
        type_name = obj_type["type"]
        schema_file = schema_dir / obj_type["schema_file"]
        if not schema_file.exists():
            warnings.warn(f"Schema file missing for '{type_name}': {schema_file}. Skipping.")
            continue
        with open(schema_file, encoding="utf-8") as f:
            schemas[type_name] = json.load(f)
    return schemas


def load_relationship_rules(schema_dir: Path) -> list[dict]:
    path = schema_dir / "relationship_rules.json"
    if not path.exists():
        warnings.warn(f"relationship_rules.json not found in {schema_dir}. No rules loaded.")
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("relationship_rules", [])


def get_rules_for_type(rules: list[dict], object_type: str) -> list[dict]:
    return [r for r in rules if r.get("source_type") == object_type or r.get("target_type") == object_type]
