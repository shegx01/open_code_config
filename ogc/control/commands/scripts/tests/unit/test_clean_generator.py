#!/usr/bin/env python3
"""
Unit tests for the CleanConfigGenerator class.

Tests all validation scenarios, template processing, language handling, and error handling.
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

# Import the clean module directly
sys.path.insert(0, str(project_root / "ogc" / "control" / "commands" / "scripts"))
from clean import CleanConfigGenerator


class TestCleanConfigGenerator(unittest.TestCase):
    """Test cases for CleanConfigGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.fixtures_dir = self.test_dir / "fixtures"
        
    def test_load_toml_config_success(self):
        """Test successful TOML configuration loading."""
        config_path = self.fixtures_dir / "clean_config_enabled.toml"
        generator = CleanConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        
        self.assertIn('opencode', config)
        self.assertIn('commands', config['opencode'])
        self.assertIn('clean', config['opencode']['commands'])
        
    def test_load_toml_config_file_not_found(self):
        """Test TOML loading with non-existent file."""
        generator = CleanConfigGenerator("nonexistent.toml")
        
        with self.assertRaises(FileNotFoundError) as context:
            generator.load_toml_config()
        
        self.assertIn("Configuration file not found", str(context.exception))
        
    def test_validate_clean_config_enabled(self):
        """Test validation of enabled clean configuration."""
        config = {
            'opencode': {
                'commands': {
                    'clean': {
                        'enabled': True,
                        'lang': 'elixir',
                        'agent': 'build',
                        'model': 'anthropic/claude-sonnet-4-20250514'
                    }
                }
            }
        }
        
        generator = CleanConfigGenerator()
        result = generator.validate_clean_config(config)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['enabled'], True)
        self.assertEqual(result['lang'], 'elixir')
        
    def test_validate_clean_config_disabled(self):
        """Test validation of disabled clean configuration."""
        config = {
            'opencode': {
                'commands': {
                    'clean': {
                        'enabled': False,
                        'lang': 'elixir'
                    }
                }
            }
        }
        
        generator = CleanConfigGenerator()
        result = generator.validate_clean_config(config)
        
        self.assertIsNone(result)
        
    def test_validate_clean_config_missing(self):
        """Test validation with missing clean configuration."""
        config = {
            'opencode': {
                'commands': {}
            }
        }
        
        generator = CleanConfigGenerator()
        result = generator.validate_clean_config(config)
        
        self.assertIsNone(result)
        
    def test_validate_clean_config_supported_languages(self):
        """Test validation with supported languages."""
        supported_langs = ['elixir', 'kotlin', 'typescript']
        
        for lang in supported_langs:
            config = {
                'opencode': {
                    'commands': {
                        'clean': {
                            'enabled': True,
                            'lang': lang
                        }
                    }
                }
            }
            
            generator = CleanConfigGenerator()
            result = generator.validate_clean_config(config)
            
            self.assertIsNotNone(result, f"Language {lang} should be supported")
            self.assertEqual(result['lang'], lang)
            
    def test_validate_clean_config_unsupported_language(self):
        """Test validation with unsupported language."""
        config = {
            'opencode': {
                'commands': {
                    'clean': {
                        'enabled': True,
                        'lang': 'python'  # Unsupported language
                    }
                }
            }
        }
        
        generator = CleanConfigGenerator()
        result = generator.validate_clean_config(config)
        
        self.assertIsNone(result)
        
    def test_validate_clean_config_empty_language(self):
        """Test validation with empty language (should be allowed)."""
        config = {
            'opencode': {
                'commands': {
                    'clean': {
                        'enabled': True,
                        'lang': ''
                    }
                }
            }
        }
        
        generator = CleanConfigGenerator()
        result = generator.validate_clean_config(config)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['lang'], '')
        
    def test_validate_and_read_template_with_base_and_language(self):
        """Test template reading with base template and language-specific template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock project structure
            base_template_dir = temp_path / "ogc/control/commands/generic/clean"
            base_template_dir.mkdir(parents=True)
            
            # Create base template
            base_template_path = base_template_dir / "base.md"
            base_template_path.write_text("# Base Template\nBase content")
            
            # Create language template
            lang_template_path = base_template_dir / "elixir.md"
            lang_template_path.write_text("# Elixir Template\nElixir content")
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'template': 'default',
                'lang': 'elixir',
                'include_base_template': True,
                'additional_files': [],
                'additional_files_strategy': 'merge'
            }
            
            result = generator.validate_and_read_template(clean_config)
            
            self.assertIn("Base Template", result)
            self.assertIn("Elixir Template", result)
            self.assertIn("Base content", result)
            self.assertIn("Elixir content", result)
            
    def test_validate_and_read_template_language_only(self):
        """Test template reading with language template only (no base)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock project structure
            base_template_dir = temp_path / "ogc/control/commands/generic/clean"
            base_template_dir.mkdir(parents=True)
            
            # Create base template (for fallback)
            base_template_path = base_template_dir / "base.md"
            base_template_path.write_text("# Base Template\nBase content")
            
            # Create language template
            lang_template_path = base_template_dir / "kotlin.md"
            lang_template_path.write_text("# Kotlin Template\nKotlin content")
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'template': 'default',
                'lang': 'kotlin',
                'include_base_template': False,
                'additional_files': [],
                'additional_files_strategy': 'merge'
            }
            
            result = generator.validate_and_read_template(clean_config)
            
            self.assertNotIn("Base Template", result)
            self.assertIn("Kotlin Template", result)
            self.assertIn("Kotlin content", result)
            
    def test_validate_and_read_template_base_only(self):
        """Test template reading with base template only (no language)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock project structure
            base_template_dir = temp_path / "ogc/control/commands/generic/clean"
            base_template_dir.mkdir(parents=True)
            
            # Create base template
            base_template_path = base_template_dir / "base.md"
            base_template_path.write_text("# Base Template\nBase content")
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'template': 'default',
                'lang': '',
                'include_base_template': True,
                'additional_files': [],
                'additional_files_strategy': 'merge'
            }
            
            result = generator.validate_and_read_template(clean_config)
            
            self.assertIn("Base Template", result)
            self.assertIn("Base content", result)
            
    def test_validate_and_read_template_missing_base_template(self):
        """Test template reading when base template is missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock project structure without base template
            base_template_dir = temp_path / "ogc/control/commands/generic/clean"
            base_template_dir.mkdir(parents=True)
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'template': 'default',
                'lang': '',
                'include_base_template': True,
                'additional_files': [],
                'additional_files_strategy': 'merge'
            }
            
            with self.assertRaises(FileNotFoundError) as context:
                generator.validate_and_read_template(clean_config)
            
            self.assertIn("No template files found", str(context.exception))
            
    def test_validate_and_read_template_custom_template(self):
        """Test template reading with custom template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create custom template
            custom_template_path = temp_path / "custom_clean.md"
            custom_template_path.write_text("# Custom Clean Template\nCustom content")
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'template': 'custom',
                'template_file': str(custom_template_path),
                'additional_files': [],
                'additional_files_strategy': 'merge'
            }
            
            result = generator.validate_and_read_template(clean_config)
            
            self.assertIn("Custom Clean Template", result)
            self.assertIn("Custom content", result)
            
    def test_validate_and_read_template_custom_template_missing(self):
        """Test template reading with missing custom template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'template': 'custom',
                'template_file': str(temp_path / "missing_template.md"),
                'additional_files': [],
                'additional_files_strategy': 'merge'
            }
            
            with self.assertRaises(FileNotFoundError) as context:
                generator.validate_and_read_template(clean_config)
            
            self.assertIn("Custom template file not found", str(context.exception))
            
    def test_validate_and_read_template_custom_template_empty_file(self):
        """Test template reading with empty custom template file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create empty custom template
            custom_template_path = temp_path / "empty_custom.md"
            custom_template_path.write_text("")
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'template': 'custom',
                'template_file': str(custom_template_path),
                'additional_files': [],
                'additional_files_strategy': 'merge'
            }
            
            with self.assertRaises(ValueError) as context:
                generator.validate_and_read_template(clean_config)
            
            self.assertIn("Custom template file is empty", str(context.exception))
            
    def test_validate_and_read_template_additional_files_merge(self):
        """Test template reading with additional files using merge strategy."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock project structure
            base_template_dir = temp_path / "ogc/control/commands/generic/clean"
            base_template_dir.mkdir(parents=True)
            
            # Create base template
            base_template_path = base_template_dir / "base.md"
            base_template_path.write_text("# Base Template\nBase content")
            
            # Create additional file
            additional_file_path = temp_path / "additional.md"
            additional_file_path.write_text("Additional content")
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'template': 'default',
                'lang': '',
                'include_base_template': True,
                'additional_files': [str(additional_file_path)],
                'additional_files_strategy': 'merge'
            }
            
            result = generator.validate_and_read_template(clean_config)
            
            self.assertIn("Base content", result)
            self.assertIn("Additional Files", result)
            self.assertIn("Additional content", result)
            
    def test_validate_and_read_template_additional_files_replace(self):
        """Test template reading with additional files using replace strategy."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create additional file
            additional_file_path = temp_path / "additional.md"
            additional_file_path.write_text("Additional content")
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'template': 'default',
                'lang': 'elixir',
                'include_base_template': True,
                'additional_files': [str(additional_file_path)],
                'additional_files_strategy': 'replace'
            }
            
            result = generator.validate_and_read_template(clean_config)
            
            # Should only contain additional file content, not base template
            self.assertNotIn("Base Template", result)
            self.assertIn("Additional content", result)
            
    def test_validate_and_read_template_invalid_strategy(self):
        """Test template reading with invalid additional files strategy."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'template': 'default',
                'additional_files': [],
                'additional_files_strategy': 'invalid_strategy'
            }
            
            with self.assertRaises(ValueError) as context:
                generator.validate_and_read_template(clean_config)
            
            self.assertIn("Invalid additional_files_strategy", str(context.exception))
            
    def test_generate_yaml_config(self):
        """Test YAML configuration generation."""
        generator = CleanConfigGenerator()
        
        clean_config = {
            'agent': 'build',
            'model': 'anthropic/claude-sonnet-4-20250514',
            'description': 'Test clean command'
        }
        
        template_content = "# Test Template\nTest content"
        
        result = generator.generate_yaml_config(clean_config, template_content)
        
        self.assertIn('$schema', result)
        self.assertIn('command', result)
        self.assertIn('clean', result['command'])
        self.assertEqual(result['command']['clean']['template'], template_content)
        self.assertEqual(result['command']['clean']['agent'], 'build')
        self.assertEqual(result['command']['clean']['model'], 'anthropic/claude-sonnet-4-20250514')
        
    def test_write_yaml_config(self):
        """Test writing YAML configuration to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create generator with temp directory
            config_path = temp_path / "ogc/config.toml"
            generator = CleanConfigGenerator(str(config_path))
            
            clean_config = {
                'agent': 'build',
                'model': 'anthropic/claude-sonnet-4-20250514',
                'description': 'Test clean command'
            }
            
            template_content = "# Test Template\nTest content"
            output_path = "test_output/clean.md"
            
            generator.write_yaml_config(clean_config, template_content, output_path)
            
            # Check if file was created
            output_file = temp_path / output_path
            self.assertTrue(output_file.exists())
            
            # Check file content
            content = output_file.read_text()
            self.assertIn("---", content)
            self.assertIn("description: Test clean command", content)
            self.assertIn("agent: build", content)
            self.assertIn("model: anthropic/claude-sonnet-4-20250514", content)
            self.assertIn("Test Template", content)
            self.assertIn("Test content", content)
            
    def test_strip_frontmatter(self):
        """Test YAML frontmatter stripping."""
        generator = CleanConfigGenerator()
        
        content_with_frontmatter = """---
