import datetime
import functools
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any
import jsonschema
import requests
import os


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


GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


repo_info_query = """
query ($name: String!, $owner: String!) {
  repository(name: $name, owner: $owner) {
    stargazerCount
    pushedAt
  }
}
"""


@functools.lru_cache(maxsize=None)
def fetch_github_repo_info(username: str, reponame: str) -> dict[str, any]:
    """Fetch repository info from GitHub API."""
    github_graphql_url = "https://api.github.com/graphql"
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable is not set")
        sys.exit(1)
    try:
        variables = {
            "name": reponame,
            "owner": username
        }
        response = requests.post(github_graphql_url, json={'query': repo_info_query, 'variables': variables}, headers={
            "Authorization": f"Token {GITHUB_TOKEN}", "X-REQUEST-TYPE": "graphql"})
        if response.status_code == 403:
            print(f"Error: GitHub API rate limit exceeded")
            sys.exit(1)
        response.raise_for_status()
        response_json = response.json()
        if 'errors' in response_json:
            error_messages = [error['message']
                              for error in response_json['errors']]
            print(f"Error fetching GitHub data: {', '.join(error_messages)}")
            sys.exit(1)
        return response_json.get('data', {}).get('repository', {})
    except requests.RequestException as e:
        print(f"Error fetching GitHub data: {e}")
        raise e


def update_json_content(data: Dict[str, Any]) -> bool:
    """Update the stars and edit time as needed."""
    changed = False

    github_pattern = r'''
        ^                           # Start of string
        https://github\.com/        # GitHub domain
        ([\w-]+)/                   # Username/organization (captured group 1)
        ([\w-]+)                    # Repository name (captured group 2)
        (?:                         # Optional path group (non-capturing)
            /(?:tree|blob)/         # Either /tree/ or /blob/
            (?:[^/]+)/              # Branch/tag name (any characters except /)
            .*                      # Any remaining path
        )?                          # Path group is optional
        /?                          # Optional trailing slash
        (?:\#.*)?                   # Optional fragment (anchor)
        $                           # End of string
    '''

    link = data.get('link', '')
    match = re.match(github_pattern, link, re.VERBOSE)
    if not match:
        print(f"Link does not match expected GitHub format: {link}")
        raise ValueError("Link does not match expected GitHub format")
    username = match.group(1)
    reponame = match.group(2)
    try:
        repo_info = fetch_github_repo_info(username, reponame)
        stars = repo_info.get('stargazerCount', 0)
        updated_at_iso = repo_info.get('pushedAt', '')  # ISO 8601 format
        updated_at_timestamp = int(
            datetime.datetime.fromisoformat(updated_at_iso).timestamp())

        if data.get('stars') != stars:
            data['stars'] = stars
            changed = True

        if data.get('last_updated') != updated_at_timestamp:
            data['last_updated'] = updated_at_timestamp
            changed = True
    except requests.RequestException as e:
        print(f"Error fetching GitHub data: {e}")
        raise e
    return changed


def load_and_update_json(file_path: Path, schema: Dict[str, Any]):
    """Load a JSON file and validate it against the schema."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate against schema
        jsonschema.validate(data, schema)
        changed = update_json_content(data)
        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent='\t')
            print(f"✓ Updated: {file_path}")
        else:
            print(f"✓ No changes needed: {file_path}")
        return changed

    except FileNotFoundError:
        print(f"✗ Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in {file_path}: {e}")
        return None
    except jsonschema.ValidationError as e:
        print(
            f"✗ Error: Schema validation failed for {file_path}: {e.message}")
        return None
    except Exception as e:
        print(f"✗ Error: Unexpected error processing {file_path}: {e}")
        return None


def update_plugins() -> None:
    """Main function to update all plugin JSON files."""
    # Paths
    schema_path = "./.ci/plugin-schema.json"
    plugins_dir = "./plugins"

    # Load schema
    print("Loading schema...")
    schema = load_schema(schema_path)

    # Find all JSON files
    print("Finding JSON files...")
    json_files = find_json_files(plugins_dir)

    if not json_files:
        print("No JSON files found in plugins directory")
        sys.exit(1)

    # Load and update all JSON files
    print("Loading and updating JSON files...")
    updated_count = 0
    for file_path in json_files:
        result = load_and_update_json(file_path, schema)
        if result is not None:
            updated_count += 1

    print(
        f"Finished updating. Processed {len(json_files)} files, updated {updated_count} files.")


if __name__ == "__main__":
    update_plugins()
