"""Waliduje pliki z examples/ względem schemas/. Uruchom z korzenia repo:

    pip install jsonschema
    python reference/validate_examples.py

Kod wyjścia 0 = wszystkie przykłady poprawne. Ten sam mechanizm ma służyć do walidacji
plików generowanych przez potok (M3): dołącz je do listy PAIRS albo wywołaj validate().
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ("ranking.schema.json", "ranking.example.json"),
    ("city_summary.schema.json", "city_summary.example.json"),
    ("segment_feature.schema.json", "segment_feature.example.json"),
    ("edition_manifest.schema.json", "edition_manifest.example.json"),
]


def validate(schema_path: Path, instance_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    instance = json.loads(instance_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in validator.iter_errors(instance)]


def main() -> int:
    failed = 0
    for schema_name, example_name in PAIRS:
        errors = validate(ROOT / "schemas" / schema_name, ROOT / "examples" / example_name)
        status = "OK  " if not errors else "FAIL"
        print(f"{status} {example_name}")
        for message in errors:
            print(f"     {message}")
        failed += bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
