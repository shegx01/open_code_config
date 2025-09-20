#!/usr/bin/env python3
"""
Unit tests for the OptimizerConfigGenerator class.

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
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the optimizer module directly
sys.path.insert(0, str(project_root / "control" / "commands" / "scripts"))
from optimizer import OptimizerConfigGenerator


class TestOptimizerConfigGenerator(unittest.TestCase):
    """Test cases for OptimizerConfigGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.fixtures_dir = self.test_dir / "fixtures"

    def test_load_toml_config_success(self):
        """Test successful TOML configuration loading."""
        config_path = self.fixtures_dir / "optimizer_config_enabled.toml"
        generator = OptimizerConfigGenerator(str(config_path))

        config = generator.load_toml_config()

        self.assertIn('opencode', config)
        self.assertIn('commands', config['opencode'])
        self.assertIn('optimizer', config['opencode']['commands'])

    def test_load_toml_config_file_not_found(self):
        """Test TOML loading with non-existent file."""
        generator = OptimizerConfigGenerator("nonexistent.toml")

        with self.assertRaises(FileNotFoundError) as context:
            generator.load_toml_config()

        self.assertIn("Configuration file not found", str(context.exception))

    def test_load_toml_config_invalid_toml(self):
        """Test TOML loading with invalid TOML syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("invalid toml [[[")
            temp_path = f.name

        try:
            generator = OptimizerConfigGenerator(temp_path)
            with self.assertRaises(ValueError) as context:
                generator.load_toml_config()

            self.assertIn("Invalid TOML configuration", str(context.exception))
        finally:
            os.unlink(temp_path)

    def test_validate_optimizer_config_enabled(self):
        """Test validation with enabled optimizer configuration."""
        config_path = self.fixtures_dir / "optimizer_config_enabled.toml"
        generator = OptimizerConfigGenerator(str(config_path))

        config = generator.load_toml_config()
        optimizer_config = generator.validate_optimizer_config(config)

        self.assertIsNotNone(optimizer_config)
        self.assertTrue(optimizer_config['enabled'])
        self.assertEqual(optimizer_config['lang'], 'elixir')

    def test_validate_optimizer_config_disabled(self):
        """Test validation with disabled optimizer configuration."""
        config_path = self.fixtures_dir / "optimizer_config_disabled.toml"
        generator = OptimizerConfigGenerator(str(config_path))

        config = generator.load_toml_config()
        optimizer_config = generator.validate_optimizer_config(config)

        self.assertIsNone(optimizer_config)

    def test_validate_optimizer_config_missing(self):
        """Test validation with missing optimizer configuration."""
        config = {'opencode': {'commands': {}}}
        generator = OptimizerConfigGenerator()

        optimizer_config = generator.validate_optimizer_config(config)

        self.assertIsNone(optimizer_config)

    def test_validate_optimizer_config_supported_languages(self):
        """Test validation with supported languages."""
        supported_langs = ['elixir', 'kotlin', 'typescript']

        for lang in supported_langs:
            config = {
                'opencode': {
                    'commands': {
                        'optimizer': {
                            'enabled': True,
                            'lang': lang,
                            'agent': 'build',
                            'model': 'anthropic/claude-sonnet-4-20250514'
                        }
                    }
                }
            }

            generator = OptimizerConfigGenerator()
            optimizer_config = generator.validate_optimizer_config(config)

            self.assertIsNotNone(optimizer_config, f"Language {lang} should be supported")
            self.assertEqual(optimizer_config['lang'], lang)

    def test_validate_optimizer_config_unsupported_language(self):
        """Test validation with unsupported language."""
        config_path = self.fixtures_dir / "optimizer_config_unsupported_lang.toml"
        generator = OptimizerConfigGenerator(str(config_path))

        config = generator.load_toml_config()
        optimizer_config = generator.validate_optimizer_config(config)

        self.assertIsNone(optimizer_config)

    def test_validate_and_read_template_default_with_base_and_lang(self):
        """Test template validation with default template, base template, and language template."""
        optimizer_config = {
            'template': 'default',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge',
            'lang': 'elixir',
            'include_base_template': True
        }

        # Mock the file system
        base_content = "# Base Optimizer Template\n\nBase content"
        lang_content = "# Elixir Optimizer Template\n\nElixir-specific content"

        with patch('builtins.open', mock_open()) as mock_file:
            with patch('pathlib.Path.exists') as mock_exists:
                mock_exists.return_value = True

                # Configure mock to return different content for different files
                def side_effect(*args, **kwargs):
                    if 'base.md' in str(args[0]):
                        return mock_open(read_data=base_content).return_value
                    elif 'elixir.md' in str(args[0]):
                        return mock_open(read_data=lang_content).return_value
                    return mock_open().return_value

                mock_file.side_effect = side_effect

                generator = OptimizerConfigGenerator()
                template_content = generator.validate_and_read_template(optimizer_config)

                self.assertIn("Base content", template_content)
                self.assertIn("Elixir-specific content", template_content)

    def test_validate_and_read_template_default_base_only(self):
        """Test template validation with default template and base template only."""
        optimizer_config = {
            'template': 'default',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge',
            'lang': '',
            'include_base_template': True
        }

        base_content = "# Base Optimizer Template\n\nBase content"

        with patch('builtins.open', mock_open(read_data=base_content)) as mock_file:
            with patch('pathlib.Path.exists') as mock_exists:
                mock_exists.return_value = True

                generator = OptimizerConfigGenerator()
                template_content = generator.validate_and_read_template(optimizer_config)

                self.assertEqual(template_content, base_content)

    def test_validate_and_read_template_default_lang_only(self):
        """Test template validation with default template and language template only."""
        optimizer_config = {
            'template': 'default',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge',
            'lang': 'kotlin',
            'include_base_template': False
        }

        lang_content = "# Kotlin Optimizer Template\n\nKotlin-specific content"

        with patch('builtins.open', mock_open(read_data=lang_content)) as mock_file:
            with patch('pathlib.Path.exists') as mock_exists:
                def exists_side_effect(path):
                    return 'kotlin.md' in str(path)

                mock_exists.side_effect = exists_side_effect

                generator = OptimizerConfigGenerator()
                template_content = generator.validate_and_read_template(optimizer_config)

                self.assertEqual(template_content, lang_content)

    def test_validate_and_read_template_default_fallback_to_base(self):
        """Test template validation with fallback to base template when no specific templates found."""
        optimizer_config = {
            'template': 'default',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge',
            'lang': '',
            'include_base_template': False
        }

        base_content = "# Base Optimizer Template\n\nFallback base content"

        with patch('builtins.open', mock_open(read_data=base_content)) as mock_file:
            with patch('pathlib.Path.exists') as mock_exists:
                mock_exists.return_value = True

                generator = OptimizerConfigGenerator()
                template_content = generator.validate_and_read_template(optimizer_config)

                self.assertEqual(template_content, base_content)

    def test_validate_and_read_template_default_no_templates_found(self):
        """Test template validation when no templates are found."""
        optimizer_config = {
            'template': 'default',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge',
            'lang': '',
            'include_base_template': False
        }

        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False

            generator = OptimizerConfigGenerator()

            with self.assertRaises(FileNotFoundError) as context:
                generator.validate_and_read_template(optimizer_config)

            self.assertIn("No template files found", str(context.exception))

    def test_validate_and_read_template_custom_valid(self):
        """Test template validation with valid custom template."""
        custom_template_path = self.fixtures_dir / "optimizer_custom_template.md"

        optimizer_config = {
            'template': 'custom',
            'template_file': str(custom_template_path),
            'additional_files': [],
            'additional_files_strategy': 'merge',
            'lang': 'elixir',
            'include_base_template': True
        }

        generator = OptimizerConfigGenerator()
        template_content = generator.validate_and_read_template(optimizer_config)

        self.assertIn("Custom Optimizer Template", template_content)
        self.assertIn("optimize the code", template_content)

    def test_validate_and_read_template_custom_empty_file(self):
        """Test template validation with empty custom template file."""
        optimizer_config = {
            'template': 'custom',
            'template_file': str(self.fixtures_dir / "empty_template.md"),
            'additional_files': [],
            'additional_files_strategy': 'merge',
            'lang': 'elixir',
            'include_base_template': True
        }

        generator = OptimizerConfigGenerator()

        with self.assertRaises(ValueError) as context:
            generator.validate_and_read_template(optimizer_config)

        self.assertIn("Custom template file is empty", str(context.exception))

    def test_validate_and_read_template_custom_missing_file(self):
        """Test template validation with missing custom template file."""
        optimizer_config = {
            'template': 'custom',
            'template_file': 'nonexistent_template.md',
            'additional_files': [],
            'additional_files_strategy': 'merge',
            'lang': 'elixir',
            'include_base_template': True
        }

        generator = OptimizerConfigGenerator()

        with self.assertRaises(FileNotFoundError) as context:
            generator.validate_and_read_template(optimizer_config)

        self.assertIn("Custom template file not found", str(context.exception))

    def test_validate_and_read_template_custom_no_template_file(self):
        """Test template validation with custom template but no template_file specified."""
        optimizer_config = {
            'template': 'custom',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge',
            'lang': 'elixir',
            'include_base_template': True
        }

        generator = OptimizerConfigGenerator()

        with self.assertRaises(ValueError) as context:
            generator.validate_and_read_template(optimizer_config)

        self.assertIn("Custom template specified but template_file is empty", str(context.exception))

    def test_validate_and_read_template_unknown_template_type(self):
        """Test template validation with unknown template type."""
        optimizer_config = {
            'template': 'unknown',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge',
            'lang': 'elixir',
            'include_base_template': True
        }

        generator = OptimizerConfigGenerator()

        with self.assertRaises(ValueError) as context:
            generator.validate_and_read_template(optimizer_config)

        self.assertIn("Unknown template type: unknown", str(context.exception))

    def test_validate_and_read_template_invalid_strategy(self):
        """Test template validation with invalid additional_files_strategy."""
        optimizer_config = {
            'template': 'default',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'invalid',
            'lang': 'elixir',
            'include_base_template': True
        }

        generator = OptimizerConfigGenerator()

        with self.assertRaises(ValueError) as context:
            generator.validate_and_read_template(optimizer_config)

        self.assertIn("Invalid additional_files_strategy: invalid", str(context.exception))

    def test_validate_and_read_template_additional_files_merge(self):
        """Test template validation with additional files using merge strategy."""
        custom_template_path = self.fixtures_dir / "optimizer_custom_template.md"

        optimizer_config = {
            'template': 'custom',
            'template_file': str(custom_template_path),
            'additional_files': [str(custom_template_path)],
            'additional_files_strategy': 'merge',
            'lang': 'elixir',
            'include_base_template': False
        }

        generator = OptimizerConfigGenerator()
        template_content = generator.validate_and_read_template(optimizer_config)

        self.assertIn("Custom Optimizer Template", template_content)
        self.assertIn("# Additional Files", template_content)
        self.assertIn("## optimizer_custom_template.md", template_content)

    def test_validate_and_read_template_additional_files_replace(self):
        """Test template validation with additional files using replace strategy."""
        custom_template_path = self.fixtures_dir / "optimizer_custom_template.md"

        optimizer_config = {
            'template': 'custom',
            'template_file': str(custom_template_path),
            'additional_files': [str(custom_template_path)],
            'additional_files_strategy': 'replace',
            'lang': 'elixir',
            'include_base_template': False
        }

        generator = OptimizerConfigGenerator()
        template_content = generator.validate_and_read_template(optimizer_config)

        # Should only contain additional files content, not the main template
        self.assertNotIn("Custom Optimizer Template", template_content)
        self.assertIn("## optimizer_custom_template.md", template_content)

    def test_process_additional_files_empty_list(self):
        """Test processing empty additional files list."""
        generator = OptimizerConfigGenerator()
        result = generator._process_additional_files([])

        self.assertEqual(result, "")

    def test_process_additional_files_missing_file(self):
        """Test processing additional files with missing file."""
        generator = OptimizerConfigGenerator()

        with self.assertRaises(FileNotFoundError) as context:
            generator._process_additional_files(["nonexistent.md"])

        self.assertIn("Additional file not found", str(context.exception))

    def test_generate_yaml_config(self):
        """Test YAML configuration generation."""
        optimizer_config = {
            'agent': 'build',
            'model': 'anthropic/claude-sonnet-4-20250514'
        }
        template_content = "# Test Template"

        generator = OptimizerConfigGenerator()
        yaml_config = generator.generate_yaml_config(optimizer_config, template_content)

        self.assertEqual(yaml_config['$schema'], 'https://opencode.ai/config.json')
        self.assertIn('command', yaml_config)
        self.assertIn('optimizer', yaml_config['command'])
        self.assertEqual(yaml_config['command']['optimizer']['template'], template_content)
        self.assertEqual(yaml_config['command']['optimizer']['agent'], 'build')
        self.assertEqual(yaml_config['command']['optimizer']['model'], 'anthropic/claude-sonnet-4-20250514')

    def test_write_yaml_config(self):
        """Test writing YAML configuration to file."""
        optimizer_config = {
            'description': 'Test optimizer command',
            'agent': 'build',
            'model': 'anthropic/claude-sonnet-4-20250514'
        }
        template_content = "# Test Template\n\nTest content"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = f"{temp_dir}/optimizer.md"

            generator = OptimizerConfigGenerator()
            generator.project_root = Path(temp_dir)
            generator.write_yaml_config(optimizer_config, template_content, "optimizer.md")

            # Verify file was created
            output_file = Path(temp_dir) / "optimizer.md"
            self.assertTrue(output_file.exists())

            # Verify content
            with open(output_file, 'r') as f:
                content = f.read()

            self.assertIn("---", content)
            self.assertIn("description: Test optimizer command", content)
            self.assertIn("agent: build", content)
            self.assertIn("model: anthropic/claude-sonnet-4-20250514", content)
            self.assertIn("# Test Template", content)
            self.assertIn("Test content", content)

    def test_strip_frontmatter_with_frontmatter(self):
        """Test stripping YAML frontmatter from content."""
        content_with_frontmatter = """---
