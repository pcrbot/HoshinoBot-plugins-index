import re
import json
import toml
import sys
import jsonschema
from jsonschema import validate
import os
import hashlib


def extract_toml_from_file(file_path):
    """Extract TOML content from markdown code blocks in the file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Find TOML code block using regex
        pattern = r'```toml\n(.*?)\n```'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return match.group(1)
        else:
            print("No TOML code block found in the file")
            return None

    except FileNotFoundError:
        print(f"File {file_path} not found")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def parse_toml_to_json(toml_content):
    """Parse TOML content and convert to JSON."""
    try:
        # Parse TOML content
        parsed_data = toml.loads(toml_content)

        # Convert to JSON string
        json_content = json.dumps(parsed_data, indent='\t', ensure_ascii=False)

        return json_content, parsed_data

    except Exception as e:
        print(f"Error parsing TOML: {e}")
        return None, None


def load_schema(schema_path):
    """Load JSON schema from file."""
    try:
        with open(schema_path, 'r', encoding='utf-8') as file:
            schema = json.load(file)
        return schema
    except FileNotFoundError:
        print(f"Schema file {schema_path} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing schema JSON: {e}")
        return None
    except Exception as e:
        print(f"Error loading schema: {e}")
        return None


def validate_json_schema(data, schema):
    """Validate JSON data against schema."""
    try:
        validate(instance=data, schema=schema)
        print("JSON validation passed")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"JSON validation failed: {e.message}")
        return False
    except Exception as e:
        print(f"Error during validation: {e}")
        return False


def get_output_path(parsed_data):
    """Determine output path based on link format."""
    link = parsed_data.get('link', '')

    # Check if link matches GitHub format (basic repo)
    github_pattern = r'''
        ^                           # Start of string
        https://github\.com         # GitHub domain
        /([\w-]+)                   # Username/organization (captured group 1)
        /([\w-]+)                   # Repository name (captured group 2)
        /?                          # Optional ending slash
        $                           # End of string
    '''
    match = re.match(github_pattern, link, re.VERBOSE)

    if match:
        username = match.group(1)
        reponame = match.group(2)
        output_dir = f'./plugins/{username}'
        output_file = f'{output_dir}/{reponame}.json'
    else:
        # Check if link matches GitHub format with deeper path
        github_deep_pattern = r'''
            ^                           # Start of string
            https://github\.com         # GitHub domain
            /([\w-]+)                   # Username/organization (captured group 1)
            /([\w-]+)                   # Repository name (captured group 2)
            (?:
                /(?:tree|blob)          # Either /tree/ or /blob/
                /.*                     # Any remaining path
                |                       # Or
                /?\#.*                  # Fragment
            )
            $
        '''
        deep_match = re.match(github_deep_pattern, link, re.VERBOSE)

        if deep_match:
            username = deep_match.group(1)
            reponame = deep_match.group(2)
            # Generate SHA256 hash of the full link
            hash_value = hashlib.sha256(link.encode('utf-8')).hexdigest()
            output_dir = f'./plugins/{username}/{reponame}'
            output_file = f'{output_dir}/{hash_value}.json'
        else:
            # Generate SHA256 hash of the link for non-GitHub links
            hash_value = hashlib.sha256(link.encode('utf-8')).hexdigest()
            output_dir = './plugins/others'
            output_file = f'{output_dir}/{hash_value}.json'

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    return output_file


def save_json_file(json_content, output_path):
    """Save JSON content to file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(json_content)
        print(f"JSON saved to {output_path}")
        return True

    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return False


def main():
    # File paths
    input_file = sys.argv[1]
    if not input_file:
        print("Input file path is required")
        sys.exit(1)
    schema_file = '.ci/plugin-schema.json'

    # Extract TOML content from pr.txt
    toml_content = extract_toml_from_file(input_file)

    if toml_content:
        print("TOML content extracted:")
        print(toml_content)
        print("-" * 50)

        # Parse TOML and convert to JSON
        json_content, parsed_data = parse_toml_to_json(toml_content)

        if json_content:
            print("Parsed JSON:")
            print(json_content)

            # Load and validate schema
            schema = load_schema(schema_file)
            if schema is None:
                sys.exit(1)

            if not validate_json_schema(parsed_data, schema):
                print("Format Validation failed")
                sys.exit(1)

            # Determine output path based on link format
            output_file = get_output_path(parsed_data)
            print(f"Output file: {output_file}")

            # Save to JSON file
            if not save_json_file(json_content, output_file):
                sys.exit(1)
        else:
            print("Failed to parse TOML content")
            sys.exit(1)
    else:
        print("No TOML content found to process")
        sys.exit(1)


if __name__ == "__main__":
    main()
