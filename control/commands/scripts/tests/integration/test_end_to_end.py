#!/usr/bin/env python3
"""
Integration tests for the commit configuration generator.

Tests end-to-end scenarios with real files and configurations.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from control.commands.scripts.commit import CommitConfigGenerator


class TestEndToEndIntegration(unittest.TestCase):
    """Integration tests for complete workflow scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.fixtures_dir = self.test_dir / "fixtures"

    def test_successful_generation_with_default_template(self):
        """Test complete successful generation with default template."""
        config_path = self.fixtures_dir / "config_enabled.toml"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generator = CommitConfigGenerator(str(config_path))

            # Override project root to use temp directory
            generator.project_root = temp_path

            # Copy the default template to temp directory
            default_template_dir = temp_path / "control/commands/generic"
            default_template_dir.mkdir(parents=True, exist_ok=True)

            # Create a mock default template
            default_template_path = default_template_dir / "git-commit.md"
            with open(default_template_path, 'w') as f:
                f.write("# Default Git Commit Template\n\nThis is the default template.")

            success = generator.generate()

            self.assertTrue(success)

            # Verify output file was created
            output_file = temp_path / "generated/.opencode/command/commit.jsonc"
            self.assertTrue(output_file.exists())

            # Verify content
            with open(output_file, 'r') as f:
                config = json.load(f)

            self.assertEqual(config["$schema"], "https://opencode.ai/config.json")
            self.assertIn("commit", config["command"])
            self.assertIn("Default Git Commit Template", config["command"]["commit"]["template"])
            self.assertEqual(config["command"]["commit"]["agent"], "build")

    def test_successful_generation_with_custom_template(self):
        """Test complete successful generation with custom template."""
        config_path = self.fixtures_dir / "config_custom_valid.toml"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generator = CommitConfigGenerator(str(config_path))

            # Override project root to use temp directory
            generator.project_root = temp_path

            # Copy the custom template to temp directory
            custom_template_dir = temp_path / "control/commands/scripts/tests/fixtures"
            custom_template_dir.mkdir(parents=True, exist_ok=True)

            # Copy the actual custom template
            import shutil
            shutil.copy2(self.fixtures_dir / "custom_template.md", custom_template_dir)

            success = generator.generate()

            self.assertTrue(success)

            # Verify output file was created
            output_file = temp_path / "generated/.opencode/command/commit.jsonc"
            self.assertTrue(output_file.exists())

            # Verify content includes custom template
            with open(output_file, 'r') as f:
                config = json.load(f)

            self.assertIn("Custom Commit Template", config["command"]["commit"]["template"])
            self.assertIn("testing purposes", config["command"]["commit"]["template"])

    def test_skipped_generation_disabled(self):
        """Test generation is skipped when disabled."""
        config_path = self.fixtures_dir / "config_disabled.toml"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generator = CommitConfigGenerator(str(config_path))
            generator.project_root = temp_path

            success = generator.generate()

            self.assertFalse(success)

            # Verify no output file was created
            output_file = temp_path / ".opencode/command/commit.jsonc"
            self.assertFalse(output_file.exists())

    def test_skipped_generation_non_git_vcs(self):
        """Test generation is skipped for non-git VCS."""
        config_path = self.fixtures_dir / "config_svn.toml"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generator = CommitConfigGenerator(str(config_path))
            generator.project_root = temp_path

            success = generator.generate()

            self.assertFalse(success)

            # Verify no output file was created
            output_file = temp_path / ".opencode/command/commit.jsonc"
            self.assertFalse(output_file.exists())

    def test_error_handling_custom_empty_file(self):
        """Test error handling for custom template with empty template_file."""
        config_path = self.fixtures_dir / "config_custom_empty_file.toml"

        generator = CommitConfigGenerator(str(config_path))

        # Should exit with error
        with self.assertRaises(SystemExit):
            generator.generate()

    def test_error_handling_custom_empty_template(self):
        """Test error handling for custom template with empty template file."""
        config_path = self.fixtures_dir / "config_custom_empty_template.toml"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generator = CommitConfigGenerator(str(config_path))
            generator.project_root = temp_path

            # Copy the empty template to temp directory
            empty_template_dir = temp_path / "control/commands/scripts/tests/fixtures"
            empty_template_dir.mkdir(parents=True, exist_ok=True)

            # Copy the actual empty template
            import shutil
            shutil.copy2(self.fixtures_dir / "empty_template.md", empty_template_dir)

            # Should exit with error
            with self.assertRaises(SystemExit):
                generator.generate()

    def test_template_content_embedding(self):
        """Test that template content is properly embedded, not just the path."""
        config_path = self.fixtures_dir / "config_enabled.toml"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generator = CommitConfigGenerator(str(config_path))
            generator.project_root = temp_path

            # Create a mock default template with specific content
            default_template_dir = temp_path / "control/commands/generic"
            default_template_dir.mkdir(parents=True, exist_ok=True)

            template_content = """# Test Template

This is a test template with specific content.

## Instructions
- Follow conventional commits
- Use semantic versioning
- Include proper descriptions

### Example
feat(auth): add user authentication system"""

            default_template_path = default_template_dir / "git-commit.md"
            with open(default_template_path, 'w') as f:
                f.write(template_content)

            success = generator.generate()
            self.assertTrue(success)

            # Verify the full template content is embedded
            output_file = temp_path / ".opencode/command/commit.jsonc"
            with open(output_file, 'r') as f:
                config = json.load(f)

            embedded_template = config["command"]["commit"]["template"]

            # Verify it's the full content, not just a path
            self.assertEqual(embedded_template, template_content)
            self.assertIn("This is a test template with specific content", embedded_template)
            self.assertIn("Follow conventional commits", embedded_template)
            self.assertIn("feat(auth): add user authentication system", embedded_template)

            # Verify it's not just a file path
            self.assertNotIn(".md", embedded_template.split('\n')[0])  # First line shouldn't be a path


if __name__ == '__main__':
    unittest.main()
