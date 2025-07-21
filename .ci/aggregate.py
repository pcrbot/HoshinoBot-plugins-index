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
import datetime


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


def print_markdown_table_line(plugin: Dict[str, Any]) -> str:
    authors = plugin.get('authors')
    author_str = ' '.join(
        [f"[{author.get('name')}]({author.get('link')})" for author in authors]
    )
    description = plugin.get('description', '')
    description = description.replace('\n', '<br/>')
    last_updated = plugin.get('last_updated', 0)  # timestamp
    if last_updated > 0:
        last_updated = datetime.datetime.fromtimestamp(
            last_updated).strftime('%Y/%m/%d')
    else:
        last_updated = ''
    return f"| [{plugin.get('name')}]({plugin.get('link')}) | {author_str} | {description} | {plugin.get('stars', 0)} | {last_updated} |"


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
    # Save markdown table
    plugins = sorted(plugins, key=lambda x: x.get('last_updated', 0), reverse=True)
    markdown_output_path = "./README.md"
    markdown_output_start = "<!-- legacy_start -->"
    markdown_output_end = "<!-- legacy_end -->"
    markdown_lines = ["| 名称 | 作者 | 备注 | 收藏 | 最后更新 |",
                      "| --- | --- | --- | --- | --- |"]
    for plugin in plugins:
        markdown_lines.append(print_markdown_table_line(plugin))
    print(f"Inserting markdown table to {markdown_output_path}...")
    try:
        with open(markdown_output_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        # Find the marker positions
        start_marker_pos = readme_content.find(markdown_output_start)
        end_marker_pos = readme_content.find(markdown_output_end)

        if start_marker_pos == -1 or end_marker_pos == -1:
            print(
                f"Error: Markers not found in {markdown_output_path}")
            sys.exit(1)
        else:
            # Replace content between markers
            new_content = (
                readme_content[:start_marker_pos + len(markdown_output_start)] +
                "\n" + "\n".join(markdown_lines) + "\n" +
                readme_content[end_marker_pos:]
            )
            with open(markdown_output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        print(f"✓ Successfully saved markdown table to {markdown_output_path}")
    except Exception as e:
        print(f"✗ Error: Failed to save markdown file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    aggregate_plugins()
