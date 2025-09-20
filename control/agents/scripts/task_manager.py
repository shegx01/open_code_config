#!/usr/bin/env python3
"""
Task-manager agent generator script.

This script parses the TOML configuration file and generates the appropriate
task-manager agent configuration based on the settings. It validates the configuration
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


class TaskManagerAgentGenerator:
    """Generates task-manager agent configuration from TOML settings."""

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

    def validate_task_manager_config(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate the task-manager configuration and return the agent settings.

        Returns None if the configuration should not generate anything.
        """
        # The task-manager config is under opencode.agents
        opencode_config = config.get('opencode', {})
        agents_config = opencode_config.get('agents', {})
        task_manager_config = agents_config.get('task-manager', {})

        if not task_manager_config:
            print("No task-manager configuration found in TOML file")
            return None

        # Check if enabled is false
        if not task_manager_config.get('enabled', True):
            print("Task-manager agent is disabled (enabled = false)")
            return None

        return task_manager_config

    def validate_and_read_template(self, task_manager_config: Dict[str, Any]) -> str:
        """
        Validate the template configuration and return the template content.

        Handles template files and additional files with merge/replace strategies.
        Raises an error if custom template is specified but file is empty or missing.
        """
        template_type = task_manager_config.get('template', 'default')
        template_file = task_manager_config.get('template_file', '')
        additional_files = task_manager_config.get('additional_files', [])
        additional_files_strategy = task_manager_config.get('additional_files_strategy', 'merge')

        # Validate additional_files_strategy
        if additional_files_strategy not in ['merge', 'replace']:
            raise ValueError(f"Invalid additional_files_strategy: {additional_files_strategy}. Must be 'merge' or 'replace'")

        # Get main template content (unless using replace strategy with additional files)
        main_template_content = ""
        if additional_files_strategy != 'replace' or not additional_files:
            if template_type == 'default':
                # Use the template_file specified in config
                if not template_file:
                    raise ValueError("Default template specified but template_file is empty")

                # Check if template file exists and is not empty
                default_template_path = Path(template_file)
                if not default_template_path.is_absolute():
                    default_template_path = self.project_root / default_template_path

                if not default_template_path.exists():
                    raise FileNotFoundError(f"Template file not found: {default_template_path}")

                if default_template_path.stat().st_size == 0:
                    raise ValueError(f"Template file is empty: {default_template_path}")

                # Read template content
                try:
                    with open(default_template_path, 'r', encoding='utf-8') as f:
                        main_template_content = f.read()
                except Exception as e:
                    raise ValueError(f"Failed to read template file {default_template_path}: {e}")

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

    def _get_output_path(self, task_manager_config: Dict[str, Any]) -> str:
        """
        Determine the output path based on the agent mode.

        Primary agents output to '.opencode/agent/task-manager.md'
        """
        return "generated/.opencode/agent/task-manager.md"

    def _extract_agent_config(self, task_manager_config: Dict[str, Any]) -> Dict[str, Any]:
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
        for key, value in task_manager_config.items():
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

    def write_agent_config(self, task_manager_config: Dict[str, Any], template_content: str) -> None:
        """Write the agent configuration to a Markdown file with YAML frontmatter."""
        output_path = self._get_output_path(task_manager_config)
        output_file = self.project_root / output_path

        # Ensure the output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Strip existing frontmatter from template content if present
        clean_content = self._strip_frontmatter(template_content)

        # Extract agent configuration (excluding config keys)
        agent_config = self._extract_agent_config(task_manager_config)

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

        print(f"Generated task-manager agent configuration: {output_file}")

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

            # Validate task-manager configuration
            task_manager_config = self.validate_task_manager_config(config)
            if task_manager_config is None:
                return False

            # Validate template and read content
            template_content = self.validate_and_read_template(task_manager_config)

            # Write the agent configuration file
            self.write_agent_config(task_manager_config, template_content)

            return True

        except Exception as e:
            print(f"Error generating task-manager agent configuration: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point for the script."""
    # Determine config path (can be overridden via command line argument)
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.toml"

    generator = TaskManagerAgentGenerator(config_path)
    success = generator.generate()

    if success:
        print("Task-manager agent configuration generated successfully")
    else:
        print("Task-manager agent configuration generation skipped")


if __name__ == "__main__":
    main()
