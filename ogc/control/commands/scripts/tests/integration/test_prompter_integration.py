#!/usr/bin/env python3
"""
Integration tests for the prompter command generator.

This module contains integration tests that test the full workflow
of the PrompterConfigGenerator class with real files and configurations.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from prompter import PrompterConfigGenerator


class TestPrompterIntegration(unittest.TestCase):
    """Integration test cases for PrompterConfigGenerator."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create directory structure
        (self.project_root / "ogc/control/commands/generic").mkdir(parents=True, exist_ok=True)
        (self.project_root / "ogc/generated/.opencode/command").mkdir(parents=True, exist_ok=True)
        
        # Create base prompter template
        base_template_path = self.project_root / "ogc/control/commands/generic/prompter.md"
        with open(base_template_path, 'w') as f:
            f.write("""---
description: Transform basic requests into comprehensive, well-structured prompts
---

# Prompter Command

This is the base prompter template for enhancing prompts using the 10-step framework.

## Usage

Provide a basic request and get an enhanced, structured prompt in return.
""")
        
        self.config_path = self.project_root / "ogc/config.toml"
        self.generator = PrompterConfigGenerator(str(self.config_path))
    
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow_enabled_with_base_template(self):
        """Test complete workflow with enabled prompter and base template."""
        # Create config file
        toml_content = """
[opencode.commands]
prompter = { enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        # Run generation
        result = self.generator.generate()
        self.assertTrue(result)
        
        # Check output file
        output_file = self.project_root / "ogc/generated/.opencode/command/prompter.md"
        self.assertTrue(output_file.exists())
        
        # Verify content
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("---", content)
        self.assertIn("description: Prompter command", content)
        self.assertIn("agent: build", content)
        self.assertIn("model: anthropic/claude-sonnet-4-20250514", content)
        self.assertIn("Prompter Command", content)
        self.assertIn("10-step framework", content)
    
    def test_full_workflow_disabled(self):
        """Test complete workflow with disabled prompter."""
        # Create config file
        toml_content = """
[opencode.commands]
prompter = { enabled = false, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        # Run generation
        result = self.generator.generate()
        self.assertFalse(result)
        
        # Check output file was not created
        output_file = self.project_root / "ogc/generated/.opencode/command/prompter.md"
        self.assertFalse(output_file.exists())
    
    def test_full_workflow_custom_template(self):
        """Test complete workflow with custom template."""
        # Create custom template
        custom_template_path = self.project_root / "custom_prompter.md"
        with open(custom_template_path, 'w') as f:
            f.write("""---
description: Custom prompter template
---

# Custom Prompter

This is a custom prompter template with specialized functionality.

## Custom Features

- Domain-specific enhancements
- Specialized formatting
""")
        
        # Create config file
        toml_content = f"""
[opencode.commands]
prompter = {{ enabled = true, agent = "custom", model = "custom-model", template = "custom", template_file = "{custom_template_path}", additional_files = [], additional_files_strategy = "merge", include_base_template = false }}
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        # Run generation
        result = self.generator.generate()
        self.assertTrue(result)
        
        # Check output file
        output_file = self.project_root / "ogc/generated/.opencode/command/prompter.md"
        self.assertTrue(output_file.exists())
        
        # Verify content
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("agent: custom", content)
        self.assertIn("model: custom-model", content)
        self.assertIn("Custom Prompter", content)
        self.assertIn("Domain-specific enhancements", content)
    
    def test_full_workflow_with_additional_files_merge(self):
        """Test complete workflow with additional files using merge strategy."""
        # Create additional file
        additional_file_path = self.project_root / "additional_prompter_info.md"
        with open(additional_file_path, 'w') as f:
            f.write("""# Additional Prompter Information

This file contains additional information for the prompter command.

## Extra Guidelines

- Follow best practices
- Use structured approaches
""")
        
        # Create config file
        toml_content = f"""
[opencode.commands]
prompter = {{ enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = ["{additional_file_path}"], additional_files_strategy = "merge", include_base_template = true }}
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        # Run generation
        result = self.generator.generate()
        self.assertTrue(result)
        
        # Check output file
        output_file = self.project_root / "ogc/generated/.opencode/command/prompter.md"
        self.assertTrue(output_file.exists())
        
        # Verify content includes both base template and additional files
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Prompter Command", content)  # From base template
        self.assertIn("Additional Files", content)  # Section header
        self.assertIn("Additional Prompter Information", content)  # From additional file
        self.assertIn("Extra Guidelines", content)  # From additional file
    
    def test_full_workflow_with_additional_files_replace(self):
        """Test complete workflow with additional files using replace strategy."""
        # Create additional file
        additional_file_path = self.project_root / "replacement_prompter.md"
        with open(additional_file_path, 'w') as f:
            f.write("""# Replacement Prompter Template

This completely replaces the base template.

## Replacement Features

- Custom workflow
- Specialized processing
""")
        
        # Create config file
        toml_content = f"""
[opencode.commands]
prompter = {{ enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = ["{additional_file_path}"], additional_files_strategy = "replace", include_base_template = true }}
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        # Run generation
        result = self.generator.generate()
        self.assertTrue(result)
        
        # Check output file
        output_file = self.project_root / "ogc/generated/.opencode/command/prompter.md"
        self.assertTrue(output_file.exists())
        
        # Verify content only includes additional files, not base template
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertNotIn("Prompter Command", content)  # Should not be from base template
        self.assertIn("Replacement Prompter Template", content)  # From additional file
        self.assertIn("Replacement Features", content)  # From additional file
    
    def test_full_workflow_no_template_content(self):
        """Test workflow when no template content is available."""
        # Create config file without base template and no additional files
        toml_content = """
[opencode.commands]
prompter = { enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = false }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        # Run generation (should fail)
        with self.assertRaises(SystemExit):
            self.generator.generate()
    
    def test_full_workflow_missing_base_template(self):
        """Test workflow when base template file is missing."""
        # Remove base template file
        base_template_path = self.project_root / "ogc/control/commands/generic/prompter.md"
        base_template_path.unlink()
        
        # Create config file
        toml_content = """
[opencode.commands]
prompter = { enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        # Run generation (should fail)
        with self.assertRaises(SystemExit):
            self.generator.generate()
    
    def test_full_workflow_multiple_additional_files(self):
        """Test workflow with multiple additional files."""
        # Create multiple additional files
        file1_path = self.project_root / "extra1.md"
        file2_path = self.project_root / "extra2.md"
        
        with open(file1_path, 'w') as f:
            f.write("# Extra File 1\n\nContent from first extra file.")
        
        with open(file2_path, 'w') as f:
            f.write("# Extra File 2\n\nContent from second extra file.")
        
        # Create config file
        toml_content = f"""
[opencode.commands]
prompter = {{ enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = ["{file1_path}", "{file2_path}"], additional_files_strategy = "merge", include_base_template = true }}
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)
        
        # Run generation
        result = self.generator.generate()
        self.assertTrue(result)
        
        # Check output file
        output_file = self.project_root / "ogc/generated/.opencode/command/prompter.md"
        self.assertTrue(output_file.exists())
        
        # Verify content includes all files
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Prompter Command", content)  # From base template
        self.assertIn("## extra1.md", content)  # First additional file header
        self.assertIn("Content from first extra file", content)  # First additional file content
        self.assertIn("## extra2.md", content)  # Second additional file header
        self.assertIn("Content from second extra file", content)  # Second additional file content


if __name__ == '__main__':
    unittest.main()
