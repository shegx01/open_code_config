#!/usr/bin/env python3
"""
Tester subagent generator script.

This script parses the TOML configuration file and generates the appropriate
tester subagent configuration based on the settings. It validates the configuration
and generates a markdown file with YAML frontmatter matching the agent format.
"""

import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Handle tomllib import for different Python versions
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: Neither tomllib (Python 3.11+) nor tomli package is available.", file=sys.stderr)
        print("Please install tomli: pip install tomli", file=sys.stderr)
        sys.exit(1)


class TesterAgentGenerator:
    """Generates tester subagent configuration from TOML settings."""

    def __init__(self, config_path: str = "config.toml"):
        """Initialize the generator with the config file path."""
        self.config_path = Path(config_path)
        if self.config_path.is_absolute():
            # For absolute paths, project root is the parent directory of config.toml
            self.project_root = self.config_path.parent
        else:
            # For relative paths, resolve relative to current working directory
            self.config_path = self.config_path.resolve()
            self.project_root = self.config_path.parent

    def load_toml_config(self) -> Dict[str, Any]:
        """Load and parse the TOML configuration file."""
        try:
            with open(self.config_path, 'rb') as f:
                return tomllib.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML configuration: {e}")

    def validate_tester_config(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate the tester configuration and return the agent settings.

        Returns None if the configuration should not generate anything.
        """
        # The tester config is under opencode.agents.subagents
        opencode_config = config.get('opencode', {})
        agents_config = opencode_config.get('agents', {})
        subagents_config = agents_config.get('subagents', {})
        tester_config = subagents_config.get('tester', {})

        if not tester_config:
            print("No tester configuration found in TOML file")
            return None

        # Check if enabled is false
        if not tester_config.get('enabled', True):
            print("Tester subagent is disabled (enabled = false)")
            return None

        return tester_config

    def validate_and_read_template(self, tester_config: Dict[str, Any]) -> str:
        """
        Validate the template configuration and return the template content.

        Handles template files and additional files with merge/replace strategies.
        Raises an error if custom template is specified but file is empty or missing.
        """
        template_type = tester_config.get('template', 'default')
        template_file = tester_config.get('template_file', '')
        additional_files = tester_config.get('additional_files', [])
        additional_files_strategy = tester_config.get('additional_files_strategy', 'merge')

        # Validate additional_files_strategy
        if additional_files_strategy not in ['merge', 'replace']:
            raise ValueError(f"Invalid additional_files_strategy: {additional_files_strategy}. Must be 'merge' or 'replace'")

        # Validate template configuration consistency
        if template_type == 'custom' and not template_file:
            raise ValueError("Custom template specified but template_file is empty")
        
        if template_type == 'default' and template_file:
            print(f"Warning: template_file '{template_file}' specified but template is 'default'. template_file will be ignored.")

        # Get main template content (unless using replace strategy with additional files)
        main_template_content = ""
        if additional_files_strategy != 'replace' or not additional_files:
            if template_type == 'default':
                # Use default template location for tester subagent
                default_template_path = self.project_root / "control/agents/subagents/tester.md"
                
                if not default_template_path.exists():
                    raise FileNotFoundError(f"Default template file not found: {default_template_path}")

                if default_template_path.stat().st_size == 0:
                    raise ValueError(f"Default template file is empty: {default_template_path}")

                # Read template content
                try:
                    with open(default_template_path, 'r', encoding='utf-8') as f:
                        main_template_content = f.read()
                except Exception as e:
                    raise ValueError(f"Failed to read default template file {default_template_path}: {e}")

            elif template_type == 'custom':
                if not template_file:
                    raise ValueError("Custom template specified but template_file is empty")

                # Check if custom template file exists and is not empty
                custom_template_path = Path(template_file)
                if not custom_template_path.is_absolute():
                    custom_template_path = self.project_root / custom_template_path

                if not custom_template_path.exists():
                    raise FileNotFoundError(f"Custom template file not found: {custom_template_path}")

                if custom_template_path.stat().st_size == 0:
                    raise ValueError(f"Custom template file is empty: {custom_template_path}")

                # Read custom template content
                try:
                    with open(custom_template_path, 'r', encoding='utf-8') as f:
                        main_template_content = f.read()
                except Exception as e:
                    raise ValueError(f"Failed to read custom template file {custom_template_path}: {e}")
            else:
                raise ValueError(f"Unknown template type: {template_type}")

        # Process additional files
        additional_content = self._process_additional_files(additional_files)

        # Apply strategy
        if additional_files_strategy == 'replace' and additional_files:
            return additional_content
        elif additional_files_strategy == 'merge':
            if additional_content:
                return f"{main_template_content}\n\n# Additional Files\n\n{additional_content}"
            else:
                return main_template_content
        else:
            return main_template_content

    def _process_additional_files(self, additional_files: list) -> str:
        """
        Process additional files and return their combined content.

        Args:
            additional_files: List of file paths to process

        Returns:
            Combined content of all additional files
        """
        if not additional_files:
            return ""

        combined_content = []

        for file_path in additional_files:
            # Resolve file path
            additional_file_path = Path(file_path)
            if not additional_file_path.is_absolute():
                additional_file_path = self.project_root / additional_file_path

            # Validate file exists
            if not additional_file_path.exists():
                raise FileNotFoundError(f"Additional file not found: {additional_file_path}")

            # Read file content
            try:
                with open(additional_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():  # Only add non-empty files
                        combined_content.append(f"## {additional_file_path.name}\n\n{content}")
            except Exception as e:
                raise ValueError(f"Failed to read additional file {additional_file_path}: {e}")

        return "\n\n".join(combined_content)

    def _get_output_path(self, tester_config: Dict[str, Any]) -> str:
        """
        Determine the output path based on the agent mode.

        Subagents output to '.opencode/agent/subagent/tester.md'
        """
        return "generated/.opencode/agent/subagent/tester.md"

    def _extract_agent_config(self, tester_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract agent configuration excluding config-specific keys.

        Config keys to exclude: enabled, template, template_file, additional_files,
        additional_files_strategy
        """
        # Keys that should not be included in the final agent configuration
        config_keys = {
            'enabled', 'template', 'template_file', 'additional_files',
            'additional_files_strategy'
        }

        # Extract agent configuration excluding config keys
        agent_config = {}
        for key, value in tester_config.items():
            if key not in config_keys:
                agent_config[key] = value

        return agent_config

    def _format_permissions(self, permissions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format permissions structure to match the expected YAML format.

        Converts the nested permissions structure to the proper format.
        """
        if not permissions:
            return {}

        formatted_permissions = {}

        # Handle tools permissions
        tools = permissions.get('tools', {})
        if tools:
            formatted_permissions['tools'] = tools

        # Handle bash_rules as bash permissions
        bash_rules = permissions.get('bash_rules', {})
        if bash_rules:
            formatted_permissions['bash'] = bash_rules

        # Handle edit_rules as edit permissions
        edit_rules = permissions.get('edit_rules', {})
        if edit_rules:
            formatted_permissions['edit'] = edit_rules

        return formatted_permissions

    def write_agent_config(self, tester_config: Dict[str, Any], template_content: str) -> None:
        """Write the agent configuration to a Markdown file with YAML frontmatter."""
        output_path = self._get_output_path(tester_config)
        output_file = self.project_root / output_path

        # Ensure the output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Strip existing frontmatter from template content if present
        clean_content = self._strip_frontmatter(template_content)

        # Extract agent configuration (excluding config keys)
        agent_config = self._extract_agent_config(tester_config)

        # Format permissions properly
        if 'permissions' in agent_config:
            agent_config['permissions'] = self._format_permissions(agent_config['permissions'])

        # Build the YAML frontmatter
        frontmatter_lines = ["---"]

        # Add each configuration item
        for key, value in agent_config.items():
            if key == 'permissions':
                # Handle permissions as a nested structure
                frontmatter_lines.append(f"{key}:")
                for perm_key, perm_value in value.items():
                    if isinstance(perm_value, dict):
                        frontmatter_lines.append(f"  {perm_key}:")
                        for sub_key, sub_value in perm_value.items():
                            if isinstance(sub_value, str):
                                frontmatter_lines.append(f'    "{sub_key}": "{sub_value}"')
                            else:
                                frontmatter_lines.append(f'    {sub_key}: {str(sub_value).lower()}')
                    else:
                        frontmatter_lines.append(f"  {perm_key}: {str(value).lower()}")
            elif isinstance(value, str):
                frontmatter_lines.append(f'{key}: "{value}"')
            elif isinstance(value, (int, float)):
                frontmatter_lines.append(f'{key}: {value}')
            elif isinstance(value, bool):
                frontmatter_lines.append(f'{key}: {str(value).lower()}')
            else:
                frontmatter_lines.append(f'{key}: {value}')

        frontmatter_lines.append("---")
        frontmatter_lines.append("")  # Empty line after frontmatter

        # Combine frontmatter and content
        complete_content = "\n".join(frontmatter_lines) + clean_content

        # Write the complete content
        with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(complete_content)

        print(f"Generated tester subagent configuration: {output_file}")

    def _strip_frontmatter(self, content: str) -> str:
        """Strip YAML frontmatter from content if present."""
        lines = content.split('\n')

        # Check if content starts with frontmatter
        if lines and lines[0].strip() == '---':
            # Find the closing frontmatter delimiter
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    # Return content after the closing delimiter, skipping empty lines
                    remaining_lines = lines[i+1:]
                    # Skip leading empty lines
                    while remaining_lines and not remaining_lines[0].strip():
                        remaining_lines = remaining_lines[1:]
                    return '\n'.join(remaining_lines)

        # No frontmatter found, return original content
        return content

    def generate(self) -> bool:
        """
        Main generation method.

        Returns True if configuration was generated, False if skipped.
        """
        try:
            # Load TOML configuration
            config = self.load_toml_config()

            # Validate tester configuration
            tester_config = self.validate_tester_config(config)
            if tester_config is None:
                return False

            # Validate template and read content
            template_content = self.validate_and_read_template(tester_config)

            # Write the agent configuration file
            self.write_agent_config(tester_config, template_content)

            return True

        except Exception as e:
            print(f"Error generating tester subagent configuration: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point for the script."""
    # Determine config path (can be overridden via command line argument)
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.toml"

    generator = TesterAgentGenerator(config_path)
    success = generator.generate()

    if success:
        print("Tester subagent configuration generated successfully")
    else:
        print("Tester subagent configuration generation skipped")


if __name__ == "__main__":
    main()
