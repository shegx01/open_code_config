#!/usr/bin/env python3
"""
Unit tests for the ContextConfigGenerator class.

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

# Import the context module directly
scripts_path = str(project_root / "ogc" / "control" / "commands" / "scripts")
sys.path.insert(0, scripts_path)

# Try different import approaches
try:
    from context import ContextConfigGenerator
except ImportError:
    # Alternative import approach
    import importlib.util
    spec = importlib.util.spec_from_file_location("context", scripts_path + "/context.py")
    context_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(context_module)
    ContextConfigGenerator = context_module.ContextConfigGenerator


class TestContextConfigGenerator(unittest.TestCase):
    """Test cases for ContextConfigGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.fixtures_dir = self.test_dir / "fixtures"
        
    def test_load_toml_config_success(self):
        """Test successful TOML configuration loading."""
        config_path = self.fixtures_dir / "context_config_enabled.toml"
        generator = ContextConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        
        self.assertIn('opencode', config)
        self.assertIn('commands', config['opencode'])
        self.assertIn('context', config['opencode']['commands'])
        
    def test_load_toml_config_file_not_found(self):
        """Test TOML loading with non-existent file."""
        generator = ContextConfigGenerator("nonexistent.toml")
        
        with self.assertRaises(FileNotFoundError) as context:
            generator.load_toml_config()
        
        self.assertIn("Configuration file not found", str(context.exception))
        
    def test_load_toml_config_invalid_toml(self):
        """Test TOML loading with invalid TOML syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("invalid toml content [[[")
            temp_path = f.name
            
        try:
            generator = ContextConfigGenerator(temp_path)
            with self.assertRaises(ValueError) as context:
                generator.load_toml_config()
            
            self.assertIn("Invalid TOML configuration", str(context.exception))
        finally:
            os.unlink(temp_path)
    
    def test_validate_context_config_enabled(self):
        """Test validation with enabled context configuration."""
        config_path = self.fixtures_dir / "context_config_enabled.toml"
        generator = ContextConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        context_config = generator.validate_context_config(config)
        
        self.assertIsNotNone(context_config)
        self.assertTrue(context_config['enabled'])
        self.assertEqual(context_config['agent'], 'build')
        self.assertEqual(context_config['model'], 'anthropic/claude-sonnet-4-20250514')
        
    def test_validate_context_config_disabled(self):
        """Test validation with disabled context configuration."""
        config_path = self.fixtures_dir / "context_config_disabled.toml"
        generator = ContextConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        context_config = generator.validate_context_config(config)
        
        self.assertIsNone(context_config)
        
    def test_validate_context_config_missing(self):
        """Test validation with missing context configuration."""
        config = {'opencode': {'commands': {}}}
        generator = ContextConfigGenerator()
        
        context_config = generator.validate_context_config(config)
        
        self.assertIsNone(context_config)
        
    def test_validate_context_config_no_opencode_section(self):
        """Test validation with missing opencode section."""
        config = {}
        generator = ContextConfigGenerator()
        
        context_config = generator.validate_context_config(config)
        
        self.assertIsNone(context_config)
        
    def test_validate_and_read_template_default(self):
        """Test template validation and reading with default template."""
        config_path = self.fixtures_dir / "context_config_enabled.toml"
        generator = ContextConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        context_config = generator.validate_context_config(config)
        
        # Mock the default template file
        mock_template_content = "# Default Context Template\n\nDefault content here."
        with patch('builtins.open', mock_open(read_data=mock_template_content)):
            template_content = generator.validate_and_read_template(context_config)
        
        self.assertEqual(template_content, mock_template_content)
        
    def test_validate_and_read_template_custom(self):
        """Test template validation and reading with custom template."""
        config_path = self.fixtures_dir / "context_config_custom.toml"
        generator = ContextConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        context_config = generator.validate_context_config(config)
        
        template_content = generator.validate_and_read_template(context_config)
        
        self.assertIn("Custom Context Template", template_content)
        self.assertIn("Custom Analysis Steps", template_content)
        
    def test_validate_and_read_template_custom_empty_file(self):
        """Test template validation with custom template but empty template_file."""
        context_config = {
            'template': 'custom',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        generator = ContextConfigGenerator()
        
        with self.assertRaises(ValueError) as context:
            generator.validate_and_read_template(context_config)
        
        self.assertIn("Custom template specified but template_file is empty", str(context.exception))
        
    def test_validate_and_read_template_custom_file_not_found(self):
        """Test template validation with custom template file that doesn't exist."""
        context_config = {
            'template': 'custom',
            'template_file': 'nonexistent_template.md',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        generator = ContextConfigGenerator()
        
        with self.assertRaises(FileNotFoundError) as context:
            generator.validate_and_read_template(context_config)
        
        self.assertIn("Custom template file not found", str(context.exception))
        
    def test_validate_and_read_template_custom_empty_file_content(self):
        """Test template validation with custom template file that is empty."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            # Create empty file
            temp_path = f.name
            
        try:
            context_config = {
                'template': 'custom',
                'template_file': temp_path,
                'additional_files': [],
                'additional_files_strategy': 'merge'
            }
            generator = ContextConfigGenerator()
            
            with self.assertRaises(ValueError) as context:
                generator.validate_and_read_template(context_config)
            
            self.assertIn("Custom template file is empty", str(context.exception))
        finally:
            os.unlink(temp_path)
            
    def test_validate_and_read_template_unknown_type(self):
        """Test template validation with unknown template type."""
        context_config = {
            'template': 'unknown',
            'template_file': '',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        generator = ContextConfigGenerator()
        
        with self.assertRaises(ValueError) as context:
            generator.validate_and_read_template(context_config)
        
        self.assertIn("Unknown template type: unknown", str(context.exception))
        
    def test_validate_and_read_template_invalid_strategy(self):
        """Test template validation with invalid additional_files_strategy."""
        config_path = self.fixtures_dir / "context_config_invalid_strategy.toml"
        generator = ContextConfigGenerator(str(config_path))
        
        config = generator.load_toml_config()
        context_config = generator.validate_context_config(config)
        
        with self.assertRaises(ValueError) as context:
            generator.validate_and_read_template(context_config)
        
        self.assertIn("Invalid additional_files_strategy: invalid", str(context.exception))
        
    def test_validate_and_read_template_with_additional_files_merge(self):
        """Test template validation with additional files using merge strategy."""
        # Create a temporary additional file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Additional File\n\nAdditional content here.")
            additional_file_path = f.name
            
        try:
            context_config = {
                'template': 'default',
                'template_file': '',
                'additional_files': [additional_file_path],
                'additional_files_strategy': 'merge'
            }
            generator = ContextConfigGenerator()
            
            mock_template_content = "# Default Template\n\nDefault content."
            with patch('builtins.open', mock_open(read_data=mock_template_content)) as mock_file:
                # Configure mock to return different content for different files
                def side_effect(file_path, *args, **kwargs):
                    if str(file_path).endswith(additional_file_path):
                        return mock_open(read_data="# Additional File\n\nAdditional content here.")()
                    else:
                        return mock_open(read_data=mock_template_content)()
                
                mock_file.side_effect = side_effect
                template_content = generator.validate_and_read_template(context_config)
            
            self.assertIn("Default content", template_content)
            self.assertIn("Additional Files", template_content)
        finally:
            os.unlink(additional_file_path)
            
    def test_validate_and_read_template_with_additional_files_replace(self):
        """Test template validation with additional files using replace strategy."""
        # Create a temporary additional file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Additional File\n\nAdditional content here.")
            additional_file_path = f.name
            
        try:
            context_config = {
                'template': 'default',
                'template_file': '',
                'additional_files': [additional_file_path],
                'additional_files_strategy': 'replace'
            }
            generator = ContextConfigGenerator()
            
            template_content = generator.validate_and_read_template(context_config)
            
            self.assertIn("Additional File", template_content)
            self.assertIn("Additional content here", template_content)
        finally:
            os.unlink(additional_file_path)
            
    def test_process_additional_files_empty_list(self):
        """Test processing empty additional files list."""
        generator = ContextConfigGenerator()
        
        result = generator._process_additional_files([])
        
        self.assertEqual(result, "")
        
    def test_process_additional_files_nonexistent_file(self):
        """Test processing additional files with non-existent file."""
        generator = ContextConfigGenerator()
        
        with self.assertRaises(FileNotFoundError) as context:
            generator._process_additional_files(["nonexistent.md"])
        
        self.assertIn("Additional file not found", str(context.exception))
        
    def test_process_additional_files_valid_files(self):
        """Test processing valid additional files."""
        # Create temporary additional files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f1:
            f1.write("Content of file 1")
            file1_path = f1.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f2:
            f2.write("Content of file 2")
            file2_path = f2.name
            
        try:
            generator = ContextConfigGenerator()
            
            result = generator._process_additional_files([file1_path, file2_path])
            
            self.assertIn("Content of file 1", result)
            self.assertIn("Content of file 2", result)
            self.assertIn(Path(file1_path).name, result)
            self.assertIn(Path(file2_path).name, result)
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)
            
    def test_generate_yaml_config(self):
        """Test YAML configuration generation."""
        context_config = {
            'agent': 'build',
            'model': 'anthropic/claude-sonnet-4-20250514'
        }
        template_content = "# Test Template\n\nTest content."
        generator = ContextConfigGenerator()
        
        yaml_config = generator.generate_yaml_config(context_config, template_content)
        
        self.assertIn('$schema', yaml_config)
        self.assertIn('command', yaml_config)
        self.assertIn('context', yaml_config['command'])
        self.assertEqual(yaml_config['command']['context']['template'], template_content)
        self.assertEqual(yaml_config['command']['context']['agent'], 'build')
        self.assertEqual(yaml_config['command']['context']['model'], 'anthropic/claude-sonnet-4-20250514')
        
    def test_write_yaml_config(self):
        """Test writing YAML configuration to file."""
        context_config = {
            'agent': 'build',
            'model': 'anthropic/claude-sonnet-4-20250514'
        }
        template_content = "# Test Template\n\nTest content."
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ContextConfigGenerator()
            generator.project_root = Path(temp_dir)
            
            output_path = "test_output/context.md"
            generator.write_yaml_config(context_config, template_content, output_path)
            
            output_file = Path(temp_dir) / output_path
            self.assertTrue(output_file.exists())
            
            with open(output_file, 'r') as f:
                content = f.read()
                
            self.assertIn("---", content)
            self.assertIn("description: Context command", content)
            self.assertIn("agent: build", content)
            self.assertIn("model: anthropic/claude-sonnet-4-20250514", content)
            self.assertIn("# Test Template", content)
            self.assertIn("Test content.", content)
            
    def test_strip_frontmatter_with_frontmatter(self):
        """Test stripping YAML frontmatter from content."""
        content_with_frontmatter = """---
description: Test
agent: build
---

# Content

This is the actual content."""
        
        generator = ContextConfigGenerator()
        
        result = generator._strip_frontmatter(content_with_frontmatter)
        
        self.assertNotIn("---", result)
        self.assertNotIn("description: Test", result)
        self.assertIn("# Content", result)
        self.assertIn("This is the actual content.", result)
        
    def test_strip_frontmatter_without_frontmatter(self):
        """Test stripping frontmatter from content without frontmatter."""
        content_without_frontmatter = """# Content

This is the actual content."""
        
        generator = ContextConfigGenerator()
        
        result = generator._strip_frontmatter(content_without_frontmatter)
        
        self.assertEqual(result, content_without_frontmatter)
        
    def test_generate_success(self):
        """Test successful generation process."""
        config_path = self.fixtures_dir / "context_config_enabled.toml"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ContextConfigGenerator(str(config_path))
            generator.project_root = Path(temp_dir)
            
            # Mock the default template file
            mock_template_content = "# Default Context Template\n\nDefault content here."
            with patch('builtins.open', mock_open(read_data=mock_template_content)):
                result = generator.generate()
            
            self.assertTrue(result)
            
    def test_generate_disabled_config(self):
        """Test generation with disabled configuration."""
        config_path = self.fixtures_dir / "context_config_disabled.toml"
        generator = ContextConfigGenerator(str(config_path))
        
        result = generator.generate()
        
        self.assertFalse(result)
        
    def test_generate_with_exception(self):
        """Test generation process with exception handling."""
        generator = ContextConfigGenerator("nonexistent.toml")
        
        with self.assertRaises(SystemExit):
            generator.generate()


if __name__ == '__main__':
    unittest.main()
