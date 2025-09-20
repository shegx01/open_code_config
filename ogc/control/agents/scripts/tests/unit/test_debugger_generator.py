#!/usr/bin/env python3
"""
Unit tests for the debugger agent generator.

This module contains comprehensive unit tests for the DebuggerAgentGenerator class,
covering configuration loading, validation, template handling, and agent file generation.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

# Add the parent directory to the path to import the generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from debugger import DebuggerAgentGenerator


class TestDebuggerAgentGenerator(unittest.TestCase):
    """Test cases for the DebuggerAgentGenerator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.toml"
        self.generator = DebuggerAgentGenerator(str(self.config_path))
        
        # Create a sample debugger template
        self.template_content = """You are an intelligent debugging agent that analyzes provided arguments to determine the optimal debugging approach.

## Core Responsibilities

- **Argument Analysis**: Parse input to understand debugging scope, language, and context
- **Technology Detection**: Identify the appropriate language/framework from available configurations
- **Adaptive Debugging**: Apply language-specific debugging techniques when configured languages are detected
"""
        
        # Create sample language-specific templates
        self.elixir_template = """### Core Tools & Commands

**Basic Debugging:**

```elixir
# Pipeline inspection
data |> IO.inspect(label: "checkpoint") |> process()

# Enhanced debugging (Elixir 1.14+)
result |> dbg()
```
"""
        
        self.kotlin_template = """### Kotlin Debugging Tools

**Basic Debugging:**

```kotlin
// Debug logging
println("Debug: $variable")

// Breakpoint debugging
debugger()
```
"""
        
        self.typescript_template = """### TypeScript Debugging Tools

**Basic Debugging:**

```typescript
// Debug logging
console.log('Debug:', variable);

// Debugger statement
debugger;
```
"""
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_config_file(self, config_content: str):
        """Helper method to create a config file with given content."""
        with open(self.config_path, 'w') as f:
            f.write(config_content)
    
    def create_template_files(self, base_content: str = None, lang_contents: dict = None):
        """Helper method to create template files."""
        # Create debugger template directory
        template_dir = Path(self.temp_dir) / "ogc/control/agents/debugger"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create base template
        base_template_path = template_dir / "base.md"
        with open(base_template_path, 'w') as f:
            f.write(base_content or self.template_content)
        
        # Create language-specific templates
        if lang_contents:
            for lang, content in lang_contents.items():
                lang_template_path = template_dir / f"{lang}.md"
                with open(lang_template_path, 'w') as f:
                    f.write(content)
    
    def test_load_toml_config_success(self):
        """Test successful TOML configuration loading."""
        config_content = """
[opencode.agents.subagents]
debugger = {enabled = true, template = "default", lang = "elixir"}
"""
        self.create_config_file(config_content)
        
        config = self.generator.load_toml_config()
        
        self.assertIn('opencode', config)
        self.assertIn('agents', config['opencode'])
        self.assertIn('subagents', config['opencode']['agents'])
        self.assertIn('debugger', config['opencode']['agents']['subagents'])
    
    def test_load_toml_config_file_not_found(self):
        """Test TOML configuration loading when file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            self.generator.load_toml_config()
    
    def test_load_toml_config_invalid_toml(self):
        """Test TOML configuration loading with invalid TOML syntax."""
        self.create_config_file("invalid toml content [[[")
        
        with self.assertRaises(ValueError):
            self.generator.load_toml_config()
    
    def test_validate_debugger_config_enabled(self):
        """Test debugger configuration validation when enabled."""
        config = {
            'opencode': {
                'agents': {
                    'subagents': {
                        'debugger': {'enabled': True, 'lang': 'elixir'}
                    }
                }
            }
        }
        
        result = self.generator.validate_debugger_config(config)
        
        self.assertIsNotNone(result)
        self.assertTrue(result['enabled'])
        self.assertEqual(result['lang'], 'elixir')
    
    def test_validate_debugger_config_disabled(self):
        """Test debugger configuration validation when disabled."""
        config = {
            'opencode': {
                'agents': {
                    'subagents': {
                        'debugger': {'enabled': False}
                    }
                }
            }
        }
        
        result = self.generator.validate_debugger_config(config)
        
        self.assertIsNone(result)
    
    def test_validate_debugger_config_missing(self):
        """Test debugger configuration validation when config is missing."""
        config = {'opencode': {'agents': {'subagents': {}}}}
        
        result = self.generator.validate_debugger_config(config)
        
        self.assertIsNone(result)
    
    def test_validate_debugger_config_no_opencode_section(self):
        """Test debugger configuration validation when opencode section is missing."""
        config = {}
        
        result = self.generator.validate_debugger_config(config)
        
        self.assertIsNone(result)
    
    def test_validate_and_read_template_default_elixir(self):
        """Test template validation and reading with default template and Elixir language."""
        self.create_template_files(
            base_content=self.template_content,
            lang_contents={'elixir': self.elixir_template}
        )
        
        # Update the generator's project root to point to our temp directory
        self.generator.project_root = Path(self.temp_dir)
        
        debugger_config = {
            'template': 'default',
            'lang': 'elixir',
            'include_base_template': True,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(debugger_config)
        
        self.assertIn("You are an intelligent debugging agent", result)
        self.assertIn("# Elixir Debugging Specifics", result)
        self.assertIn("Pipeline inspection", result)
    
    def test_validate_and_read_template_default_kotlin(self):
        """Test template validation and reading with default template and Kotlin language."""
        self.create_template_files(
            base_content=self.template_content,
            lang_contents={'kotlin': self.kotlin_template}
        )
        
        # Update the generator's project root to point to our temp directory
        self.generator.project_root = Path(self.temp_dir)
        
        debugger_config = {
            'template': 'default',
            'lang': 'kotlin',
            'include_base_template': True,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(debugger_config)
        
        self.assertIn("You are an intelligent debugging agent", result)
        self.assertIn("# Kotlin Debugging Specifics", result)
        self.assertIn("Debug logging", result)
    
    def test_validate_and_read_template_default_typescript(self):
        """Test template validation and reading with default template and TypeScript language."""
        self.create_template_files(
            base_content=self.template_content,
            lang_contents={'typescript': self.typescript_template}
        )
        
        # Update the generator's project root to point to our temp directory
        self.generator.project_root = Path(self.temp_dir)
        
        debugger_config = {
            'template': 'default',
            'lang': 'typescript',
            'include_base_template': True,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(debugger_config)
        
        self.assertIn("You are an intelligent debugging agent", result)
        self.assertIn("# Typescript Debugging Specifics", result)
        self.assertIn("console.log", result)
    
    def test_validate_and_read_template_unsupported_language(self):
        """Test template validation with unsupported language."""
        debugger_config = {
            'template': 'default',
            'lang': 'python',  # Unsupported language
            'include_base_template': True,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(debugger_config)
        
        self.assertIn("Unsupported language: python", str(context.exception))
        self.assertIn("elixir, kotlin, typescript", str(context.exception))
    
    def test_validate_and_read_template_base_only(self):
        """Test template validation with base template only (no language)."""
        self.create_template_files(base_content=self.template_content)
        
        # Update the generator's project root to point to our temp directory
        self.generator.project_root = Path(self.temp_dir)
        
        debugger_config = {
            'template': 'default',
            'lang': '',  # No language specified
            'include_base_template': True,
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(debugger_config)
        
        self.assertIn("You are an intelligent debugging agent", result)
        self.assertNotIn("# Elixir Debugging Specifics", result)
    
    def test_validate_and_read_template_language_only(self):
        """Test template validation with language template only (no base)."""
        self.create_template_files(
            base_content=self.template_content,
            lang_contents={'elixir': self.elixir_template}
        )
        
        # Update the generator's project root to point to our temp directory
        self.generator.project_root = Path(self.temp_dir)
        
        debugger_config = {
            'template': 'default',
            'lang': 'elixir',
            'include_base_template': False,  # Don't include base
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(debugger_config)
        
        self.assertNotIn("You are an intelligent debugging agent", result)
        self.assertIn("# Elixir Debugging Specifics", result)
        self.assertIn("Pipeline inspection", result)
    
    def test_validate_and_read_template_custom_template(self):
        """Test template validation with custom template."""
        custom_template_content = "Custom debugger template content"
        custom_template_path = self.temp_dir / Path("custom_debugger.md")
        with open(custom_template_path, 'w') as f:
            f.write(custom_template_content)
        
        debugger_config = {
            'template': 'custom',
            'template_file': str(custom_template_path),
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        result = self.generator.validate_and_read_template(debugger_config)
        
        self.assertEqual(result, custom_template_content)
    
    def test_validate_and_read_template_custom_template_missing_file(self):
        """Test template validation with custom template but missing template_file."""
        debugger_config = {
            'template': 'custom',
            'template_file': '',  # Missing template file
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(debugger_config)
        
        self.assertIn("Custom template specified but template_file is empty", str(context.exception))
    
    def test_validate_and_read_template_custom_template_file_not_found(self):
        """Test template validation with custom template file that doesn't exist."""
        debugger_config = {
            'template': 'custom',
            'template_file': '/nonexistent/template.md',
            'additional_files': [],
            'additional_files_strategy': 'merge'
        }
        
        with self.assertRaises(FileNotFoundError) as context:
            self.generator.validate_and_read_template(debugger_config)
        
        self.assertIn("Custom template file not found", str(context.exception))
    
    def test_validate_and_read_template_invalid_strategy(self):
        """Test template validation with invalid additional_files_strategy."""
        debugger_config = {
            'template': 'default',
            'additional_files': [],
            'additional_files_strategy': 'invalid_strategy'
        }
        
        with self.assertRaises(ValueError) as context:
            self.generator.validate_and_read_template(debugger_config)
        
        self.assertIn("Invalid additional_files_strategy: invalid_strategy", str(context.exception))
    
    def test_get_output_path_subagent_mode(self):
        """Test output path generation for subagent mode."""
        debugger_config = {'mode': 'subagent'}
        
        result = self.generator._get_output_path(debugger_config)
        
        self.assertEqual(result, "ogc/generated/.opencode/agent/subagent/debugger.md")
    
    def test_get_output_path_primary_mode(self):
        """Test output path generation for primary mode."""
        debugger_config = {'mode': 'primary'}
        
        result = self.generator._get_output_path(debugger_config)
        
        self.assertEqual(result, "ogc/generated/.opencode/agent/debugger.md")
    
    def test_get_output_path_default_mode(self):
        """Test output path generation for default mode (no mode specified)."""
        debugger_config = {}
        
        result = self.generator._get_output_path(debugger_config)
        
        self.assertEqual(result, "ogc/generated/.opencode/agent/debugger.md")
    
    def test_extract_agent_config_excludes_config_keys(self):
        """Test that agent configuration extraction excludes config-specific keys."""
        debugger_config = {
            'enabled': True,
            'template': 'default',
            'template_file': 'custom.md',
            'additional_files': ['file1.md'],
            'additional_files_strategy': 'merge',
            'include_base_template': True,
            'lang': 'elixir',
            'description': 'Test debugger',
            'mode': 'subagent',
            'model': 'claude-4',
            'temperature': 0.1
        }
        
        result = self.generator._extract_agent_config(debugger_config)
        
        # Should include agent configuration
        self.assertIn('description', result)
        self.assertIn('mode', result)
        self.assertIn('model', result)
        self.assertIn('temperature', result)
        
        # Should exclude config keys
        self.assertNotIn('enabled', result)
        self.assertNotIn('template', result)
        self.assertNotIn('template_file', result)
        self.assertNotIn('additional_files', result)
        self.assertNotIn('additional_files_strategy', result)
        self.assertNotIn('include_base_template', result)
        self.assertNotIn('lang', result)
    
    def test_format_permissions_structure(self):
        """Test permissions structure formatting."""
        permissions = {
            'tools': {'read': True, 'write': False, 'bash': True},
            'bash_rules': {'rm -rf *': 'deny', 'git *': 'allow'},
            'edit_rules': {'**/*.env*': 'deny', '**/*.key': 'deny'}
        }
        
        result = self.generator._format_permissions(permissions)
        
        self.assertIn('tools', result)
        self.assertIn('bash', result)
        self.assertIn('edit', result)
        self.assertEqual(result['tools'], permissions['tools'])
        self.assertEqual(result['bash'], permissions['bash_rules'])
        self.assertEqual(result['edit'], permissions['edit_rules'])
    
    def test_format_permissions_empty(self):
        """Test permissions structure formatting with empty permissions."""
        permissions = {}
        
        result = self.generator._format_permissions(permissions)
        
        self.assertEqual(result, {})
    
    def test_strip_frontmatter_with_frontmatter(self):
        """Test stripping YAML frontmatter from content."""
        content_with_frontmatter = """---
title: Test
description: Test content
---

This is the actual content.
More content here.
"""
        
        result = self.generator._strip_frontmatter(content_with_frontmatter)
        
        self.assertEqual(result, "This is the actual content.\nMore content here.\n")
    
    def test_strip_frontmatter_without_frontmatter(self):
        """Test stripping YAML frontmatter from content without frontmatter."""
        content_without_frontmatter = "This is content without frontmatter.\nMore content here."
        
        result = self.generator._strip_frontmatter(content_without_frontmatter)
        
        self.assertEqual(result, content_without_frontmatter)
    
    def test_strip_frontmatter_incomplete_frontmatter(self):
        """Test stripping YAML frontmatter with incomplete frontmatter."""
        content_incomplete = """---
title: Test
description: Test content
This is content without closing frontmatter.
"""
        
        result = self.generator._strip_frontmatter(content_incomplete)
        
        # Should return original content if frontmatter is incomplete
        self.assertEqual(result, content_incomplete)


if __name__ == '__main__':
    unittest.main()
