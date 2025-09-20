#!/usr/bin/env python3
"""
Unit tests for the test command generator.

This test suite validates all aspects of the TestConfigGenerator class,
including configuration loading, validation, template handling, and output generation.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

# Add the scripts directory to the path to import the test generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test import TestConfigGenerator


class TestTestConfigGenerator(unittest.TestCase):
    """Test cases for TestConfigGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.toml"
        self.generator = TestConfigGenerator(str(self.config_path))
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test TestConfigGenerator initialization."""
        generator = TestConfigGenerator("ogc/config.toml")
        self.assertEqual(generator.config_path, Path("ogc/config.toml"))
        self.assertEqual(generator.project_root, Path("ogc/config.toml").parent.parent)
    
    def test_load_toml_config_success(self):
        """Test successful TOML configuration loading."""
        toml_content = """
[opencode.commands]
test = { enabled = true, lang = "elixir" }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        config = self.generator.load_toml_config()
        self.assertIn('opencode', config)
        self.assertIn('commands', config['opencode'])
        self.assertIn('test', config['opencode']['commands'])
    
    def test_load_toml_config_file_not_found(self):
        """Test TOML loading with missing file."""
        with self.assertRaises(FileNotFoundError) as context:
            self.generator.load_toml_config()
        self.assertIn("Configuration file not found", str(context.exception))
    
    def test_load_toml_config_invalid_toml(self):
        """Test TOML loading with invalid syntax."""
        with open(self.config_path, 'w') as f:
            f.write("invalid toml content [[[")
        
        with self.assertRaises(ValueError) as context:
            self.generator.load_toml_config()
        self.assertIn("Invalid TOML configuration", str(context.exception))
    
    def test_validate_test_config_enabled(self):
        """Test validation of enabled test configuration."""
        config = {
            'opencode': {
                'commands': {
                    'test': {
                        'enabled': True,
                        'lang': 'elixir',
                        'agent': 'build',
                        'model': 'anthropic/claude-sonnet-4-20250514'
                    }
                }
            }
        }
        
        result = self.generator.validate_test_config(config)
        self.assertIsNotNone(result)
        self.assertEqual(result['enabled'], True)
        self.assertEqual(result['lang'], 'elixir')
    
    def test_validate_test_config_disabled(self):
        """Test validation of disabled test configuration."""
        config = {
            'opencode': {
                'commands': {
                    'test': {
                        'enabled': False,
                        'lang': 'elixir'
                    }
                }
            }
        }
        
        result = self.generator.validate_test_config(config)
        self.assertIsNone(result)
    
    def test_validate_test_config_missing(self):
        """Test validation with missing test configuration."""
        config = {
            'opencode': {
                'commands': {}
            }
        }
        
        result = self.generator.validate_test_config(config)
        self.assertIsNone(result)
    
    def test_validate_test_config_supported_languages(self):
        """Test validation with supported languages."""
        supported_langs = ['elixir', 'kotlin', 'typescript']
        
        for lang in supported_langs:
            config = {
                'opencode': {
                    'commands': {
                        'test': {
                            'enabled': True,
                            'lang': lang
                        }
                    }
                }
            }
            
            result = self.generator.validate_test_config(config)
            self.assertIsNotNone(result, f"Language {lang} should be supported")
            self.assertEqual(result['lang'], lang)
    
    def test_validate_test_config_unsupported_language(self):
        """Test validation with unsupported language."""
        config = {
            'opencode': {
                'commands': {
                    'test': {
                        'enabled': True,
                        'lang': 'python'  # Unsupported language
                    }
                }
            }
        }
        
        result = self.generator.validate_test_config(config)
        self.assertIsNone(result)
    
    def test_validate_test_config_no_language(self):
        """Test validation with no language specified."""
        config = {
            'opencode': {
                'commands': {
                    'test': {
                        'enabled': True
                    }
                }
            }
        }
        
        result = self.generator.validate_test_config(config)
        self.assertIsNotNone(result)
    
    def test_validate_and_read_template_invalid_strategy(self):
        """Test template validation with invalid additional_files_strategy."""
        test_config = {
            'template': 'default',
            'additional_files_strategy': 'invalid_strategy'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(test_config)
        self.assertIn("Invalid additional_files_strategy", str(context.exception))
    
    @patch('builtins.open', new_callable=mock_open, read_data="# Base Template Content")
    @patch('pathlib.Path.exists')
    def test_validate_and_read_template_base_only(self, mock_exists, mock_file):
        """Test template reading with base template only."""
        mock_exists.return_value = True
        
        test_config = {
            'template': 'default',
            'include_base_template': True,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(test_config)
        self.assertEqual(result, "# Base Template Content")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_validate_and_read_template_base_and_language(self, mock_exists, mock_file):
        """Test template reading with base and language templates."""
        mock_exists.return_value = True
        
        # Mock different content for base and language templates
        def mock_read_side_effect(*args, **kwargs):
            if 'base.md' in str(args[0]):
                return mock_open(read_data="# Base Template Content").return_value
            elif 'elixir.md' in str(args[0]):
                return mock_open(read_data="# Elixir Template Content").return_value
            return mock_open(read_data="").return_value
        
        mock_file.side_effect = mock_read_side_effect
        
        test_config = {
            'template': 'default',
            'lang': 'elixir',
            'include_base_template': True,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(test_config)
        self.assertIn("Base Template Content", result)
        self.assertIn("Elixir Template Content", result)
    
    @patch('builtins.open', new_callable=mock_open, read_data="# Custom Template Content")
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_validate_and_read_template_custom(self, mock_stat, mock_exists, mock_file):
        """Test template reading with custom template."""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 100  # Non-empty file
        
        test_config = {
            'template': 'custom',
            'template_file': 'custom_template.md',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(test_config)
        self.assertEqual(result, "# Custom Template Content")
    
    def test_validate_and_read_template_custom_missing_file(self):
        """Test custom template with missing template_file."""
        test_config = {
            'template': 'custom',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(test_config)
        self.assertIn("Custom template specified but template_file is empty", str(context.exception))
    
    @patch('pathlib.Path.exists')
    def test_validate_and_read_template_custom_file_not_found(self, mock_exists):
        """Test custom template with non-existent file."""
        mock_exists.return_value = False
        
        test_config = {
            'template': 'custom',
            'template_file': 'nonexistent.md',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(FileNotFoundError) as context:
            self.generator.validate_and_read_template(test_config)
        self.assertIn("Custom template file not found", str(context.exception))
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_validate_and_read_template_custom_empty_file(self, mock_stat, mock_exists):
        """Test custom template with empty file."""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 0  # Empty file
        
        test_config = {
            'template': 'custom',
            'template_file': 'empty.md',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(test_config)
        self.assertIn("Custom template file is empty", str(context.exception))
    
    def test_validate_and_read_template_unknown_type(self):
        """Test template validation with unknown template type."""
        test_config = {
            'template': 'unknown_type',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(test_config)
        self.assertIn("Unknown template type", str(context.exception))
    
    @patch('builtins.open', new_callable=mock_open, read_data="# Additional File Content")
    @patch('pathlib.Path.exists')
    def test_process_additional_files_merge_strategy(self, mock_exists, mock_file):
        """Test additional files processing with merge strategy."""
        mock_exists.return_value = True
        
        test_config = {
            'template': 'default',
            'additional_files': ['additional.md'],
            'additional_files_strategy': 'merge',
            'include_base_template': False
        }
        
        # Mock base template reading
        with patch.object(self.generator, 'validate_and_read_template') as mock_validate:
            mock_validate.return_value = "# Main Template\n\n# Additional Files\n\n## additional.md\n\n# Additional File Content"
            
            result = self.generator.validate_and_read_template(test_config)
            self.assertIn("Additional File Content", result)
    
    @patch('builtins.open', new_callable=mock_open, read_data="# Additional File Content")
    @patch('pathlib.Path.exists')
    def test_process_additional_files_replace_strategy(self, mock_exists, mock_file):
        """Test additional files processing with replace strategy."""
        mock_exists.return_value = True
        
        additional_files = ['additional.md']
        result = self.generator._process_additional_files(additional_files)
        self.assertIn("Additional File Content", result)
        self.assertIn("## additional.md", result)
    
    def test_process_additional_files_empty_list(self):
        """Test additional files processing with empty list."""
        result = self.generator._process_additional_files([])
        self.assertEqual(result, "")
    
    @patch('pathlib.Path.exists')
    def test_process_additional_files_missing_file(self, mock_exists):
        """Test additional files processing with missing file."""
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError) as context:
            self.generator._process_additional_files(['missing.md'])
        self.assertIn("Additional file not found", str(context.exception))
    
    def test_generate_yaml_config(self):
        """Test YAML configuration generation."""
        test_config = {
            'agent': 'build',
            'model': 'anthropic/claude-sonnet-4-20250514'
        }
        template_content = "# Test Template"
        
        result = self.generator.generate_yaml_config(test_config, template_content)
        
        expected = {
            "$schema": "https://opencode.ai/config.json",
            "command": {
                "test": {
                    "template": "# Test Template",
                    "description": "Test command",
                    "agent": "build",
                    "model": "anthropic/claude-sonnet-4-20250514"
                }
            }
        }
        
        self.assertEqual(result, expected)
    
    def test_generate_yaml_config_defaults(self):
        """Test YAML configuration generation with defaults."""
        test_config = {}
        template_content = "# Test Template"
        
        result = self.generator.generate_yaml_config(test_config, template_content)
        
        self.assertEqual(result["command"]["test"]["agent"], "build")
        self.assertEqual(result["command"]["test"]["model"], "anthropic/claude-sonnet-4-20250514")
    
    def test_strip_frontmatter_with_frontmatter(self):
        """Test frontmatter stripping with YAML frontmatter present."""
        content = """---
description: Test
agent: build
---

# Main Content
This is the main content."""
        
        result = self.generator._strip_frontmatter(content)
        expected = """# Main Content
This is the main content."""
        
        self.assertEqual(result, expected)
    
    def test_strip_frontmatter_without_frontmatter(self):
        """Test frontmatter stripping without YAML frontmatter."""
        content = """# Main Content
This is the main content."""
        
        result = self.generator._strip_frontmatter(content)
        self.assertEqual(result, content)
    
    def test_strip_frontmatter_with_leading_empty_lines(self):
        """Test frontmatter stripping with leading empty lines after frontmatter."""
        content = """---
description: Test
---


# Main Content"""
        
        result = self.generator._strip_frontmatter(content)
        self.assertEqual(result, "# Main Content")
    
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_yaml_config(self, mock_file, mock_mkdir):
        """Test YAML configuration writing."""
        test_config = {
            'description': 'Test command',
            'agent': 'build',
            'model': 'anthropic/claude-sonnet-4-20250514'
        }
        template_content = "# Test Template"
        
        self.generator.write_yaml_config(test_config, template_content)
        
        # Verify file was opened for writing
        mock_file.assert_called_once()
        
        # Verify directory creation
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        
        # Verify content written
        written_content = mock_file().write.call_args[0][0]
        self.assertIn("---", written_content)
        self.assertIn("description: Test command", written_content)
        self.assertIn("agent: build", written_content)
        self.assertIn("model: anthropic/claude-sonnet-4-20250514", written_content)
        self.assertIn("# Test Template", written_content)


if __name__ == '__main__':
    unittest.main()