description: Test
agent: build
---

# Template Content
This is the actual content."""
        
        result = generator._strip_frontmatter(content_with_frontmatter)
        
        self.assertNotIn("---", result)
        self.assertNotIn("description: Test", result)
        self.assertIn("# Template Content", result)
        self.assertIn("This is the actual content.", result)
        
    def test_strip_frontmatter_no_frontmatter(self):
        """Test frontmatter stripping with content that has no frontmatter."""
        generator = CleanConfigGenerator()
        
        content_without_frontmatter = """# Template Content
This is the actual content."""
        
        result = generator._strip_frontmatter(content_without_frontmatter)
        
        self.assertEqual(result, content_without_frontmatter)
        
    def test_generate_success(self):
        """Test successful generation process."""
        config_path = self.fixtures_dir / "clean_config_enabled.toml"
        
        with patch.object(CleanConfigGenerator, 'validate_and_read_template') as mock_template:
            with patch.object(CleanConfigGenerator, 'write_yaml_config') as mock_write:
                mock_template.return_value = "Test template content"
                
                generator = CleanConfigGenerator(str(config_path))
                result = generator.generate()
                
                self.assertTrue(result)
                mock_template.assert_called_once()
                mock_write.assert_called_once()
                
    def test_generate_disabled_config(self):
        """Test generation with disabled configuration."""
        config_path = self.fixtures_dir / "clean_config_disabled.toml"
        
        generator = CleanConfigGenerator(str(config_path))
        result = generator.generate()
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
