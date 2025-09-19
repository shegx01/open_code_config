#!/usr/bin/env python3
"""
Integration tests for the CleanConfigGenerator.

Tests the full workflow from TOML config to generated output file.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the clean module directly
sys.path.insert(0, str(project_root / "ogc" / "control" / "commands" / "scripts"))
from clean import CleanConfigGenerator


class TestCleanIntegration(unittest.TestCase):
    """Integration test cases for CleanConfigGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.fixtures_dir = self.test_dir / "fixtures"
        
    def test_full_workflow_with_elixir(self):
        """Test complete workflow with Elixir language configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock project structure
            self._create_mock_project_structure(temp_path)
            
            # Create config file
            config_content = """
[opencode.commands]
clean = { enabled = true, lang = "elixir", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true }
"""
            config_path = temp_path / "ogc/config.toml"
            config_path.write_text(config_content)
            
            # Run generator
            generator = CleanConfigGenerator(str(config_path))
            result = generator.generate()
            
            # Verify success
            self.assertTrue(result)
            
            # Verify output file exists
            output_file = temp_path / "ogc/generated/.opencode/command/clean.md"
            self.assertTrue(output_file.exists())
            
            # Verify output content
            content = output_file.read_text()
            self.assertIn("---", content)  # YAML frontmatter
            self.assertIn("description: Clean command", content)
            self.assertIn("agent: build", content)
            self.assertIn("model: anthropic/claude-sonnet-4-20250514", content)
            self.assertIn("Base Template Content", content)
            self.assertIn("Elixir Template Content", content)
            
    def test_full_workflow_with_kotlin(self):
        """Test complete workflow with Kotlin language configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock project structure
            self._create_mock_project_structure(temp_path)
            
            # Create config file
            config_content = """
[opencode.commands]
clean = { enabled = true, lang = "kotlin", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true }
"""
            config_path = temp_path / "ogc/config.toml"
            config_path.write_text(config_content)
            
            # Run generator
            generator = CleanConfigGenerator(str(config_path))
            result = generator.generate()
            
            # Verify success
            self.assertTrue(result)
            
            # Verify output file exists
            output_file = temp_path / "ogc/generated/.opencode/command/clean.md"
            self.assertTrue(output_file.exists())
            
            # Verify output content
            content = output_file.read_text()
            self.assertIn("Base Template Content", content)
            self.assertIn("Kotlin Template Content", content)
            
    def test_full_workflow_without_base_template(self):
        """Test complete workflow without base template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock project structure
            self._create_mock_project_structure(temp_path)
            
            # Create config file
            config_content = """
[opencode.commands]
clean = { enabled = true, lang = "elixir", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = false }
"""
            config_path = temp_path / "ogc/config.toml"
            config_path.write_text(config_content)
            
            # Run generator
            generator = CleanConfigGenerator(str(config_path))
            result = generator.generate()
            
            # Verify success
            self.assertTrue(result)
            
            # Verify output file exists
            output_file = temp_path / "ogc/generated/.opencode/command/clean.md"
            self.assertTrue(output_file.exists())
            
            # Verify output content
            content = output_file.read_text()
            self.assertNotIn("Base Template Content", content)
            self.assertIn("Elixir Template Content", content)
            
    def test_full_workflow_with_custom_template(self):
        """Test complete workflow with custom template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create custom template
            custom_template_path = temp_path / "custom_clean.md"
            custom_template_path.write_text("# Custom Clean Template\nCustom template content for testing")
            
            # Create config file
            config_content = f"""
[opencode.commands]
clean = {{ enabled = true, lang = "elixir", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "custom", template_file = "{custom_template_path}", additional_files = [], additional_files_strategy = "merge", include_base_template = false }}
"""
            config_path = temp_path / "ogc/config.toml"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(config_content)
            
            # Run generator
            generator = CleanConfigGenerator(str(config_path))
            result = generator.generate()
            
            # Verify success
            self.assertTrue(result)
            
            # Verify output file exists
            output_file = temp_path / "ogc/generated/.opencode/command/clean.md"
            self.assertTrue(output_file.exists())
            
            # Verify output content
            content = output_file.read_text()
            self.assertIn("Custom Clean Template", content)
            self.assertIn("Custom template content for testing", content)
            
    def test_full_workflow_with_additional_files(self):
        """Test complete workflow with additional files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock project structure
            self._create_mock_project_structure(temp_path)
            
            # Create additional file
            additional_file_path = temp_path / "additional_instructions.md"
            additional_file_path.write_text("# Additional Instructions\nAdditional content for clean command")
            
            # Create config file
            config_content = f"""
[opencode.commands]
clean = {{ enabled = true, lang = "elixir", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = ["{additional_file_path}"], additional_files_strategy = "merge", include_base_template = true }}
"""
            config_path = temp_path / "ogc/config.toml"
            config_path.write_text(config_content)
            
            # Run generator
            generator = CleanConfigGenerator(str(config_path))
            result = generator.generate()
            
            # Verify success
            self.assertTrue(result)
            
            # Verify output file exists
            output_file = temp_path / "ogc/generated/.opencode/command/clean.md"
            self.assertTrue(output_file.exists())
            
            # Verify output content
            content = output_file.read_text()
            self.assertIn("Base Template Content", content)
            self.assertIn("Elixir Template Content", content)
            self.assertIn("Additional Files", content)
            self.assertIn("Additional Instructions", content)
            self.assertIn("Additional content for clean command", content)
            
    def test_full_workflow_disabled_config(self):
        """Test complete workflow with disabled configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create config file
            config_content = """
[opencode.commands]
clean = { enabled = false, lang = "elixir", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true }
"""
            config_path = temp_path / "ogc/config.toml"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(config_content)
            
            # Run generator
            generator = CleanConfigGenerator(str(config_path))
            result = generator.generate()
            
            # Verify skipped
            self.assertFalse(result)
            
            # Verify no output file created
            output_file = temp_path / "ogc/generated/.opencode/command/clean.md"
            self.assertFalse(output_file.exists())
            
    def test_full_workflow_unsupported_language(self):
        """Test complete workflow with unsupported language."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create config file
            config_content = """
[opencode.commands]
clean = { enabled = true, lang = "python", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true }
"""
            config_path = temp_path / "ogc/config.toml"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(config_content)
            
            # Run generator
            generator = CleanConfigGenerator(str(config_path))
            result = generator.generate()
            
            # Verify skipped
            self.assertFalse(result)
            
            # Verify no output file created
            output_file = temp_path / "ogc/generated/.opencode/command/clean.md"
            self.assertFalse(output_file.exists())
            
    def _create_mock_project_structure(self, temp_path: Path):
        """Create mock project structure with template files."""
        # Create template directory
        template_dir = temp_path / "ogc/control/commands/generic/clean"
        template_dir.mkdir(parents=True)
        
        # Create base template
        base_template = template_dir / "base.md"
        base_template.write_text("# Base Template\nBase Template Content")
        
        # Create language templates
        elixir_template = template_dir / "elixir.md"
        elixir_template.write_text("# Elixir Template\nElixir Template Content")
        
        kotlin_template = template_dir / "kotlin.md"
        kotlin_template.write_text("# Kotlin Template\nKotlin Template Content")
        
        typescript_template = template_dir / "typescript.md"
        typescript_template.write_text("# TypeScript Template\nTypeScript Template Content")


if __name__ == '__main__':
    unittest.main()
