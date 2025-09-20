#!/usr/bin/env python3
"""
Integration tests for the debugger agent generator.

This module contains integration tests that test the full workflow of the
DebuggerAgentGenerator class from configuration loading to file generation.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the parent directory to the path to import the generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from debugger import DebuggerAgentGenerator


class TestDebuggerGeneratorIntegration(unittest.TestCase):
    """Integration test cases for the DebuggerAgentGenerator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.toml"
        
        # Create template directory structure
        self.template_dir = Path(self.temp_dir) / "ogc/control/agents/debugger"
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create base template
        base_template_content = """You are an intelligent debugging agent that analyzes provided arguments to determine the optimal debugging approach.

## Core Responsibilities

- **Argument Analysis**: Parse input to understand debugging scope, language, and context
- **Technology Detection**: Identify the appropriate language/framework from available configurations
- **Adaptive Debugging**: Apply language-specific debugging techniques when configured languages are detected
"""
        
        with open(self.template_dir / "base.md", 'w') as f:
            f.write(base_template_content)
        
        # Create language-specific templates
        elixir_template = """### Core Tools & Commands

**Basic Debugging:**

```elixir
# Pipeline inspection
data |> IO.inspect(label: "checkpoint") |> process()

# Enhanced debugging (Elixir 1.14+)
result |> dbg()
```
"""
        
        kotlin_template = """### Kotlin Debugging Tools

**Basic Debugging:**

```kotlin
// Debug logging
println("Debug: $variable")

// Breakpoint debugging
debugger()
```
"""
        
        typescript_template = """### TypeScript Debugging Tools

**Basic Debugging:**

```typescript
// Debug logging
console.log('Debug:', variable);

// Debugger statement
debugger;
```
"""
        
        with open(self.template_dir / "elixir.md", 'w') as f:
            f.write(elixir_template)
        
        with open(self.template_dir / "kotlin.md", 'w') as f:
            f.write(kotlin_template)
        
        with open(self.template_dir / "typescript.md", 'w') as f:
            f.write(typescript_template)
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_config_file(self, config_content: str):
        """Helper method to create a config file with given content."""
        with open(self.config_path, 'w') as f:
            f.write(config_content)
    
    def test_full_workflow_elixir_subagent(self):
        """Test full workflow with Elixir language and subagent mode."""
        config_content = """
[opencode.agents.subagents]
debugger = {enabled = true, template = "default", lang = "elixir", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true, description = "Elixir debugging specialist", mode = "subagent", model = "anthropic/claude-sonnet-4-20250514", temperature = 0.1, permissions = { tools = { read = true, edit = true, write = false, grep = true, glob = true, patch = false, bash = true }, bash_rules = { "rm -rf *" = "deny", "sudo *" = "deny", "mix *" = "allow", "git *" = "allow" }, edit_rules = { "**/*.env*" = "deny", "**/*.key" = "deny", "**/*.secret" = "deny" } } }
"""
        
        self.create_config_file(config_content)
        generator = DebuggerAgentGenerator(str(self.config_path))
        
        # Update the generator's project root to point to our temp directory
        generator.project_root = Path(self.temp_dir)
        
        # Execute the full workflow
        success = generator.generate()
        
        # Verify success
        self.assertTrue(success)
        
        # Verify output file was created
        expected_output_path = Path(self.temp_dir) / "ogc/generated/.opencode/agent/subagent/debugger.md"
        self.assertTrue(expected_output_path.exists())
        
        # Verify output content
        with open(expected_output_path, 'r') as f:
            content = f.read()
        
        # Check YAML frontmatter
        self.assertIn('---', content)
        self.assertIn('description: "Elixir debugging specialist"', content)
        self.assertIn('mode: "subagent"', content)
        self.assertIn('model: "anthropic/claude-sonnet-4-20250514"', content)
        self.assertIn('temperature: 0.1', content)
        self.assertIn('permissions:', content)
        self.assertIn('tools:', content)
        self.assertIn('bash:', content)
        self.assertIn('edit:', content)
        
        # Check that config keys are excluded
        self.assertNotIn('enabled:', content)
        self.assertNotIn('template:', content)
        self.assertNotIn('lang:', content)
        self.assertNotIn('include_base_template:', content)
        
        # Check base template content
        self.assertIn('You are an intelligent debugging agent', content)
        
        # Check Elixir-specific content
        self.assertIn('# Elixir Debugging Specifics', content)
        self.assertIn('Pipeline inspection', content)
        self.assertIn('IO.inspect', content)
    
    def test_full_workflow_kotlin_primary(self):
        """Test full workflow with Kotlin language and primary mode."""
        config_content = """
[opencode.agents.subagents]
debugger = {enabled = true, template = "default", lang = "kotlin", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = true, description = "Kotlin debugging specialist", mode = "primary", model = "anthropic/claude-sonnet-4-20250514", temperature = 0.2, permissions = { tools = { read = true, edit = true, write = true, grep = true, glob = true, patch = true, bash = true }, bash_rules = { "rm -rf *" = "ask", "sudo *" = "deny", "./gradlew *" = "allow" }, edit_rules = { "**/*.env*" = "deny", "**/*.key" = "deny" } } }
"""
        
        self.create_config_file(config_content)
        generator = DebuggerAgentGenerator(str(self.config_path))
        
        # Update the generator's project root to point to our temp directory
        generator.project_root = Path(self.temp_dir)
        
        # Execute the full workflow
        success = generator.generate()
        
        # Verify success
        self.assertTrue(success)
        
        # Verify output file was created in primary agent directory
        expected_output_path = Path(self.temp_dir) / "ogc/generated/.opencode/agent/debugger.md"
        self.assertTrue(expected_output_path.exists())
        
        # Verify output content
        with open(expected_output_path, 'r') as f:
            content = f.read()
        
        # Check YAML frontmatter
        self.assertIn('description: "Kotlin debugging specialist"', content)
        self.assertIn('mode: "primary"', content)
        self.assertIn('temperature: 0.2', content)
        
        # Check Kotlin-specific content
        self.assertIn('# Kotlin Debugging Specifics', content)
        self.assertIn('println("Debug: $variable")', content)
    
    def test_full_workflow_typescript_base_only(self):
        """Test full workflow with TypeScript language but no base template."""
        config_content = """
[opencode.agents.subagents]
debugger = {enabled = true, template = "default", lang = "typescript", template_file = "", additional_files = [], additional_files_strategy = "merge", include_base_template = false, description = "TypeScript debugging specialist", mode = "subagent", model = "anthropic/claude-sonnet-4-20250514", temperature = 0.0, permissions = { tools = { read = true, edit = false, write = false, grep = true, glob = true, patch = false, bash = false }, bash_rules = {}, edit_rules = {} } }
"""
        
        self.create_config_file(config_content)
        generator = DebuggerAgentGenerator(str(self.config_path))
        
        # Update the generator's project root to point to our temp directory
        generator.project_root = Path(self.temp_dir)
        
        # Execute the full workflow
        success = generator.generate()
        
        # Verify success
        self.assertTrue(success)
        
        # Verify output file was created
        expected_output_path = Path(self.temp_dir) / "ogc/generated/.opencode/agent/subagent/debugger.md"
        self.assertTrue(expected_output_path.exists())
        
        # Verify output content
        with open(expected_output_path, 'r') as f:
            content = f.read()
        
        # Check YAML frontmatter
        self.assertIn('description: "TypeScript debugging specialist"', content)
        self.assertIn('temperature: 0.0', content)
        
        # Should NOT have base template content
        self.assertNotIn('You are an intelligent debugging agent', content)
        
        # Should have TypeScript-specific content
        self.assertIn('# Typescript Debugging Specifics', content)
        self.assertIn('console.log', content)
    
    def test_full_workflow_disabled_configuration(self):
        """Test full workflow with disabled debugger configuration."""
        config_content = """
[opencode.agents.subagents]
debugger = {enabled = false, template = "default", lang = "elixir", description = "Disabled debugger", mode = "subagent"}
"""
        
        self.create_config_file(config_content)
        generator = DebuggerAgentGenerator(str(self.config_path))
        
        # Update the generator's project root to point to our temp directory
        generator.project_root = Path(self.temp_dir)
        
        # Execute the full workflow
        success = generator.generate()
        
        # Verify that generation was skipped
        self.assertFalse(success)
        
        # Verify no output file was created
        expected_output_path = Path(self.temp_dir) / "ogc/generated/.opencode/agent/subagent/debugger.md"
        self.assertFalse(expected_output_path.exists())
    
    def test_full_workflow_custom_template(self):
        """Test full workflow with custom template."""
        # Create custom template
        custom_template_content = """# Custom Debugger Agent

This is a custom debugger template with specific instructions.

## Custom Features

- Feature 1
- Feature 2
"""
        
        custom_template_path = Path(self.temp_dir) / "custom_debugger.md"
        with open(custom_template_path, 'w') as f:
            f.write(custom_template_content)
        
        config_content = f"""
[opencode.agents.subagents]
debugger = {{enabled = true, template = "custom", template_file = "{custom_template_path}", additional_files = [], additional_files_strategy = "merge", description = "Custom debugger", mode = "subagent", model = "anthropic/claude-sonnet-4-20250514", temperature = 0.1, permissions = {{ tools = {{ read = true, edit = true }}, bash_rules = {{}}, edit_rules = {{}} }} }}
"""
        
        self.create_config_file(config_content)
        generator = DebuggerAgentGenerator(str(self.config_path))
        
        # Update the generator's project root to point to our temp directory
        generator.project_root = Path(self.temp_dir)
        
        # Execute the full workflow
        success = generator.generate()
        
        # Verify success
        self.assertTrue(success)
        
        # Verify output file was created
        expected_output_path = Path(self.temp_dir) / "ogc/generated/.opencode/agent/subagent/debugger.md"
        self.assertTrue(expected_output_path.exists())
        
        # Verify output content
        with open(expected_output_path, 'r') as f:
            content = f.read()
        
        # Check custom template content
        self.assertIn('# Custom Debugger Agent', content)
        self.assertIn('This is a custom debugger template', content)
        self.assertIn('Custom Features', content)
    
    def test_full_workflow_additional_files_merge(self):
        """Test full workflow with additional files using merge strategy."""
        # Create additional file
        additional_file_content = """## Additional Debugging Guidelines

### Security Considerations

- Always validate inputs
- Use secure debugging practices
- Clean up after debugging
"""
        
        additional_file_path = Path(self.temp_dir) / "additional_debug.md"
        with open(additional_file_path, 'w') as f:
            f.write(additional_file_content)
        
        config_content = f"""
[opencode.agents.subagents]
debugger = {{enabled = true, template = "default", lang = "elixir", additional_files = ["{additional_file_path}"], additional_files_strategy = "merge", include_base_template = true, description = "Enhanced debugger", mode = "subagent", model = "anthropic/claude-sonnet-4-20250514", temperature = 0.1, permissions = {{ tools = {{ read = true }}, bash_rules = {{}}, edit_rules = {{}} }} }}
"""
        
        self.create_config_file(config_content)
        generator = DebuggerAgentGenerator(str(self.config_path))
        
        # Update the generator's project root to point to our temp directory
        generator.project_root = Path(self.temp_dir)
        
        # Execute the full workflow
        success = generator.generate()
        
        # Verify success
        self.assertTrue(success)
        
        # Verify output file was created
        expected_output_path = Path(self.temp_dir) / "ogc/generated/.opencode/agent/subagent/debugger.md"
        self.assertTrue(expected_output_path.exists())
        
        # Verify output content
        with open(expected_output_path, 'r') as f:
            content = f.read()
        
        # Check base template content
        self.assertIn('You are an intelligent debugging agent', content)
        
        # Check Elixir-specific content
        self.assertIn('# Elixir Debugging Specifics', content)
        
        # Check additional files content
        self.assertIn('# Additional Files', content)
        self.assertIn('Additional Debugging Guidelines', content)
        self.assertIn('Security Considerations', content)
    
    def test_full_workflow_additional_files_replace(self):
        """Test full workflow with additional files using replace strategy."""
        # Create additional file
        replacement_content = """# Replacement Debugger Content

This content replaces the default template entirely.

## Replacement Features

- Custom debugging approach
- Specialized tools
"""
        
        replacement_file_path = Path(self.temp_dir) / "replacement_debug.md"
        with open(replacement_file_path, 'w') as f:
            f.write(replacement_content)
        
        config_content = f"""
[opencode.agents.subagents]
debugger = {{enabled = true, template = "default", lang = "elixir", additional_files = ["{replacement_file_path}"], additional_files_strategy = "replace", include_base_template = true, description = "Replacement debugger", mode = "subagent", model = "anthropic/claude-sonnet-4-20250514", temperature = 0.1, permissions = {{ tools = {{ read = true }}, bash_rules = {{}}, edit_rules = {{}} }} }}
"""
        
        self.create_config_file(config_content)
        generator = DebuggerAgentGenerator(str(self.config_path))
        
        # Update the generator's project root to point to our temp directory
        generator.project_root = Path(self.temp_dir)
        
        # Execute the full workflow
        success = generator.generate()
        
        # Verify success
        self.assertTrue(success)
        
        # Verify output file was created
        expected_output_path = Path(self.temp_dir) / "ogc/generated/.opencode/agent/subagent/debugger.md"
        self.assertTrue(expected_output_path.exists())
        
        # Verify output content
        with open(expected_output_path, 'r') as f:
            content = f.read()
        
        # Should NOT have base template content (replaced)
        self.assertNotIn('You are an intelligent debugging agent', content)
        
        # Should have replacement content
        self.assertIn('# Replacement Debugger Content', content)
        self.assertIn('This content replaces the default template', content)


if __name__ == '__main__':
    unittest.main()
