#!/usr/bin/env python3
"""
Plugin Directory Generator Script

This script generates the .opencode/plugin directory structure in the generated folder
and adds a .gitkeep file to ensure the directory persists in version control.
"""

import os
import pathlib
from typing import Optional


def create_plugin_directory(base_path: Optional[str] = None) -> bool:
    """
    Create the .opencode/plugin directory structure with a .gitkeep file.
    
    Args:
        base_path: Base path for the generated directory. If None, uses the script's location.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Determine the base path
        if base_path is None:
            # Get the script's directory and go up to find the ogc directory
            script_dir = pathlib.Path(__file__).parent
            base_path = script_dir.parent / "generated"
        else:
            base_path = pathlib.Path(base_path)
        
        # Create the .opencode/plugin directory structure
        plugin_dir = base_path / ".opencode" / "plugin"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .gitkeep file to ensure directory persists in git
        gitkeep_file = plugin_dir / ".gitkeep"
        gitkeep_file.write_text("# This file ensures the plugin directory is tracked by git\n")
        
        # Create a README.md for documentation
        readme_file = plugin_dir / "README.md"
        readme_content = """# Plugin Directory

This directory is intended for OpenCode agent plugins.

## Structure
- Place plugin files in this directory
- Subdirectories can be created for organized plugin categories
- The `.gitkeep` file ensures this directory is tracked by version control

## Usage
Plugins placed in this directory will be automatically discovered by the OpenCode agent system.
"""
        readme_file.write_text(readme_content)
        
        print(f"✅ Successfully created plugin directory: {plugin_dir}")
        print(f"📁 Created files:")
        print(f"   - {gitkeep_file}")
        print(f"   - {readme_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating plugin directory: {e}")
        return False


def main():
    """Main function to run the plugin directory generator."""
    print("🚀 OpenCode Plugin Directory Generator")
    print("=" * 40)
    
    success = create_plugin_directory()
    
    if success:
        print("\n✨ Plugin directory setup complete!")
    else:
        print("\n💥 Plugin directory setup failed!")
        exit(1)


if __name__ == "__main__":
    main()