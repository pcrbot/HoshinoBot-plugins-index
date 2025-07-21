#!/usr/bin/env python3
"""
Aggregate all plugin JSON files from ./plugins directory,
validate them against the schema, and save to ./plugins.json
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import jsonschema


def load_schema(schema_path: str) -> Dict[str, Any]:
    """Load the JSON schema from file."""
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file not found: {schema_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file: {e}")
        sys.exit(1)


def find_json_files(plugins_dir: str) -> List[Path]:
    """Recursively find all JSON files in the plugins directory."""
    plugins_path = Path(plugins_dir)
    if not plugins_path.exists():
        print(f"Error: Plugins directory not found: {plugins_dir}")
        sys.exit(1)

    json_files = list(plugins_path.rglob("*.json"))
    print(f"Found {len(json_files)} JSON files in {plugins_dir}")
    return json_files


def load_and_validate_json(file_path: Path, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Load a JSON file and validate it against the schema."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate against schema
        jsonschema.validate(data, schema)
        print(f"✓ Valid: {file_path}")
        return data

    except FileNotFoundError:
        print(f"✗ Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"::warning file={file_path}::Invalid JSON")
        print(f"✗ Error: Invalid JSON in {file_path}: {e}")
        return None
    except jsonschema.ValidationError as e:
        print(f"::warning file={file_path}::Schema validation failed")
        print(
            f"✗ Error: Schema validation failed for {file_path}: {e.message}")
        return None
    except Exception as e:
        print(f"✗ Error: Unexpected error processing {file_path}: {e}")
        return None


def aggregate_plugins() -> None:
    """Main function to aggregate all plugin JSON files."""
    # Paths
    schema_path = "./.ci/plugin-schema.json"
    plugins_dir = "./plugins"
    output_path = "./plugins.json"

    # Load schema
    print("Loading schema...")
    schema = load_schema(schema_path)

    # Find all JSON files
    print("Finding JSON files...")
    json_files = find_json_files(plugins_dir)

    if not json_files:
        print("No JSON files found in plugins directory")
        sys.exit(1)

    # Load and validate all JSON files
    print("Loading and validating JSON files...")
    plugins = []
    valid_count = 0
    invalid_count = 0

    for file_path in json_files:
        plugin_data = load_and_validate_json(file_path, schema)
        if plugin_data is not None:
            plugins.append(plugin_data)
            valid_count += 1
        else:
            invalid_count += 1

    print(f"\nValidation summary:")
    print(f"Valid files: {valid_count}")
    print(f"Invalid files: {invalid_count}")
    print(f"Total files: {len(json_files)}")

    if invalid_count > 0:
        print(f"Warning: {invalid_count} files failed validation")

    # Save aggregated data
    print(f"Saving {len(plugins)} plugins to {output_path}...")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(plugins, f, ensure_ascii=False, separators=(',', ':'))
        print(f"✓ Successfully saved {len(plugins)} plugins to {output_path}")
    except Exception as e:
        print(f"✗ Error: Failed to save output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    aggregate_plugins()
