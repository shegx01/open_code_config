#!/usr/bin/env python3
"""
Unit tests for the tester subagent generator.

This module contains comprehensive unit tests for the TesterAgentGenerator class,
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

from tester import TesterAgentGenerator


class TestTesterAgentGenerator(unittest.TestCase):
    """Test cases for the TesterAgentGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.toml"
        self.generator = TesterAgentGenerator(str(self.config_path))

        # Create a sample tester template
        self.template_content = """# Test Authoring Agent

You are a test authoring and TDD specialist.

## Core Responsibilities

- **Test Design**: Create comprehensive test suites and test cases
- **TDD Implementation**: Follow test-driven development practices
- **Test Automation**: Implement automated testing frameworks
- **Quality Assurance**: Ensure test coverage and reliability
"""

        # Sample TOML configurations
        self.enabled_config = {
            'opencode': {
                'agents': {
                    'subagents': {
                        'tester': {
                            'enabled': True,
                            'template': 'default',
                            'template_file': 'control/agents/subagents/tester.md',
                            'additional_files': [],
                            'additional_files_strategy': 'merge',
                            'description': 'Test authoring and TDD agent',
                            'mode': 'subagent',
                            'model': 'google/gemini-2.5-flash',
                            'temperature': 0.1,
                            'permissions': {
                                'tools': {'read': True, 'grep': True, 'glob': True, 'edit': True, 'write': True, 'bash': True},
                                'bash_rules': {'rm -rf *': 'ask', 'sudo *': 'deny'},
                                'edit_rules': {'**/*.env*': 'deny', '**/*.key': 'deny', '**/*.secret': 'deny'}
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
                        'tester': {
                            'enabled': False,
                            'template': 'default',
                            'template_file': 'control/agents/subagents/tester.md',
                            'additional_files': [],
                            'additional_files_strategy': 'merge'
                        }
                    }
                }
            }
        }

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_tester_config_enabled(self):
        """Test validation of enabled tester configuration."""
        config = self.generator.validate_tester_config(self.enabled_config)
        self.assertIsNotNone(config)
        self.assertTrue(config['enabled'])

    def test_validate_tester_config_disabled(self):
        """Test validation of disabled tester configuration."""
        config = self.generator.validate_tester_config(self.disabled_config)
        self.assertIsNone(config)

    def test_validate_tester_config_missing(self):
        """Test validation with missing tester configuration."""
        empty_config = {'opencode': {'agents': {'subagents': {}}}}
        config = self.generator.validate_tester_config(empty_config)
        self.assertIsNone(config)

    def test_validate_and_read_template_default(self):
        """Test template validation and reading for default template."""
        config = self.enabled_config['opencode']['agents']['subagents']['tester']

        # Mock file operations
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with patch('builtins.open', mock_open(read_data=self.template_content)):
                    template = self.generator.validate_and_read_template(config)
                    self.assertEqual(template, self.template_content)

    def test_get_output_path(self):
        """Test output path generation for subagent."""
        config = self.enabled_config['opencode']['agents']['subagents']['tester']
        path = self.generator._get_output_path(config)
        self.assertEqual(path, "generated/.opencode/agent/subagent/tester.md")

    def test_extract_agent_config(self):
        """Test extraction of agent configuration excluding config keys."""
        config = self.enabled_config['opencode']['agents']['subagents']['tester']
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

    def test_generate_success(self):
        """Test successful generation of tester configuration."""
        with patch.object(self.generator, 'load_toml_config', return_value=self.enabled_config):
            with patch.object(self.generator, 'validate_and_read_template', return_value=self.template_content):
                with patch.object(self.generator, 'write_agent_config') as mock_write:
                    result = self.generator.generate()
                    self.assertTrue(result)
                    mock_write.assert_called_once()

    def test_generate_disabled(self):
        """Test generation with disabled tester configuration."""
        with patch.object(self.generator, 'load_toml_config', return_value=self.disabled_config):
            result = self.generator.generate()
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
