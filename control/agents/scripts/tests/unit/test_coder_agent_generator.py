#!/usr/bin/env python3
"""
Unit tests for the coder-agent subagent generator.

This module contains comprehensive unit tests for the CoderAgentGenerator class,
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

from coder_agent import CoderAgentGenerator


class TestCoderAgentGenerator(unittest.TestCase):
    """Test cases for the CoderAgentGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.toml"
        self.generator = CoderAgentGenerator(str(self.config_path))

        # Create sample templates
        self.base_template_content = """# Coder Agent

You are a coding execution specialist that implements coding subtasks in sequence.

## Core Responsibilities

- **Code Implementation**: Execute coding tasks with precision
- **Sequential Execution**: Complete subtasks in proper order
- **Quality Assurance**: Ensure code meets specifications
- **Error Handling**: Handle and resolve coding issues
"""

        self.elixir_template_content = """## Elixir Coding Specifics

### Functional Programming
- Immutable data structures
- Pattern matching
- Pipeline operators

### OTP Patterns
- GenServer implementations
- Supervision trees
"""

        # Sample TOML configurations
        self.enabled_config = {
            'opencode': {
                'agents': {
                    'subagents': {
                        'coder-agent': {
                            'enabled': True,
                            'template': 'default',
                            'lang': 'elixir',
                            'template_file': '',
                            'additional_files': [],
                            'additional_files_strategy': 'merge',
                            'include_base_template': True,
                            'description': 'Executes coding subtasks in sequence, ensuring completion as specified',
                            'mode': 'subagent',
                            'model': 'claude-4-sonnet',
                            'temperature': 0,
                            'permissions': {
                                'tools': {'read': True, 'edit': True, 'write': True, 'grep': True, 'glob': True, 'bash': True, 'patch': True},
                                'bash_rules': {'rm -rf *': 'deny', 'sudo *': 'deny', 'mix *': 'allow'},
                                'edit_rules': {'**/*.env*': 'deny', '**/*.key': 'deny', 'node_modules/**': 'deny'}
                            }
                        }
                    }
                }
            }
        }

        self.disabled_config = {
            'opencode': {
                'agents': {
                    'subagents': {
                        'coder-agent': {
                            'enabled': False,
                            'template': 'default',
                            'lang': 'elixir',
                            'template_file': '',
                            'additional_files': [],
                            'additional_files_strategy': 'merge',
                            'include_base_template': True
                        }
                    }
                }
            }
        }

        self.kotlin_config = {
            'opencode': {
                'agents': {
                    'subagents': {
                        'coder-agent': {
                            'enabled': True,
                            'template': 'default',
                            'lang': 'kotlin',
                            'template_file': '',
                            'additional_files': [],
                            'additional_files_strategy': 'merge',
                            'include_base_template': True,
                            'description': 'Kotlin coder agent',
                            'mode': 'subagent',
                            'model': 'claude-4-sonnet',
                            'temperature': 0
                        }
                    }
                }
            }
        }

        self.custom_template_config = {
            'opencode': {
                'agents': {
                    'subagents': {
                        'coder-agent': {
                            'enabled': True,
                            'template': 'custom',
                            'template_file': 'custom/coder-agent.md',
                            'additional_files': [],
                            'additional_files_strategy': 'merge',
                            'description': 'Custom coder agent',
                            'mode': 'subagent',
                            'model': 'claude-4-sonnet',
                            'temperature': 0
                        }
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

    def test_validate_coder_agent_config_enabled(self):
        """Test validation of enabled coder-agent configuration."""
        config = self.generator.validate_coder_agent_config(self.enabled_config)
        self.assertIsNotNone(config)
        self.assertTrue(config['enabled'])

    def test_validate_coder_agent_config_disabled(self):
        """Test validation of disabled coder-agent configuration."""
        config = self.generator.validate_coder_agent_config(self.disabled_config)
        self.assertIsNone(config)

    def test_validate_coder_agent_config_missing(self):
        """Test validation with missing coder-agent configuration."""
        empty_config = {'opencode': {'agents': {'subagents': {}}}}
        config = self.generator.validate_coder_agent_config(empty_config)
        self.assertIsNone(config)

    def test_validate_and_read_template_with_base_and_lang(self):
        """Test template validation with base template and language-specific template."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent']

        # Mock file operations
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with patch('builtins.open', mock_open()) as mock_file:
                    mock_file.return_value.read.side_effect = [self.base_template_content, self.elixir_template_content]
                    template = self.generator.validate_and_read_template(config)
                    self.assertIn(self.base_template_content, template)
                    self.assertIn("# Elixir Coding Specifics", template)
                    self.assertIn(self.elixir_template_content, template)

    def test_validate_and_read_template_base_only(self):
        """Test template validation with base template only (no language)."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent'].copy()
        config['lang'] = ''

        # Mock file operations
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with patch('builtins.open', mock_open(read_data=self.base_template_content)):
                    template = self.generator.validate_and_read_template(config)
                    self.assertEqual(template, self.base_template_content)

    def test_validate_and_read_template_empty_lang_file(self):
        """Test template validation with empty language file (should skip gracefully)."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent']

        # Mock file operations - base exists, lang file is empty
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                def side_effect(path):
                    if 'base.md' in str(path):
                        return type('MockStat', (), {'st_size': 100})()
                    else:  # language file
                        return type('MockStat', (), {'st_size': 0})()

                mock_stat.side_effect = side_effect

                with patch('builtins.open', mock_open(read_data=self.base_template_content)):
                    template = self.generator.validate_and_read_template(config)
                    self.assertEqual(template, self.base_template_content)
                    # Should not contain language-specific content
                    self.assertNotIn("Elixir Coding Specifics", template)

    def test_validate_and_read_template_unsupported_language(self):
        """Test template validation with unsupported language."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent'].copy()
        config['lang'] = 'unsupported'

        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(config)
        self.assertIn("Unsupported language", str(context.exception))

    def test_validate_and_read_template_missing_base(self):
        """Test template validation with missing base template."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent']

        with patch('pathlib.Path.exists', return_value=False):
            with self.assertRaises(FileNotFoundError):
                self.generator.validate_and_read_template(config)

    def test_validate_and_read_template_missing_lang_file(self):
        """Test template validation with missing language template file."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent']

        def exists_side_effect(path):
            return 'base.md' in str(path)  # Only base exists, lang file doesn't

        with patch('pathlib.Path.exists', side_effect=exists_side_effect):
            with self.assertRaises(FileNotFoundError):
                self.generator.validate_and_read_template(config)

    def test_validate_and_read_template_custom(self):
        """Test template validation with custom template."""
        config = self.custom_template_config['opencode']['agents']['subagents']['coder-agent']

        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with patch('builtins.open', mock_open(read_data=self.base_template_content)):
                    template = self.generator.validate_and_read_template(config)
                    self.assertEqual(template, self.base_template_content)

    def test_validate_and_read_template_invalid_strategy(self):
        """Test template validation with invalid additional_files_strategy."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent'].copy()
        config['additional_files_strategy'] = 'invalid'

        with self.assertRaises(ValueError):
            self.generator.validate_and_read_template(config)

    def test_validate_and_read_template_no_content_available(self):
        """Test template validation with no content available."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent'].copy()
        config['include_base_template'] = False
        config['lang'] = ''

        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(config)
        self.assertIn("No template content available", str(context.exception))

    def test_validate_and_read_template_with_additional_files_merge(self):
        """Test template validation with additional files using merge strategy."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent'].copy()
        config['additional_files'] = ['additional.md']
        config['additional_files_strategy'] = 'merge'

        additional_content = "# Additional Content"

        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with patch('builtins.open', mock_open()) as mock_file:
                    mock_file.return_value.read.side_effect = [self.base_template_content, self.elixir_template_content, additional_content]
                    template = self.generator.validate_and_read_template(config)
                    self.assertIn(self.base_template_content, template)
                    self.assertIn("# Additional Files", template)
                    self.assertIn(additional_content, template)

    def test_get_output_path(self):
        """Test output path generation for subagent."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent']
        path = self.generator._get_output_path(config)
        self.assertEqual(path, "generated/.opencode/agent/subagent/coder-agent.md")

    def test_extract_agent_config(self):
        """Test extraction of agent configuration excluding config keys."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent']
        agent_config = self.generator._extract_agent_config(config)

        # Should exclude config-specific keys
        excluded_keys = {'enabled', 'template', 'template_file', 'additional_files', 'additional_files_strategy', 'include_base_template', 'lang'}
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
            'edit_rules': {'**/*.env*': 'deny'}
        }

        formatted = self.generator._format_permissions(permissions)

        self.assertIn('tools', formatted)
        self.assertIn('bash', formatted)
        self.assertIn('edit', formatted)
        self.assertEqual(formatted['bash'], permissions['bash_rules'])
        self.assertEqual(formatted['edit'], permissions['edit_rules'])

    def test_write_agent_config(self):
        """Test writing agent configuration to file."""
        config = self.enabled_config['opencode']['agents']['subagents']['coder-agent']

        with patch('pathlib.Path.mkdir'):
            with patch('builtins.open', mock_open()) as mock_file:
                self.generator.write_agent_config(config, self.base_template_content)

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
                self.assertIn('# Coder Agent', written_content)

    def test_generate_success(self):
        """Test successful generation of coder-agent configuration."""
        with patch.object(self.generator, 'load_toml_config', return_value=self.enabled_config):
            with patch.object(self.generator, 'validate_and_read_template', return_value=self.base_template_content):
                with patch.object(self.generator, 'write_agent_config') as mock_write:
                    result = self.generator.generate()
                    self.assertTrue(result)
                    mock_write.assert_called_once()

    def test_generate_disabled(self):
        """Test generation with disabled coder-agent configuration."""
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
