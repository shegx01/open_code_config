#!/usr/bin/env python3
"""
Unit tests for the codebase-agent generator.

This module contains comprehensive unit tests for the CodebaseAgentGenerator class,
covering configuration loading, validation, template handling, and agent file generation.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

# Add the parent directory to the path to import the generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from codebase_agent import CodebaseAgentGenerator


class TestCodebaseAgentGenerator(unittest.TestCase):
    """Test cases for the CodebaseAgentGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.toml"
        self.generator = CodebaseAgentGenerator(str(self.config_path))

        # Create a sample codebase-agent template
        self.template_content = """# Codebase Agent

You are a multi-language implementation agent for modular and functional development.

## Core Responsibilities

- **Code Implementation**: Write clean, maintainable code following best practices
- **Architecture Design**: Design modular and scalable system architectures
- **Code Review**: Review code for quality, performance, and security
- **Documentation**: Create comprehensive technical documentation
"""

        # Sample TOML configurations
        self.enabled_config = {
            'opencode': {
                'agents': {
                    'codebase-agent': {
                        'enabled': True,
                        'template': 'default',
                        'template_file': 'control/agents/codebase-agent.md',
                        'additional_files': [],
                        'additional_files_strategy': 'merge',
                        'description': 'Multi-language implementation agent for modular and functional development',
                        'mode': 'primary',
                        'model': 'claude-4-sonnet',
                        'temperature': 0.1,
                        'permissions': {
                            'tools': {'read': True, 'edit': True, 'write': True, 'grep': True, 'glob': True, 'bash': True, 'patch': True},
                            'bash_rules': {'rm -rf *': 'ask', 'sudo *': 'deny', 'chmod *': 'ask'},
                            'edit_rules': {'**/*.env*': 'deny', '**/*.key': 'deny', 'node_modules/**': 'deny'}
                        }
                    }
                }
            }
        }

        self.disabled_config = {
            'opencode': {
                'agents': {
                    'codebase-agent': {
                        'enabled': False,
                        'template': 'default',
                        'template_file': 'control/agents/codebase-agent.md',
                        'additional_files': [],
                        'additional_files_strategy': 'merge'
                    }
                }
            }
        }

        self.custom_template_config = {
            'opencode': {
                'agents': {
                    'codebase-agent': {
                        'enabled': True,
                        'template': 'custom',
                        'template_file': 'custom/codebase-agent.md',
                        'additional_files': [],
                        'additional_files_strategy': 'merge',
                        'description': 'Custom codebase agent',
                        'mode': 'primary',
                        'model': 'claude-4-sonnet',
                        'temperature': 0.1
                    }
                }
            }
        }

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_toml_config_success(self):
        """Test successful TOML configuration loading."""
        with patch('builtins.open', mock_open(read_data=b'[test]\nkey = "value"')):
            with patch('tomllib.load') as mock_load:
                mock_load.return_value = {'test': {'key': 'value'}}
                config = self.generator.load_toml_config()
                self.assertEqual(config, {'test': {'key': 'value'}})

    def test_load_toml_config_file_not_found(self):
        """Test TOML configuration loading with missing file."""
        with self.assertRaises(FileNotFoundError):
            self.generator.load_toml_config()

    def test_load_toml_config_invalid_toml(self):
        """Test TOML configuration loading with invalid TOML."""
        with patch('builtins.open', mock_open(read_data=b'invalid toml content')):
            with patch('tomllib.load') as mock_load:
                import tomllib
                mock_load.side_effect = tomllib.TOMLDecodeError("Invalid TOML")
                with self.assertRaises(ValueError):
                    self.generator.load_toml_config()

    def test_validate_codebase_agent_config_enabled(self):
        """Test validation of enabled codebase-agent configuration."""
        config = self.generator.validate_codebase_agent_config(self.enabled_config)
        self.assertIsNotNone(config)
        self.assertTrue(config['enabled'])

    def test_validate_codebase_agent_config_disabled(self):
        """Test validation of disabled codebase-agent configuration."""
        config = self.generator.validate_codebase_agent_config(self.disabled_config)
        self.assertIsNone(config)

    def test_validate_codebase_agent_config_missing(self):
        """Test validation with missing codebase-agent configuration."""
        empty_config = {'opencode': {'agents': {}}}
        config = self.generator.validate_codebase_agent_config(empty_config)
        self.assertIsNone(config)

    def test_validate_and_read_template_default(self):
        """Test template validation and reading for default template."""
        config = self.enabled_config['opencode']['agents']['codebase-agent']

        # Mock file operations
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with patch('builtins.open', mock_open(read_data=self.template_content)):
                    template = self.generator.validate_and_read_template(config)
                    self.assertEqual(template, self.template_content)

    def test_validate_and_read_template_custom(self):
        """Test template validation and reading for custom template."""
        config = self.custom_template_config['opencode']['agents']['codebase-agent']

        # Mock file operations
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with patch('builtins.open', mock_open(read_data=self.template_content)):
                    template = self.generator.validate_and_read_template(config)
                    self.assertEqual(template, self.template_content)

    def test_validate_and_read_template_missing_file(self):
        """Test template validation with missing template file."""
        config = self.enabled_config['opencode']['agents']['codebase-agent']

        with patch('pathlib.Path.exists', return_value=False):
            with self.assertRaises(FileNotFoundError):
                self.generator.validate_and_read_template(config)

    def test_validate_and_read_template_empty_file(self):
        """Test template validation with empty template file."""
        config = self.enabled_config['opencode']['agents']['codebase-agent']

        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 0
                with self.assertRaises(ValueError):
                    self.generator.validate_and_read_template(config)

    def test_validate_and_read_template_empty_template_file(self):
        """Test template validation with empty template_file."""
        config = self.enabled_config['opencode']['agents']['codebase-agent'].copy()
        config['template_file'] = ''

        with self.assertRaises(ValueError):
            self.generator.validate_and_read_template(config)

    def test_validate_and_read_template_invalid_strategy(self):
        """Test template validation with invalid additional_files_strategy."""
        config = self.enabled_config['opencode']['agents']['codebase-agent'].copy()
        config['additional_files_strategy'] = 'invalid'

        with self.assertRaises(ValueError):
            self.generator.validate_and_read_template(config)

    def test_validate_and_read_template_unknown_type(self):
        """Test template validation with unknown template type."""
        config = self.enabled_config['opencode']['agents']['codebase-agent'].copy()
        config['template'] = 'unknown'

        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with self.assertRaises(ValueError):
                    self.generator.validate_and_read_template(config)

    def test_validate_and_read_template_with_additional_files_merge(self):
        """Test template validation with additional files using merge strategy."""
        config = self.enabled_config['opencode']['agents']['codebase-agent'].copy()
        config['additional_files'] = ['additional.md']
        config['additional_files_strategy'] = 'merge'

        additional_content = "# Additional Content"

        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with patch('builtins.open', mock_open()) as mock_file:
                    mock_file.return_value.read.side_effect = [self.template_content, additional_content]
                    template = self.generator.validate_and_read_template(config)
                    self.assertIn(self.template_content, template)
                    self.assertIn("# Additional Files", template)
                    self.assertIn(additional_content, template)

    def test_validate_and_read_template_with_additional_files_replace(self):
        """Test template validation with additional files using replace strategy."""
        config = self.enabled_config['opencode']['agents']['codebase-agent'].copy()
        config['additional_files'] = ['additional.md']
        config['additional_files_strategy'] = 'replace'

        additional_content = "# Additional Content"

        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with patch('builtins.open', mock_open(read_data=additional_content)):
                    template = self.generator.validate_and_read_template(config)
                    self.assertEqual(template, f"## additional.md\n\n{additional_content}")

    def test_get_output_path(self):
        """Test output path generation for primary agent."""
        config = self.enabled_config['opencode']['agents']['codebase-agent']
        path = self.generator._get_output_path(config)
        self.assertEqual(path, "generated/.opencode/agent/codebase-agent.md")

    def test_extract_agent_config(self):
        """Test extraction of agent configuration excluding config keys."""
        config = self.enabled_config['opencode']['agents']['codebase-agent']
        agent_config = self.generator._extract_agent_config(config)

        # Should exclude config-specific keys
        excluded_keys = {'enabled', 'template', 'template_file', 'additional_files', 'additional_files_strategy'}
        for key in excluded_keys:
            self.assertNotIn(key, agent_config)

        # Should include agent-specific keys
        self.assertIn('description', agent_config)
        self.assertIn('mode', agent_config)
        self.assertIn('model', agent_config)
        self.assertIn('permissions', agent_config)

    def test_format_permissions(self):
        """Test permissions formatting for YAML output."""
        permissions = {
            'tools': {'read': True, 'write': False},
            'bash_rules': {'sudo *': 'deny'},
            'edit_rules': {'**/*.key': 'deny'}
        }

        formatted = self.generator._format_permissions(permissions)

        self.assertIn('tools', formatted)
        self.assertIn('bash', formatted)
        self.assertIn('edit', formatted)
        self.assertEqual(formatted['bash'], permissions['bash_rules'])
        self.assertEqual(formatted['edit'], permissions['edit_rules'])

    def test_format_permissions_empty(self):
        """Test permissions formatting with empty permissions."""
        formatted = self.generator._format_permissions({})
        self.assertEqual(formatted, {})

    def test_strip_frontmatter(self):
        """Test YAML frontmatter stripping from template content."""
        content_with_frontmatter = """---
title: Test
description: Test template
---

# Template Content

This is the actual template content.
"""

        stripped = self.generator._strip_frontmatter(content_with_frontmatter)
        self.assertNotIn('---', stripped)
        self.assertNotIn('title: Test', stripped)
        self.assertIn('# Template Content', stripped)

    def test_strip_frontmatter_no_frontmatter(self):
        """Test frontmatter stripping with content that has no frontmatter."""
        content = "# Template Content\n\nThis is template content."
        stripped = self.generator._strip_frontmatter(content)
        self.assertEqual(stripped, content)

    def test_write_agent_config(self):
        """Test writing agent configuration to file."""
        config = self.enabled_config['opencode']['agents']['codebase-agent']

        with patch('pathlib.Path.mkdir'):
            with patch('builtins.open', mock_open()) as mock_file:
                self.generator.write_agent_config(config, self.template_content)

                # Verify file was opened for writing
                mock_file.assert_called_once()

                # Get the content that was written
                written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)

                # Verify YAML frontmatter is present
                self.assertIn('---', written_content)
                self.assertIn('description:', written_content)
                self.assertIn('mode:', written_content)
                self.assertIn('permissions:', written_content)

                # Verify template content is present
                self.assertIn('# Codebase Agent', written_content)

    def test_generate_success(self):
        """Test successful generation of codebase-agent configuration."""
        with patch.object(self.generator, 'load_toml_config', return_value=self.enabled_config):
            with patch.object(self.generator, 'validate_and_read_template', return_value=self.template_content):
                with patch.object(self.generator, 'write_agent_config') as mock_write:
                    result = self.generator.generate()
                    self.assertTrue(result)
                    mock_write.assert_called_once()

    def test_generate_disabled(self):
        """Test generation with disabled codebase-agent configuration."""
        with patch.object(self.generator, 'load_toml_config', return_value=self.disabled_config):
            result = self.generator.generate()
            self.assertFalse(result)

    def test_generate_exception(self):
        """Test generation with exception handling."""
        with patch.object(self.generator, 'load_toml_config', side_effect=Exception("Test error")):
            with self.assertRaises(SystemExit):
                self.generator.generate()


if __name__ == '__main__':
    unittest.main()
