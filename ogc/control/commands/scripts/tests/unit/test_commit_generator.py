#!/usr/bin/env python3
"""
Unit tests for the CommitConfigGenerator class.

Tests all validation scenarios, template processing, and error handling.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from ogc.control.commands.scripts.commit import CommitConfigGenerator


class TestCommitConfigGenerator(unittest.TestCase):
    """Test cases for CommitConfigGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.fixtures_dir = self.test_dir / "fixtures"
        
    def test_load_toml_config_success(self):
        """Test successful TOML configuration loading."""
        config_path = self.fixtures_dir / "config_enabled.toml"
        generator = CommitConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        
        self.assertIn('opencode', config)
        self.assertIn('commands', config['opencode'])
        self.assertIn('commit', config['opencode']['commands'])
        
    def test_load_toml_config_file_not_found(self):
        """Test TOML loading with non-existent file."""
        generator = CommitConfigGenerator("nonexistent.toml")
        
        with self.assertRaises(FileNotFoundError) as context:
            generator.load_toml_config()
        
        self.assertIn("Configuration file not found", str(context.exception))
        
    def test_validate_commit_config_enabled(self):
        """Test validation with enabled commit configuration."""
        config_path = self.fixtures_dir / "config_enabled.toml"
        generator = CommitConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        commit_config = generator.validate_commit_config(config)
        
        self.assertIsNotNone(commit_config)
        self.assertTrue(commit_config['enabled'])
        self.assertEqual(commit_config['vcs'], 'git')
        
    def test_validate_commit_config_disabled(self):
        """Test validation with disabled commit configuration."""
        config_path = self.fixtures_dir / "config_disabled.toml"
        generator = CommitConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        
        with patch('builtins.print') as mock_print:
            commit_config = generator.validate_commit_config(config)
            
        self.assertIsNone(commit_config)
        mock_print.assert_called_with("Commit command is disabled (enabled = false)")
        
    def test_validate_commit_config_non_git_vcs(self):
        """Test validation with non-git VCS."""
        config_path = self.fixtures_dir / "config_svn.toml"
        generator = CommitConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        
        with patch('builtins.print') as mock_print:
            commit_config = generator.validate_commit_config(config)
            
        self.assertIsNone(commit_config)
        mock_print.assert_called_with("VCS 'svn' is not supported (only 'git' is supported)")
        
    def test_validate_and_read_template_default(self):
        """Test template validation and reading for default template."""
        config_path = self.fixtures_dir / "config_enabled.toml"
        generator = CommitConfigGenerator(str(config_path))
        
        commit_config = {'template': 'default', 'template_file': ''}
        
        # Mock the default template file reading
        expected_content = "# Default Template Content"
        with patch('builtins.open', mock_open(read_data=expected_content)):
            template_content = generator.validate_and_read_template(commit_config)
            
        self.assertEqual(template_content, expected_content)
        
    def test_validate_and_read_template_custom_valid(self):
        """Test template validation and reading for valid custom template."""
        config_path = self.fixtures_dir / "config_custom_valid.toml"
        generator = CommitConfigGenerator(str(config_path))
        
        # Set the project root to resolve paths correctly
        generator.project_root = project_root
        
        config = generator.load_toml_config()
        commit_config = config['opencode']['commands']['commit']
        
        template_content = generator.validate_and_read_template(commit_config)
        
        self.assertIn("Custom Commit Template", template_content)
        self.assertIn("testing purposes", template_content)
        
    def test_validate_and_read_template_custom_empty_file(self):
        """Test template validation with custom template but empty template_file."""
        config_path = self.fixtures_dir / "config_custom_empty_file.toml"
        generator = CommitConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        commit_config = config['opencode']['commands']['commit']
        
        with self.assertRaises(ValueError) as context:
            generator.validate_and_read_template(commit_config)
            
        self.assertIn("Custom template specified but template_file is empty", str(context.exception))
        
    def test_validate_and_read_template_custom_empty_template(self):
        """Test template validation with custom template pointing to empty file."""
        config_path = self.fixtures_dir / "config_custom_empty_template.toml"
        generator = CommitConfigGenerator(str(config_path))
        
        # Set the project root to resolve paths correctly
        generator.project_root = project_root
        
        config = generator.load_toml_config()
        commit_config = config['opencode']['commands']['commit']
        
        with self.assertRaises(ValueError) as context:
            generator.validate_and_read_template(commit_config)
            
        self.assertIn("Custom template file is empty", str(context.exception))
        
    def test_validate_and_read_template_custom_missing_file(self):
        """Test template validation with custom template pointing to non-existent file."""
        generator = CommitConfigGenerator("dummy.toml")
        
        commit_config = {
            'template': 'custom',
            'template_file': 'nonexistent_template.md'
        }
        
        with self.assertRaises(FileNotFoundError) as context:
            generator.validate_and_read_template(commit_config)
            
        self.assertIn("Custom template file not found", str(context.exception))
        
    def test_validate_and_read_template_unknown_type(self):
        """Test template validation with unknown template type."""
        generator = CommitConfigGenerator("dummy.toml")
        
        commit_config = {
            'template': 'unknown',
            'template_file': ''
        }
        
        with self.assertRaises(ValueError) as context:
            generator.validate_and_read_template(commit_config)
            
        self.assertIn("Unknown template type: unknown", str(context.exception))
        
    def test_generate_json_config(self):
        """Test JSON configuration generation."""
        generator = CommitConfigGenerator("dummy.toml")
        
        commit_config = {
            'agent': 'test-agent',
            'model': 'test-model'
        }
        template_content = "Test template content"
        
        json_config = generator.generate_json_config(commit_config, template_content)
        
        expected = {
            "$schema": "https://opencode.ai/config.json",
            "command": {
                "commit": {
                    "template": template_content,
                    "description": "Commit command",
                    "agent": "test-agent",
                    "model": "test-model"
                }
            }
        }
        
        self.assertEqual(json_config, expected)
        
    def test_generate_json_config_defaults(self):
        """Test JSON configuration generation with default values."""
        generator = CommitConfigGenerator("dummy.toml")
        
        commit_config = {}
        template_content = "Test template content"
        
        json_config = generator.generate_json_config(commit_config, template_content)
        
        self.assertEqual(json_config["command"]["commit"]["agent"], "build")
        self.assertEqual(json_config["command"]["commit"]["model"], "anthropic/claude-sonnet-4-20250514")
        
    def test_write_json_config(self):
        """Test JSON configuration file writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generator = CommitConfigGenerator("dummy.toml")
            generator.project_root = temp_path
            
            json_config = {
                "$schema": "https://opencode.ai/config.json",
                "command": {
                    "commit": {
                        "template": "test content",
                        "description": "Commit command",
                        "agent": "build",
                        "model": "test-model"
                    }
                }
            }
            
            with patch('builtins.print') as mock_print:
                generator.write_json_config(json_config)
                
            # Verify file was created
            output_file = temp_path / "ogc/generated/.opencode/command/commit.jsonc"
            self.assertTrue(output_file.exists())
            
            # Verify content
            with open(output_file, 'r') as f:
                written_config = json.load(f)
                
            self.assertEqual(written_config, json_config)
            mock_print.assert_called_once()


if __name__ == '__main__':
    unittest.main()