description: Test
agent: build
---

# Template Content

This is the actual content."""

        generator = OptimizerConfigGenerator()
        stripped_content = generator._strip_frontmatter(content_with_frontmatter)

        self.assertNotIn("---", stripped_content)
        self.assertNotIn("description: Test", stripped_content)
        self.assertIn("# Template Content", stripped_content)
        self.assertIn("This is the actual content.", stripped_content)

    def test_strip_frontmatter_without_frontmatter(self):
        """Test stripping frontmatter from content without frontmatter."""
        content_without_frontmatter = """# Template Content

This is the actual content."""

        generator = OptimizerConfigGenerator()
        stripped_content = generator._strip_frontmatter(content_without_frontmatter)

        self.assertEqual(stripped_content, content_without_frontmatter)

    def test_generate_success(self):
        """Test successful generation workflow."""
        config_path = self.fixtures_dir / "optimizer_config_enabled.toml"

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock template files
            optimizer_dir = Path(temp_dir) / "control" / "commands" / "generic" / "optimizer"
            optimizer_dir.mkdir(parents=True)

            base_template = optimizer_dir / "base.md"
            base_template.write_text("# Base Optimizer Template")

            lang_template = optimizer_dir / "elixir.md"
            lang_template.write_text("# Elixir Optimizer Template")

            generator = OptimizerConfigGenerator(str(config_path))
            generator.project_root = Path(temp_dir)

            result = generator.generate()

            self.assertTrue(result)

            # Verify output file was created
            output_file = Path(temp_dir) / "generated" / ".opencode" / "command" / "optimizer.md"
            self.assertTrue(output_file.exists())

    def test_generate_disabled_config(self):
        """Test generation with disabled configuration."""
        config_path = self.fixtures_dir / "optimizer_config_disabled.toml"

        generator = OptimizerConfigGenerator(str(config_path))
        result = generator.generate()

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
