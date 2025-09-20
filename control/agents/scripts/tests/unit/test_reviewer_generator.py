#!/usr/bin/env python3
"""
Unit tests for the reviewer subagent generator.

This module contains comprehensive unit tests for the ReviewerAgentGenerator class,
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

from reviewer import ReviewerAgentGenerator


class TestReviewerAgentGenerator(unittest.TestCase):
    """Test cases for the ReviewerAgentGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.toml"
        self.generator = ReviewerAgentGenerator(str(self.config_path))

        # Create a sample reviewer template
        self.template_content = """# Code Reviewer Agent

You are a code review, security, and quality assurance specialist.

## Core Responsibilities

- **Code Quality Review**: Analyze code for maintainability and best practices
- **Security Assessment**: Identify potential security vulnerabilities
- **Performance Analysis**: Review code for performance bottlenecks
- **Standards Compliance**: Ensure adherence to coding standards
"""

        # Sample TOML configurations
        self.enabled_config = {
            'opencode': {
                'agents': {
                    'subagents': {
                        'reviewer': {
                            'enabled': True,
                            'template': 'default',
                            'template_file': 'control/agents/subagents/reviewer.md',
                            'additional_files': [],
                            'additional_files_strategy': 'merge',
                            'description': 'Code review, security, and quality assurance agent',
                            'mode': 'subagent',
                            'model': 'claude-4-sonnet',
                            'temperature': 0.1,
                            'permissions': {
                                'tools': {'read': True, 'grep': True, 'glob': True, 'bash': False, 'edit': False, 'write': False},
                                'bash_rules': {'*': 'deny'},
                                'edit_rules': {'**/*': 'deny'}
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
                        'reviewer': {
                            'enabled': False,
                            'template': 'default',
                            'template_file': 'control/agents/subagents/reviewer.md',
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

    def test_validate_reviewer_config_enabled(self):
        """Test validation of enabled reviewer configuration."""
        config = self.generator.validate_reviewer_config(self.enabled_config)
        self.assertIsNotNone(config)
        self.assertTrue(config['enabled'])

    def test_validate_reviewer_config_disabled(self):
        """Test validation of disabled reviewer configuration."""
        config = self.generator.validate_reviewer_config(self.disabled_config)
        self.assertIsNone(config)

    def test_validate_reviewer_config_missing(self):
        """Test validation with missing reviewer configuration."""
        empty_config = {'opencode': {'agents': {'subagents': {}}}}
        config = self.generator.validate_reviewer_config(empty_config)
        self.assertIsNone(config)

    def test_validate_and_read_template_default(self):
        """Test template validation and reading for default template."""
        config = self.enabled_config['opencode']['agents']['subagents']['reviewer']

        # Mock file operations
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100
                with patch('builtins.open', mock_open(read_data=self.template_content)):
                    template = self.generator.validate_and_read_template(config)
                    self.assertEqual(template, self.template_content)

    def test_get_output_path(self):
        """Test output path generation for subagent."""
        config = self.enabled_config['opencode']['agents']['subagents']['reviewer']
        path = self.generator._get_output_path(config)
        self.assertEqual(path, "generated/.opencode/agent/subagent/reviewer.md")

    def test_extract_agent_config(self):
        """Test extraction of agent configuration excluding config keys."""
        config = self.enabled_config['opencode']['agents']['subagents']['reviewer']
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
        """Test successful generation of reviewer configuration."""
        with patch.object(self.generator, 'load_toml_config', return_value=self.enabled_config):
            with patch.object(self.generator, 'validate_and_read_template', return_value=self.template_content):
                with patch.object(self.generator, 'write_agent_config') as mock_write:
                    result = self.generator.generate()
                    self.assertTrue(result)
                    mock_write.assert_called_once()

    def test_generate_disabled(self):
        """Test generation with disabled reviewer configuration."""
        with patch.object(self.generator, 'load_toml_config', return_value=self.disabled_config):
            result = self.generator.generate()
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
