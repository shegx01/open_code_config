#!/usr/bin/env python3
"""
Unit tests for the prompter command generator.

This module contains comprehensive unit tests for the PrompterConfigGenerator class,
covering configuration loading, validation, template handling, and file generation.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from prompter import PrompterConfigGenerator


class TestPrompterConfigGenerator(unittest.TestCase):
    """Test cases for PrompterConfigGenerator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.toml")
        self.generator = PrompterConfigGenerator(self.config_path)
        
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test PrompterConfigGenerator initialization."""
        generator = PrompterConfigGenerator("test/config.toml")
        self.assertEqual(str(generator.config_path), "test/config.toml")
        self.assertEqual(str(generator.project_root), "test")
    
    def test_load_toml_config_success(self):
        """Test successful TOML configuration loading."""
        toml_content = """
[opencode.commands]
prompter = { enabled = true, agent = "build", model = "test-model" }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        config = self.generator.load_toml_config()
        self.assertIn('opencode', config)
        self.assertIn('commands', config['opencode'])
        self.assertIn('prompter', config['opencode']['commands'])
    
    def test_load_toml_config_file_not_found(self):
        """Test TOML configuration loading with missing file."""
        with self.assertRaises(FileNotFoundError):
            self.generator.load_toml_config()
    
    def test_load_toml_config_invalid_toml(self):
        """Test TOML configuration loading with invalid TOML."""
        with open(self.config_path, 'w') as f:
            f.write("invalid toml content [[[")
        
        with self.assertRaises(ValueError):
            self.generator.load_toml_config()
    
    def test_validate_prompter_config_success(self):
        """Test successful prompter configuration validation."""
        config = {
            'opencode': {
                'commands': {
                    'prompter': {
                        'enabled': True,
                        'agent': 'build',
                        'model': 'test-model'
                    }
                }
            }
        }
        
        result = self.generator.validate_prompter_config(config)
        self.assertIsNotNone(result)
        self.assertEqual(result['agent'], 'build')
        self.assertEqual(result['model'], 'test-model')
    
    def test_validate_prompter_config_missing(self):
        """Test prompter configuration validation with missing config."""
        config = {'opencode': {'commands': {}}}
        
        result = self.generator.validate_prompter_config(config)
        self.assertIsNone(result)
    
    def test_validate_prompter_config_disabled(self):
        """Test prompter configuration validation when disabled."""
        config = {
            'opencode': {
                'commands': {
                    'prompter': {
                        'enabled': False,
                        'agent': 'build',
                        'model': 'test-model'
                    }
                }
            }
        }
        
        result = self.generator.validate_prompter_config(config)
        self.assertIsNone(result)
    
    def test_validate_and_read_template_default_with_base(self):
        """Test template validation with default template and base template included."""
        prompter_config = {
            'template': 'default',
            'include_base_template': True,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        # Create mock base template file
        base_template_path = self.generator.project_root / "ogc/control/commands/generic/prompter.md"
        base_template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(base_template_path, 'w') as f:
            f.write("Base template content")
        
        result = self.generator.validate_and_read_template(prompter_config)
        self.assertEqual(result, "Base template content")
    
    def test_validate_and_read_template_default_without_base(self):
        """Test template validation with default template but no base template."""
        prompter_config = {
            'template': 'default',
            'include_base_template': False,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(prompter_config)
        
        self.assertIn("No template content available", str(context.exception))
    
    def test_validate_and_read_template_default_base_missing(self):
        """Test template validation when base template file is missing."""
        prompter_config = {
            'template': 'default',
            'include_base_template': True,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(FileNotFoundError) as context:
            self.generator.validate_and_read_template(prompter_config)
        
        self.assertIn("Base template not found", str(context.exception))
    
    def test_validate_and_read_template_custom_success(self):
        """Test template validation with custom template."""
        custom_template_path = os.path.join(self.temp_dir, "custom.md")
        with open(custom_template_path, 'w') as f:
            f.write("Custom template content")
        
        prompter_config = {
            'template': 'custom',
            'template_file': custom_template_path,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(prompter_config)
        self.assertEqual(result, "Custom template content")
    
    def test_validate_and_read_template_custom_missing_file(self):
        """Test template validation with custom template but missing template_file."""
        prompter_config = {
            'template': 'custom',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(prompter_config)
        
        self.assertIn("Custom template specified but template_file is empty", str(context.exception))
    
    def test_validate_and_read_template_custom_file_not_found(self):
        """Test template validation with custom template file not found."""
        prompter_config = {
            'template': 'custom',
            'template_file': 'nonexistent.md',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(FileNotFoundError) as context:
            self.generator.validate_and_read_template(prompter_config)
        
        self.assertIn("Custom template file not found", str(context.exception))
    
    def test_validate_and_read_template_custom_empty_file(self):
        """Test template validation with empty custom template file."""
        custom_template_path = os.path.join(self.temp_dir, "empty.md")
        with open(custom_template_path, 'w') as f:
            f.write("")  # Empty file
        
        prompter_config = {
            'template': 'custom',
            'template_file': custom_template_path,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(prompter_config)
        
        self.assertIn("Custom template file is empty", str(context.exception))
    
    def test_validate_and_read_template_additional_files_merge(self):
        """Test template validation with additional files using merge strategy."""
        # Create base template
        base_template_path = self.generator.project_root / "ogc/control/commands/generic/prompter.md"
        base_template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(base_template_path, 'w') as f:
            f.write("Base template content")
        
        # Create additional file
        additional_file_path = os.path.join(self.temp_dir, "additional.md")
        with open(additional_file_path, 'w') as f:
            f.write("Additional content")
        
        prompter_config = {
            'template': 'default',
            'include_base_template': True,
            'additional_files': [additional_file_path],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(prompter_config)
        self.assertIn("Base template content", result)
        self.assertIn("Additional Files", result)
        self.assertIn("Additional content", result)
    
    def test_validate_and_read_template_additional_files_replace(self):
        """Test template validation with additional files using replace strategy."""
        # Create base template (should be ignored)
        base_template_path = self.generator.project_root / "ogc/control/commands/generic/prompter.md"
        base_template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(base_template_path, 'w') as f:
            f.write("Base template content")
        
        # Create additional file
        additional_file_path = os.path.join(self.temp_dir, "additional.md")
        with open(additional_file_path, 'w') as f:
            f.write("Additional content")
        
        prompter_config = {
            'template': 'default',
            'include_base_template': True,
            'additional_files': [additional_file_path],
            'additional_files_strategy': 'replace'
        }
        
        result = self.generator.validate_and_read_template(prompter_config)
        self.assertNotIn("Base template content", result)
        self.assertIn("Additional content", result)
    
    def test_validate_and_read_template_invalid_strategy(self):
        """Test template validation with invalid additional_files_strategy."""
        prompter_config = {
            'template': 'default',
            'include_base_template': False,
            'additional_files': [],
            'additional_files_strategy': 'invalid'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(prompter_config)
        
        self.assertIn("Invalid additional_files_strategy", str(context.exception))
    
    def test_process_additional_files_success(self):
        """Test processing additional files successfully."""
        # Create additional files
        file1_path = os.path.join(self.temp_dir, "file1.md")
        file2_path = os.path.join(self.temp_dir, "file2.md")
        
        with open(file1_path, 'w') as f:
            f.write("Content of file 1")
        with open(file2_path, 'w') as f:
            f.write("Content of file 2")
        
        result = self.generator._process_additional_files([file1_path, file2_path])
        
        self.assertIn("## file1.md", result)
        self.assertIn("Content of file 1", result)
        self.assertIn("## file2.md", result)
        self.assertIn("Content of file 2", result)
    
    def test_process_additional_files_empty_list(self):
        """Test processing empty additional files list."""
        result = self.generator._process_additional_files([])
        self.assertEqual(result, "")
    
    def test_process_additional_files_missing_file(self):
        """Test processing additional files with missing file."""
        with self.assertRaises(FileNotFoundError) as context:
            self.generator._process_additional_files(["nonexistent.md"])
        
        self.assertIn("Additional file not found", str(context.exception))
    
    def test_process_additional_files_empty_file(self):
        """Test processing additional files with empty file (should be skipped)."""
        empty_file_path = os.path.join(self.temp_dir, "empty.md")
        with open(empty_file_path, 'w') as f:
            f.write("")  # Empty file
        
        result = self.generator._process_additional_files([empty_file_path])
        self.assertEqual(result, "")
    
    def test_generate_yaml_config(self):
        """Test YAML configuration generation."""
        prompter_config = {
            'agent': 'build',
            'model': 'test-model'
        }
        template_content = "Test template content"
        
        result = self.generator.generate_yaml_config(prompter_config, template_content)
        
        expected = {
            "$schema": "https://opencode.ai/config.json",
            "command": {
                "prompter": {
                    "template": "Test template content",
                    "description": "Prompter command",
                    "agent": "build",
                    "model": "test-model"
                }
            }
        }
        
        self.assertEqual(result, expected)
    
    def test_write_yaml_config(self):
        """Test writing YAML configuration to file."""
        prompter_config = {
            'agent': 'build',
            'model': 'test-model'
        }
        template_content = "Test template content"
        output_path = "test_output.md"
        
        self.generator.write_yaml_config(prompter_config, template_content, output_path)
        
        output_file = self.generator.project_root / output_path
        self.assertTrue(output_file.exists())
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("---", content)
        self.assertIn("description: Prompter command", content)
        self.assertIn("agent: build", content)
        self.assertIn("model: test-model", content)
        self.assertIn("Test template content", content)
    
    def test_strip_frontmatter_with_frontmatter(self):
        """Test stripping YAML frontmatter from content."""
        content_with_frontmatter = """---
description: Test
agent: build
---

This is the main content
More content here"""
        
        result = self.generator._strip_frontmatter(content_with_frontmatter)
        expected = "This is the main content\nMore content here"
        self.assertEqual(result, expected)
    
    def test_strip_frontmatter_without_frontmatter(self):
        """Test stripping frontmatter from content without frontmatter."""
        content_without_frontmatter = "This is just regular content"
        
        result = self.generator._strip_frontmatter(content_without_frontmatter)
        self.assertEqual(result, content_without_frontmatter)
    
    def test_strip_frontmatter_incomplete_frontmatter(self):
        """Test stripping incomplete frontmatter (missing closing ---)."""
        content_incomplete = """---
description: Test
agent: build

This content has no closing frontmatter"""
        
        result = self.generator._strip_frontmatter(content_incomplete)
        self.assertEqual(result, content_incomplete)  # Should return original
    
    def test_generate_success(self):
        """Test successful generation workflow."""
        # Create config file
        toml_content = """
[opencode.commands]
prompter = { enabled = true, agent = "build", model = "test-model", include_base_template = true }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        # Create base template
        base_template_path = self.generator.project_root / "ogc/control/commands/generic/prompter.md"
        base_template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(base_template_path, 'w') as f:
            f.write("Base template content")
        
        result = self.generator.generate()
        self.assertTrue(result)
        
        # Check output file was created
        output_file = self.generator.project_root / "ogc/generated/.opencode/command/prompter.md"
        self.assertTrue(output_file.exists())
    
    def test_generate_disabled(self):
        """Test generation with disabled prompter command."""
        # Create config file with disabled prompter
        toml_content = """
[opencode.commands]
prompter = { enabled = false, agent = "build", model = "test-model" }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        result = self.generator.generate()
        self.assertFalse(result)
    
    def test_generate_missing_config(self):
        """Test generation with missing prompter configuration."""
        # Create config file without prompter
        toml_content = """
[opencode.commands]
other = { enabled = true }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        result = self.generator.generate()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
