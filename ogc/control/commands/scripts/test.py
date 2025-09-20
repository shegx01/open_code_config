#!/usr/bin/env python3
"""
Test command generator script.

This script parses the TOML configuration file and generates the appropriate
test command configuration based on the settings. It validates the configuration
and generates a Markdown file with YAML frontmatter matching the test command format.
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


class TestConfigGenerator:
    """Generates test command configuration from TOML settings."""
    
    def __init__(self, config_path: str = "ogc/config.toml"):
        """Initialize the generator with the config file path."""
        self.config_path = Path(config_path)
        self.project_root = self.config_path.parent.parent
        
    def load_toml_config(self) -> Dict[str, Any]:
        """Load and parse the TOML configuration file."""
        try:
            with open(self.config_path, 'rb') as f:
                return tomllib.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML configuration: {e}")
    
    def validate_test_config(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate the test configuration and return the test settings.
        
        Returns None if the configuration should not generate anything.
        """
        opencode_config = config.get('opencode', {})
        commands_config = opencode_config.get('commands', {})
        test_config = commands_config.get('test', {})
        
        if not test_config:
            print("No test configuration found in TOML file")
            return None
            
        # Check if enabled is false
        if not test_config.get('enabled', True):
            print("Test command is disabled (enabled = false)")
            return None
            
        # Validate language if specified
        lang = test_config.get('lang', '')
        if lang:
            supported_langs = ['elixir', 'kotlin', 'typescript']
            if lang not in supported_langs:
                print(f"Language '{lang}' is not supported. Supported languages: {', '.join(supported_langs)}")
                return None
            
        return test_config
    
    def validate_and_read_template(self, test_config: Dict[str, Any]) -> str:
        """
        Validate the template configuration and return the template content.
        
        Handles additional files with merge/replace strategies and language-specific templates.
        Raises an error if custom template is specified but file is empty or missing.
        """
        template_type = test_config.get('template', 'default')
        template_file = test_config.get('template_file', '')
        additional_files = test_config.get('additional_files', [])
        additional_files_strategy = test_config.get('additional_files_strategy', 'merge')
        lang = test_config.get('lang', '')
        include_base_template = test_config.get('include_base_template', False)
        
        # Validate additional_files_strategy
        if additional_files_strategy not in ['merge', 'replace']:
            raise ValueError(f"Invalid additional_files_strategy: {additional_files_strategy}. Must be 'merge' or 'replace'")
        
        # Get main template content (unless using replace strategy with additional files)
        main_template_content = ""
        if additional_files_strategy != 'replace' or not additional_files:
            if template_type == 'default':
                # For test command, we need to handle base template and language-specific templates
                template_content_parts = []
                
                # Include base template if requested
                if include_base_template:
                    base_template_path = self.project_root / "ogc/control/commands/generic/test/base.md"
                    if base_template_path.exists():
                        try:
                            with open(base_template_path, 'r', encoding='utf-8') as f:
                                base_content = f.read()
                                template_content_parts.append(base_content)
                        except Exception as e:
                            raise ValueError(f"Failed to read base template file {base_template_path}: {e}")
                    else:
                        print(f"Warning: Base template not found at {base_template_path}")
                
                # Include language-specific template if language is specified
                if lang:
                    lang_template_path = self.project_root / f"ogc/control/commands/generic/test/{lang}.md"
                    if lang_template_path.exists():
                        try:
                            with open(lang_template_path, 'r', encoding='utf-8') as f:
                                lang_content = f.read()
                                template_content_parts.append(lang_content)
                        except Exception as e:
                            raise ValueError(f"Failed to read language template file {lang_template_path}: {e}")
                    else:
                        print(f"Warning: Language template not found at {lang_template_path}")
                
                # Combine template parts
                if template_content_parts:
                    main_template_content = "\n\n".join(template_content_parts)
                else:
                    # Fallback to base template only if no parts were found
                    base_template_path = self.project_root / "ogc/control/commands/generic/test/base.md"
                    if base_template_path.exists():
                        try:
                            with open(base_template_path, 'r', encoding='utf-8') as f:
                                main_template_content = f.read()
                        except Exception as e:
                            raise ValueError(f"Failed to read fallback base template file {base_template_path}: {e}")
                    else:
                        raise FileNotFoundError(f"No template files found. Base template missing: {base_template_path}")
                        
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
    
    def generate_yaml_config(self, test_config: Dict[str, Any], template_content: str) -> Dict[str, Any]:
        """Generate the YAML configuration matching the test.yaml format."""
        return {
            "$schema": "https://opencode.ai/config.json",
            "command": {
                "test": {
                    "template": template_content,
                    "description": "Test command",
                    "agent": test_config.get('agent', 'build'),
                    "model": test_config.get('model', 'anthropic/claude-sonnet-4-20250514')
                }
            }
        }
    
    def write_yaml_config(self, test_config: Dict[str, Any], template_content: str, output_path: str = "ogc/generated/.opencode/command/test.md") -> None:
        """Write the configuration to a Markdown file with YAML frontmatter (preferred by OpenCode CLI)."""
        output_file = self.project_root / output_path
        
        # Ensure the output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Strip existing frontmatter from template content if present
        clean_content = self._strip_frontmatter(template_content)
        
        # Create the complete file content as a single string
        description = test_config.get('description', 'Test command')
        agent = test_config.get('agent', 'build')
        model = test_config.get('model', 'anthropic/claude-sonnet-4-20250514')
        
        # Build the complete file content in one go
        complete_content = f"""---
description: {description}
agent: {agent}
model: {model}
---

{clean_content}"""
        
        # Write the complete content in a single operation
        with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(complete_content)
        
        print(f"Generated test configuration (markdown): {output_path}")
    
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
            
            # Validate test configuration
            test_config = self.validate_test_config(config)
            if test_config is None:
                return False
            
            # Validate template and read content
            template_content = self.validate_and_read_template(test_config)
            
            # Write the configuration file in frontmatter format
            self.write_yaml_config(test_config, template_content)
            
            return True
            
        except Exception as e:
            print(f"Error generating test configuration: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point for the script."""
    # Determine config path (can be overridden via command line argument)
    config_path = sys.argv[1] if len(sys.argv) > 1 else "ogc/config.toml"
    
    generator = TestConfigGenerator(config_path)
    success = generator.generate()
    
    if success:
        print("Test configuration generated successfully")
    else:
        print("Test configuration generation skipped")


if __name__ == "__main__":
    main()
