import json
import warnings
from pathlib import Path


def load_design_doc(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".md":
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ImportError("pypdf is required to read PDF files: pip install pypdf") from exc
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    raise ValueError(f"Unsupported design document format: {suffix}. Use .md or .pdf.")


def load_catalogue(catalogue_dir: Path, filename: str) -> list[dict] | None:
    path = catalogue_dir / filename
    if not path.exists():
        warnings.warn(f"Catalogue file not found: {path}. Skipping this catalogue type.")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_all_catalogues(catalogue_dir: Path, meta_schema: dict) -> dict[str, list[dict]]:
    catalogues: dict[str, list[dict]] = {}
    for obj_type in meta_schema.get("object_types", []):
        type_name = obj_type["type"]
        filename = obj_type["catalogue_file"]
        data = load_catalogue(catalogue_dir, filename)
        if data is not None:
            catalogues[type_name] = data
    return catalogues
