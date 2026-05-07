import json
import sys
from jsonschema import validate, ValidationError

SCHEMA_PATH = "schema/ods_decision_v1.json"


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validator/validate.py <file.json>")
        sys.exit(1)

    target_file = sys.argv[1]

    schema = load_json(SCHEMA_PATH)
    data = load_json(target_file)

    try:
        validate(instance=data, schema=schema)
        print("✓ ODS VALID: compliant with schema v1.0")
        sys.exit(0)
    except ValidationError as e:
        print("✗ ODS INVALID")
        print(f"Reason: {e.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()

