#!/usr/bin/env python3
"""
Integration tests for the OptimizerConfigGenerator class.

Tests the full workflow integration with real template files and configurations.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the optimizer module directly
sys.path.insert(0, str(project_root / "control" / "commands" / "scripts"))
from optimizer import OptimizerConfigGenerator


class TestOptimizerIntegration(unittest.TestCase):
    """Integration test cases for OptimizerConfigGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.fixtures_dir = self.test_dir / "fixtures"
        self.project_root = project_root
        
    def test_full_workflow_with_real_templates(self):
        """Test the complete workflow with real optimizer template files."""
        config_path = self.fixtures_dir / "optimizer_config_enabled.toml"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = OptimizerConfigGenerator(str(config_path))
            
            # Use the real project root for template files
            generator.project_root = self.project_root
            
            # Override output path to use temp directory
            temp_output_path = Path(temp_dir) / "optimizer.md"
            
            # Load and validate config
            config = generator.load_toml_config()
            optimizer_config = generator.validate_optimizer_config(config)
            
            self.assertIsNotNone(optimizer_config)
            
            # Validate and read template
            template_content = generator.validate_and_read_template(optimizer_config)
            
            self.assertIsNotNone(template_content)
            self.assertGreater(len(template_content), 0)
            
            # Write configuration
            generator.write_yaml_config(optimizer_config, template_content, str(temp_output_path))
            
            # Verify output file exists and has correct content
            self.assertTrue(temp_output_path.exists())
            
            with open(temp_output_path, 'r') as f:
                content = f.read()
            
            # Verify YAML frontmatter
            self.assertIn("---", content)
            self.assertIn("description: Optimizer command", content)
            self.assertIn("agent: build", content)
            self.assertIn("model: anthropic/claude-sonnet-4-20250514", content)
            
            # Verify template content is included
            self.assertGreater(len(content.split("---")[2].strip()), 0)
    
    def test_full_workflow_kotlin_language(self):
        """Test the complete workflow with Kotlin language configuration."""
        config_path = self.fixtures_dir / "optimizer_config_kotlin.toml"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = OptimizerConfigGenerator(str(config_path))
            generator.project_root = self.project_root
            
            temp_output_path = Path(temp_dir) / "optimizer.md"
            
            # Run the full generation process
            config = generator.load_toml_config()
            optimizer_config = generator.validate_optimizer_config(config)
            template_content = generator.validate_and_read_template(optimizer_config)
            generator.write_yaml_config(optimizer_config, template_content, str(temp_output_path))
            
            # Verify the output
            self.assertTrue(temp_output_path.exists())
            
            with open(temp_output_path, 'r') as f:
                content = f.read()
            
            self.assertIn("---", content)
            self.assertIn("description: Optimizer command", content)
    
    def test_full_workflow_with_custom_template(self):
        """Test the complete workflow with custom template configuration."""
        # Create a temporary config file with custom template
        custom_template_path = self.fixtures_dir / "optimizer_custom_template.md"
        
        config_content = f"""[opencode.commands]
optimizer = {{ enabled = true, lang = "elixir", agent = "build", model = "anthropic/claude-sonnet-4-20250514", template = "custom", template_file = "{custom_template_path}", additional_files = [], additional_files_strategy = "merge", include_base_template = false }}"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as config_file:
            config_file.write(config_content)
            config_path = config_file.name
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                generator = OptimizerConfigGenerator(config_path)
                generator.project_root = self.project_root
                
                temp_output_path = Path(temp_dir) / "optimizer.md"
                
                # Run the full generation process
                config = generator.load_toml_config()
                optimizer_config = generator.validate_optimizer_config(config)
                template_content = generator.validate_and_read_template(optimizer_config)
                generator.write_yaml_config(optimizer_config, template_content, str(temp_output_path))
                
                # Verify the output
                self.assertTrue(temp_output_path.exists())
                
                with open(temp_output_path, 'r') as f:
                    content = f.read()
                
                self.assertIn("Custom Optimizer Template", content)
                self.assertIn("optimize the code", content)
        finally:
            os.unlink(config_path)
    
    def test_generate_method_full_integration(self):
        """Test the generate method with full integration."""
        config_path = self.fixtures_dir / "optimizer_config_enabled.toml"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = OptimizerConfigGenerator(str(config_path))
            generator.project_root = self.project_root
            
            # Override the output path to use temp directory
            original_write_method = generator.write_yaml_config
            
            def mock_write_yaml_config(optimizer_config, template_content, output_path=None):
                temp_output_path = Path(temp_dir) / "optimizer.md"
                return original_write_method(optimizer_config, template_content, str(temp_output_path))
            
            generator.write_yaml_config = mock_write_yaml_config
            
            # Run the generate method
            result = generator.generate()
            
            self.assertTrue(result)
            
            # Verify output file was created
            output_file = Path(temp_dir) / "optimizer.md"
            self.assertTrue(output_file.exists())
            
            # Verify content structure
            with open(output_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            self.assertEqual(lines[0], '---')
            self.assertIn('description:', content)
            self.assertIn('agent:', content)
            self.assertIn('model:', content)
            
            # Find the closing frontmatter
            closing_frontmatter_index = None
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    closing_frontmatter_index = i
                    break
            
            self.assertIsNotNone(closing_frontmatter_index)
            
            # Verify there's content after the frontmatter
            content_after_frontmatter = '\n'.join(lines[closing_frontmatter_index + 1:]).strip()
            self.assertGreater(len(content_after_frontmatter), 0)


if __name__ == '__main__':
    unittest.main()
