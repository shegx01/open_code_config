#!/usr/bin/env python3
"""
OpenCode GitHub Workflow Generator

This script generates a GitHub workflow for OpenCode by reading configuration
from a config.toml file and substituting values into the workflow template.

Usage:
    python generate_workflow.py [--config CONFIG_FILE] [--output OUTPUT_FILE]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

# Try to import tomllib (Python 3.11+), fallback to tomli for older versions
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("📦 TOML parsing library not found. Installing tomli...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "tomli"])
            import tomli as tomllib
            print("✅ Successfully installed tomli")
        except Exception as e:
            print(f"❌ Error: Failed to install tomli automatically: {e}", file=sys.stderr)
            print("Please install manually: pip install tomli", file=sys.stderr)
            sys.exit(1)


class WorkflowGenerator:
    """Generates OpenCode GitHub workflows from configuration files."""

    def __init__(self, config_file: str = "config.toml"):
        """Initialize the generator with a configuration file."""
        self.config_file = Path(config_file)
        self.config = {}

    def parse_toml(self) -> Dict[str, str]:
        """Parse the config.toml file and return a flattened dictionary of key-value pairs."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        try:
            with open(self.config_file, 'rb') as file:
                toml_data = tomllib.load(file)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML format in {self.config_file}: {e}")

        # Flatten the TOML structure for easier access
        config = {}
        
        def flatten_dict(data, prefix=""):
            for key, value in data.items():
                if isinstance(value, dict):
                    flatten_dict(value, f"{prefix}{key}.")
                else:
                    config[f"{prefix}{key}"] = str(value)
        
        flatten_dict(toml_data)
        
        self.config = config
        return config

    def get_workflow_template(self) -> str:
        """Return the GitHub workflow template with placeholders."""
        return """name: opencode

on:
  issue_comment:
    types: [created]

jobs:
  opencode:
    if: |
      (contains(github.event.comment.body, '/oc') ||
       contains(github.event.comment.body, '/opencode')) &&
      (github.event.comment.author_association == 'OWNER' ||
       github.event.comment.author_association == 'MEMBER')
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: write
      pull-requests: write
      issues: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Run opencode
        uses: sst/opencode/github@latest
        env:
          {env_key}: ${{{{ secrets.{env_key} }}}}
        with:
          model: {model}
"""

    def validate_config(self) -> None:
        """Validate that required configuration keys are present and valid."""
        errors = []
        warnings = []

        # Check for required keys (though we have defaults, warn if missing)
        if 'gh.workflow.env_key' not in self.config:
            warnings.append("Missing 'gh.workflow.env_key' - using default: ANTHROPIC_API_KEY")

        if 'gh.workflow.model' not in self.config:
            warnings.append("Missing 'gh.workflow.model' - using default: anthropic/claude-sonnet-4-20250514")

        # Validate model format if present
        if 'gh.workflow.model' in self.config:
            model = self.config['gh.workflow.model']
            if '/' not in model:
                errors.append(f"Invalid model format '{model}' - expected format: provider/model (e.g., 'anthropic/claude-sonnet-4-20250514')")

        # Validate env_key format if present
        if 'gh.workflow.env_key' in self.config:
            env_key = self.config['gh.workflow.env_key']
            if not env_key.replace('_', '').replace('-', '').isalnum():
                warnings.append(f"Environment key '{env_key}' contains special characters - ensure it's a valid environment variable name")

        # Check for empty values
        for key, value in self.config.items():
            if not value.strip():
                errors.append(f"Configuration key '{key}' has an empty value")

        # Print warnings
        if warnings:
            print("⚠️  Configuration Warnings:")
            for warning in warnings:
                print(f"   • {warning}")
            print()

        # Raise errors if any
        if errors:
            print("❌ Configuration Errors:")
            for error in errors:
                print(f"   • {error}")
            print()
            raise ValueError(f"Configuration validation failed with {len(errors)} error(s)")

    def substitute_values(self, template: str) -> str:
        """Substitute configuration values into the template."""
        # Validate configuration first
        self.validate_config()

        # Extract values from config with defaults
        env_key = self.config.get('gh.workflow.env_key', 'ANTHROPIC_API_KEY')
        model = self.config.get('gh.workflow.model', 'anthropic/claude-sonnet-4-20250514')

        # Perform substitutions
        workflow = template.format(
            env_key=env_key,
            model=model
        )

        return workflow

    def generate_workflow(self, output_file: Optional[str] = None) -> str:
        """Generate the complete workflow file."""
        # Parse configuration
        self.parse_toml()

        # Get template and substitute values
        template = self.get_workflow_template()
        workflow = self.substitute_values(template)

        # Write to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(workflow)

            print(f"Workflow generated successfully: {output_path}")

        return workflow

    def print_config_summary(self):
        """Print a summary of the parsed configuration."""
        print("Configuration Summary:")
        print("-" * 40)
        for key, value in self.config.items():
            print(f"  {key}: {value}")
        print("-" * 40)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate OpenCode GitHub workflow from configuration file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_workflow.py
  python generate_workflow.py --config ogc/config.toml
  python generate_workflow.py --config custom.properties --output custom/.github/workflows/opencode.yml
  python generate_workflow.py --output - --verbose  # Print to stdout with config summary
        """
    )

    parser.add_argument(
        '--config', '-c',
        default='config.toml',
        help='Path to the configuration file (default: config.toml)'
    )

    parser.add_argument(
        '--output', '-o',
        default='ogc/generated/.github/workflows/opencode.yml',
        help='Output file path (default: ogc/generated/.github/workflows/opencode.yml)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show configuration summary'
    )

    args = parser.parse_args()

    try:
        # Create generator
        generator = WorkflowGenerator(args.config)

        # Generate workflow
        workflow = generator.generate_workflow(args.output)

        # Show config summary if verbose
        if args.verbose:
            generator.print_config_summary()

        # Print to stdout only if explicitly requested (output set to None or -)
        if args.output == '-' or (args.output is None):
            print(workflow)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except tomllib.TOMLDecodeError as e:
        print(f"❌ TOML parsing error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
