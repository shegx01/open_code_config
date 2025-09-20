#!/usr/bin/env python3
"""
Integration tests for the ContextConfigGenerator.

Tests the full workflow from TOML config to generated output file.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the context module directly
sys.path.insert(0, str(project_root / "control" / "commands" / "scripts"))
from context import ContextConfigGenerator


class TestContextIntegration(unittest.TestCase):
    """Integration test cases for ContextConfigGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.fixtures_dir = self.test_dir / "fixtures"

    def test_full_workflow_with_default_template(self):
        """Test complete workflow with default template configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock project structure
            self._create_mock_project_structure(temp_path)

            # Create config file
            config_content = """
[opencode.commands]
context = { enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge" }
"""
            config_path = temp_path / "config.toml"
            config_path.write_text(config_content)

            # Run generator
            generator = ContextConfigGenerator(str(config_path))
            result = generator.generate()

            # Verify result
            self.assertTrue(result)

            # Check output file exists
            output_file = temp_path / "generated/.opencode/command/context.md"
            self.assertTrue(output_file.exists())

            # Verify output content
            content = output_file.read_text()
            self.assertIn("---", content)
            self.assertIn("description: Context command", content)
            self.assertIn("agent: build", content)
            self.assertIn("model: anthropic/claude-sonnet-4-20250514", content)
            self.assertIn("# Project Context Analysis", content)

    def test_full_workflow_with_custom_template(self):
        """Test complete workflow with custom template configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock project structure
            self._create_mock_project_structure(temp_path)

            # Create custom template
            custom_template_content = """# Custom Context Analysis

This is a custom template for context analysis.

## Custom Steps

1. Custom step one
2. Custom step two

## Custom Output

Custom output format here."""

            custom_template_path = temp_path / "custom_context_template.md"
            custom_template_path.write_text(custom_template_content)

            # Create config file
            config_content = f"""
[opencode.commands]
context = {{ enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "custom", template_file = "{custom_template_path}", additional_files = [], additional_files_strategy = "merge" }}
"""
            config_path = temp_path / "config.toml"
            config_path.write_text(config_content)

            # Run generator
            generator = ContextConfigGenerator(str(config_path))
            result = generator.generate()

            # Verify result
            self.assertTrue(result)

            # Check output file exists
            output_file = temp_path / "generated/.opencode/command/context.md"
            self.assertTrue(output_file.exists())

            # Verify output content
            content = output_file.read_text()
            self.assertIn("---", content)
            self.assertIn("description: Context command", content)
            self.assertIn("agent: build", content)
            self.assertIn("model: anthropic/claude-sonnet-4-20250514", content)
            self.assertIn("# Custom Context Analysis", content)
            self.assertIn("Custom Steps", content)

    def test_full_workflow_with_additional_files_merge(self):
        """Test complete workflow with additional files using merge strategy."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock project structure
            self._create_mock_project_structure(temp_path)

            # Create additional file
            additional_file_content = """# Additional Context Information

This file contains additional context information.

## Additional Guidelines

- Additional guideline 1
- Additional guideline 2"""

            additional_file_path = temp_path / "additional_context.md"
            additional_file_path.write_text(additional_file_content)

            # Create config file
            config_content = f"""
[opencode.commands]
context = {{ enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = ["{additional_file_path}"], additional_files_strategy = "merge" }}
"""
            config_path = temp_path / "config.toml"
            config_path.write_text(config_content)

            # Run generator
            generator = ContextConfigGenerator(str(config_path))
            result = generator.generate()

            # Verify result
            self.assertTrue(result)

            # Check output file exists
            output_file = temp_path / "generated/.opencode/command/context.md"
            self.assertTrue(output_file.exists())

            # Verify output content
            content = output_file.read_text()
            self.assertIn("---", content)
            self.assertIn("# Project Context Analysis", content)  # Default template
            self.assertIn("# Additional Files", content)  # Merge section
            self.assertIn("Additional Context Information", content)  # Additional file content

    def test_full_workflow_with_additional_files_replace(self):
        """Test complete workflow with additional files using replace strategy."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock project structure
            self._create_mock_project_structure(temp_path)

            # Create additional file
            additional_file_content = """# Replacement Context Template

This file replaces the default template.

## Replacement Guidelines

- Replacement guideline 1
- Replacement guideline 2"""

            additional_file_path = temp_path / "replacement_context.md"
            additional_file_path.write_text(additional_file_content)

            # Create config file
            config_content = f"""
[opencode.commands]
context = {{ enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = ["{additional_file_path}"], additional_files_strategy = "replace" }}
"""
            config_path = temp_path / "config.toml"
            config_path.write_text(config_content)

            # Run generator
            generator = ContextConfigGenerator(str(config_path))
            result = generator.generate()

            # Verify result
            self.assertTrue(result)

            # Check output file exists
            output_file = temp_path / "generated/.opencode/command/context.md"
            self.assertTrue(output_file.exists())

            # Verify output content
            content = output_file.read_text()
            self.assertIn("---", content)
            self.assertNotIn("# Project Context Analysis", content)  # Default template should be replaced
            self.assertIn("# Replacement Context Template", content)  # Replacement content
            self.assertIn("Replacement Guidelines", content)

    def test_full_workflow_disabled_command(self):
        """Test complete workflow with disabled command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock project structure
            self._create_mock_project_structure(temp_path)

            # Create config file with disabled command
            config_content = """
[opencode.commands]
context = { enabled = false, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge" }
"""
            config_path = temp_path / "config.toml"
            config_path.write_text(config_content)

            # Run generator
            generator = ContextConfigGenerator(str(config_path))
            result = generator.generate()

            # Verify result
            self.assertFalse(result)

            # Check output file does not exist
            output_file = temp_path / "generated/.opencode/command/context.md"
            self.assertFalse(output_file.exists())

    def test_full_workflow_with_custom_agent_and_model(self):
        """Test complete workflow with custom agent and model configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock project structure
            self._create_mock_project_structure(temp_path)

            # Create config file with custom agent and model
            config_content = """
[opencode.commands]
context = { enabled = true, agent = "custom-agent", model = "custom/model-v1", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge" }
"""
            config_path = temp_path / "config.toml"
            config_path.write_text(config_content)

            # Run generator
            generator = ContextConfigGenerator(str(config_path))
            result = generator.generate()

            # Verify result
            self.assertTrue(result)

            # Check output file exists
            output_file = temp_path / "generated/.opencode/command/context.md"
            self.assertTrue(output_file.exists())

            # Verify output content has custom agent and model
            content = output_file.read_text()
            self.assertIn("agent: custom-agent", content)
            self.assertIn("model: custom/model-v1", content)

    def test_full_workflow_with_frontmatter_stripping(self):
        """Test complete workflow with template that has existing frontmatter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock project structure
            self._create_mock_project_structure(temp_path)

            # Create custom template with frontmatter
            custom_template_content = """---
description: Old description
agent: old-agent
---

# Custom Context Analysis

This template has existing frontmatter that should be stripped."""

            custom_template_path = temp_path / "custom_context_template.md"
            custom_template_path.write_text(custom_template_content)

            # Create config file
            config_content = f"""
[opencode.commands]
context = {{ enabled = true, agent = "new-agent", model = "new/model", template = "custom", template_file = "{custom_template_path}", additional_files = [], additional_files_strategy = "merge" }}
"""
            config_path = temp_path / "config.toml"
            config_path.write_text(config_content)

            # Run generator
            generator = ContextConfigGenerator(str(config_path))
            result = generator.generate()

            # Verify result
            self.assertTrue(result)

            # Check output file exists
            output_file = temp_path / "generated/.opencode/command/context.md"
            self.assertTrue(output_file.exists())

            # Verify output content
            content = output_file.read_text()

            # Should have new frontmatter, not old
            self.assertIn("agent: new-agent", content)
            self.assertIn("model: new/model", content)
            self.assertNotIn("agent: old-agent", content)
            self.assertNotIn("Old description", content)

            # Should have template content without old frontmatter
            self.assertIn("# Custom Context Analysis", content)
            self.assertIn("This template has existing frontmatter", content)

    def _create_mock_project_structure(self, temp_path: Path):
        """Create a mock project structure for testing."""
        # Create necessary directories
        (temp_path / "control/commands/generic").mkdir(parents=True, exist_ok=True)
        (temp_path / "generated/.opencode/command").mkdir(parents=True, exist_ok=True)

        # Create default template file
        default_template_content = """---
description: Analyze and understand the complete project context and structure
---

# Project Context Analysis

You are a project analysis specialist. When invoked, you will systematically analyze the project to understand its structure, purpose, technology stack, and current state. Use $ARGUMENTS to focus on specific aspects if provided.

## Your Analysis Process

**Step 1: Project Discovery**

- Read the README.md file to understand project purpose and setup
- Examine package.json/requirements.txt/Cargo.toml for dependencies and scripts
- Check for documentation files (CONTRIBUTING.md, CHANGELOG.md, etc.)

**Step 2: Codebase Structure Analysis**

- Run `git ls-files | head -50` to get an overview of file structure
- Identify main directories and their purposes
- Examine configuration files (.gitignore, .env.example, config files)
- Look for framework-specific patterns

## Analysis Guidelines

- **Be thorough**: Don't just read README, examine actual code structure, git history, and recent commits
- **Focus on developer needs**: What would a new team member need to know?
- **Identify gaps**: Missing documentation, setup issues, etc.
- **Practical insights**: Actual workflow vs documented workflow"""

        default_template_path = temp_path / "control/commands/generic/context.md"
        default_template_path.write_text(default_template_content)


if __name__ == '__main__':
    unittest.main()
