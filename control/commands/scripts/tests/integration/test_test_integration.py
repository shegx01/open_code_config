#!/usr/bin/env python3
"""
Integration tests for the test command generator.

This test suite validates the complete workflow of the TestConfigGenerator,
including end-to-end configuration processing and file generation.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the scripts directory to the path to import the test generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test import TestConfigGenerator


class TestTestIntegration(unittest.TestCase):
    """Integration test cases for TestConfigGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.toml"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create template directories
        self.template_dir = Path(self.temp_dir) / "control" / "commands" / "generic" / "test"
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Create output directory
        self.output_dir = Path(self.temp_dir) / "generated" / ".opencode" / "command"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.generator = TestConfigGenerator(str(self.config_path))

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_workflow_enabled_configuration(self):
        """Test complete workflow with enabled configuration."""
        # Create TOML configuration
        toml_content = """
[opencode.commands]
test = { enabled = true, lang = "elixir", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)

        # Create base template
        base_template_content = """# Test Base Template

This is the base template for test commands.

## Instructions
- Write comprehensive tests
- Follow TDD principles
- Ensure good coverage
"""
        base_template_path = self.template_dir / "base.md"
        with open(base_template_path, 'w') as f:
            f.write(base_template_content)

        # Create language-specific template
        elixir_template_content = """# Elixir Test Template

## ExUnit Testing
- Use `ExUnit` for unit tests
- Use `StreamData` for property-based testing
- Follow Elixir testing conventions

## Test Structure
```elixir
defmodule MyModuleTest do
  use ExUnit.Case

  test "should do something" do
    assert true
  end
end
```
"""
        elixir_template_path = self.template_dir / "elixir.md"
        with open(elixir_template_path, 'w') as f:
            f.write(elixir_template_content)

        # Run the generator
        result = self.generator.generate()

        # Verify generation was successful
        self.assertTrue(result)

        # Verify output file was created
        output_file = Path(self.temp_dir) / "generated" / ".opencode" / "command" / "test.md"
        self.assertTrue(output_file.exists())

        # Verify output file content
        with open(output_file, 'r') as f:
            content = f.read()

        # Check YAML frontmatter
        self.assertIn("---", content)
        self.assertIn("description: Test command", content)
        self.assertIn("agent: build", content)
        self.assertIn("model: anthropic/claude-sonnet-4-20250514", content)

        # Check template content
        self.assertIn("Test Base Template", content)
        self.assertIn("Elixir Test Template", content)
        self.assertIn("ExUnit Testing", content)

    def test_full_workflow_disabled_configuration(self):
        """Test complete workflow with disabled configuration."""
        # Create TOML configuration with disabled test
        toml_content = """
[opencode.commands]
test = { enabled = false, lang = "elixir" }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)

        # Run the generator
        result = self.generator.generate()

        # Verify generation was skipped
        self.assertFalse(result)

        # Verify no output file was created
        output_file = Path(self.temp_dir) / "generated" / ".opencode" / "command" / "test.md"
        self.assertFalse(output_file.exists())

    def test_full_workflow_kotlin_configuration(self):
        """Test complete workflow with Kotlin configuration."""
        # Create TOML configuration for Kotlin
        toml_content = """
[opencode.commands]
test = { enabled = true, lang = "kotlin", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)

        # Create base template
        base_template_content = "# Test Base Template\n\nBase testing instructions."
        base_template_path = self.template_dir / "base.md"
        with open(base_template_path, 'w') as f:
            f.write(base_template_content)

        # Create Kotlin template
        kotlin_template_content = """# Kotlin Test Template

## Kotlin Testing
- Use JUnit for unit tests
- Use MockK for mocking
- Follow Kotlin testing conventions

## Test Structure
```kotlin
class MyClassTest {
    @Test
    fun `should do something`() {
        assertTrue(true)
    }
}
```
"""
        kotlin_template_path = self.template_dir / "kotlin.md"
        with open(kotlin_template_path, 'w') as f:
            f.write(kotlin_template_content)

        # Run the generator
        result = self.generator.generate()

        # Verify generation was successful
        self.assertTrue(result)

        # Verify output file content
        output_file = Path(self.temp_dir) / "generated" / ".opencode" / "command" / "test.md"
        with open(output_file, 'r') as f:
            content = f.read()

        self.assertIn("Kotlin Test Template", content)
        self.assertIn("JUnit for unit tests", content)

    def test_full_workflow_typescript_configuration(self):
        """Test complete workflow with TypeScript configuration."""
        # Create TOML configuration for TypeScript
        toml_content = """
[opencode.commands]
test = { enabled = true, lang = "typescript", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = false }
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)

        # Create TypeScript template (no base template)
        typescript_template_content = """# TypeScript Test Template

## TypeScript Testing
- Use Jest or Vitest for testing
- Use TypeScript for type safety
- Follow TypeScript testing conventions

## Test Structure
```typescript
describe('MyClass', () => {
  test('should do something', () => {
    expect(true).toBe(true);
  });
});
```
"""
        typescript_template_path = self.template_dir / "typescript.md"
        with open(typescript_template_path, 'w') as f:
            f.write(typescript_template_content)

        # Run the generator
        result = self.generator.generate()

        # Verify generation was successful
        self.assertTrue(result)

        # Verify output file content
        output_file = Path(self.temp_dir) / "generated" / ".opencode" / "command" / "test.md"
        with open(output_file, 'r') as f:
            content = f.read()

        self.assertIn("TypeScript Test Template", content)
        self.assertIn("Jest or Vitest", content)
        # Should not contain base template content since include_base_template = false
        self.assertNotIn("Test Base Template", content)

    def test_full_workflow_custom_template(self):
        """Test complete workflow with custom template."""
        # Create custom template file
        custom_template_path = Path(self.temp_dir) / "custom_test_template.md"
        custom_template_content = """---
description: Custom Test Template
---

# Custom Test Template

This is a custom template for test commands.

## Custom Instructions
- Follow custom testing guidelines
- Use specific testing frameworks
- Implement custom test patterns
"""
        with open(custom_template_path, 'w') as f:
            f.write(custom_template_content)

        # Create TOML configuration with custom template
        toml_content = f"""
[opencode.commands]
test = {{ enabled = true, agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "custom", template_file = "{custom_template_path}", additional_files = [], additional_files_strategy = "merge" }}
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)

        # Run the generator
        result = self.generator.generate()

        # Verify generation was successful
        self.assertTrue(result)

        # Verify output file content
        output_file = Path(self.temp_dir) / "generated" / ".opencode" / "command" / "test.md"
        with open(output_file, 'r') as f:
            content = f.read()

        # Check that custom template content is present (without its frontmatter)
        self.assertIn("Custom Test Template", content)
        self.assertIn("Custom Instructions", content)
        # The original frontmatter should be stripped and replaced
        self.assertIn("description: Test command", content)  # Default description
        self.assertNotIn("description: Custom Test Template", content)  # Original frontmatter stripped

    def test_full_workflow_additional_files_merge(self):
        """Test complete workflow with additional files using merge strategy."""
        # Create additional file
        additional_file_path = Path(self.temp_dir) / "additional_test_info.md"
        additional_content = """# Additional Test Information

## Testing Best Practices
- Write clear test names
- Use arrange-act-assert pattern
- Keep tests independent
"""
        with open(additional_file_path, 'w') as f:
            f.write(additional_content)

        # Create TOML configuration with additional files
        toml_content = f"""
[opencode.commands]
test = {{ enabled = true, lang = "elixir", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = ["{additional_file_path}"], additional_files_strategy = "merge", include_base_template = true }}
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)

        # Create base template
        base_template_content = "# Test Base Template\n\nBase instructions."
        base_template_path = self.template_dir / "base.md"
        with open(base_template_path, 'w') as f:
            f.write(base_template_content)

        # Create language template
        elixir_template_content = "# Elixir Test Template\n\nElixir-specific instructions."
        elixir_template_path = self.template_dir / "elixir.md"
        with open(elixir_template_path, 'w') as f:
            f.write(elixir_template_content)

        # Run the generator
        result = self.generator.generate()

        # Verify generation was successful
        self.assertTrue(result)

        # Verify output file content
        output_file = Path(self.temp_dir) / "generated" / ".opencode" / "command" / "test.md"
        with open(output_file, 'r') as f:
            content = f.read()

        # Check that all content is merged
        self.assertIn("Test Base Template", content)
        self.assertIn("Elixir Test Template", content)
        self.assertIn("Additional Files", content)
        self.assertIn("Additional Test Information", content)
        self.assertIn("Testing Best Practices", content)

    def test_full_workflow_additional_files_replace(self):
        """Test complete workflow with additional files using replace strategy."""
        # Create additional file
        additional_file_path = Path(self.temp_dir) / "replacement_test_template.md"
        additional_content = """# Replacement Test Template

This completely replaces the default template.

## Replacement Instructions
- Use only this template
- Ignore default templates
"""
        with open(additional_file_path, 'w') as f:
            f.write(additional_content)

        # Create TOML configuration with replace strategy
        toml_content = f"""
[opencode.commands]
test = {{ enabled = true, lang = "elixir", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "default", template_file = "", additional_files = ["{additional_file_path}"], additional_files_strategy = "replace", include_base_template = true }}
"""
        with open(self.config_path, 'w') as f:
            f.write(toml_content)

        # Create base template (should be ignored due to replace strategy)
        base_template_content = "# Test Base Template\n\nThis should not appear."
        base_template_path = self.template_dir / "base.md"
        with open(base_template_path, 'w') as f:
            f.write(base_template_content)

        # Run the generator
        result = self.generator.generate()

        # Verify generation was successful
        self.assertTrue(result)

        # Verify output file content
        output_file = Path(self.temp_dir) / "generated" / ".opencode" / "command" / "test.md"
        with open(output_file, 'r') as f:
            content = f.read()

        # Check that only additional file content is present
        self.assertIn("Replacement Test Template", content)
        self.assertIn("Replacement Instructions", content)
        # Base template should not be present due to replace strategy
        self.assertNotIn("Test Base Template", content)


if __name__ == '__main__':
    unittest.main()
