#!/usr/bin/env python3

import sys
import subprocess
import importlib.util
import io
import contextlib
from pathlib import Path
from typing import List, Dict, Any, Tuple

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

def check_requirements() -> bool:
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    missing_packages = []
    installed_packages = []
    
    for req in requirements:
        if '>=' in req:
            package_name = req.split('>=')[0].strip()
            required_version = req.split('>=')[1].strip()
        elif '==' in req:
            package_name = req.split('==')[0].strip()
            required_version = req.split('==')[1].strip()
        else:
            package_name = req.strip()
            required_version = None
        
        try:
            installed_version = version(package_name)
            if required_version:
                try:
                    from packaging import version as pkg_version
                    if pkg_version.parse(installed_version) >= pkg_version.parse(required_version):
                        installed_packages.append(f"{package_name} (v{installed_version})")
                    else:
                        missing_packages.append(req)
                except ImportError:
                    installed_packages.append(f"{package_name} (v{installed_version})")
            else:
                installed_packages.append(f"{package_name} (v{installed_version})")
        except PackageNotFoundError:
            missing_packages.append(req)
        except ImportError:
            try:
                importlib.import_module(package_name.replace('-', '_'))
                installed_packages.append(f"{package_name} (installed)")
            except ImportError:
                missing_packages.append(req)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        
        response = input("\n📦 Install missing packages? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
                print("✅ Packages installed successfully")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install packages")
                return False
        else:
            print("❌ Cannot proceed without required packages")
            return False
    
    if installed_packages:
        print("✅ All required packages are installed:")
        for pkg in installed_packages:
            print(f"   ✓ {pkg}")
    else:
        print("✅ All required packages are installed")
    return True

def import_generator_class(module_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    class_name_map = {
        'coder_agent': 'CoderAgentGenerator',
        'code_pattern_analyst': 'CodePatternAnalystAgentGenerator', 
        'codebase_agent': 'CodebaseAgentGenerator',
        'debugger': 'DebuggerAgentGenerator',
        'documentation': 'DocumentationAgentGenerator',
        'reviewer': 'ReviewerAgentGenerator',
        'task_manager': 'TaskManagerAgentGenerator',
        'tester': 'TesterAgentGenerator',
        'clean': 'CleanConfigGenerator',
        'commit': 'CommitConfigGenerator',
        'context': 'ContextConfigGenerator',
        'optimizer': 'OptimizerConfigGenerator',
        'prompter': 'PrompterConfigGenerator',
        'test': 'TestConfigGenerator',
        'worktrees': 'WorktreesConfigGenerator'
    }
    
    class_name = class_name_map.get(module_path.stem)
    if class_name and hasattr(module, class_name):
        return getattr(module, class_name)
    return None

def discover_generators() -> Tuple[List[Path], List[Path]]:
    agent_scripts = []
    command_scripts = []
    
    agents_dir = Path("control/agents/scripts")
    if agents_dir.exists():
        for script in agents_dir.glob("*.py"):
            if not script.name.startswith('test_') and script.name != '__init__.py' and 'tests' not in str(script):
                agent_scripts.append(script)
    
    commands_dir = Path("control/commands/scripts")
    if commands_dir.exists():
        for script in commands_dir.glob("*.py"):
            if not script.name.startswith('test_') and script.name != '__init__.py' and 'tests' not in str(script):
                command_scripts.append(script)
    
    return sorted(agent_scripts), sorted(command_scripts)

def run_generator(generator_class: Any, config_path: str = "config.toml") -> Dict[str, Any]:
    try:
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            generator = generator_class(config_path)
            success = generator.generate()
        
        output = captured_output.getvalue()
        warnings = []
        
        for line in output.split('\n'):
            if line.strip().startswith('Warning:'):
                warnings.append(line.strip())
        
        return {
            'success': success,
            'error': None,
            'skipped': not success,
            'warnings': warnings
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'skipped': False,
            'warnings': []
        }

def format_results(results: Dict[str, Dict[str, Any]]) -> None:
    print("\n" + "="*60)
    print("🚀 OPENCODE AGENTS INITIALIZATION RESULTS")
    print("="*60)
    
    successful = []
    skipped = []
    failed = []
    
    for name, result in results.items():
        if result['success']:
            successful.append(name)
        elif result['skipped']:
            skipped.append(name)
        else:
            failed.append((name, result['error']))
    
    if successful:
        print(f"\n✅ SUCCESSFUL GENERATIONS ({len(successful)}):")
        for name in successful:
            print(f"   ✓ {name}")
    
    if skipped:
        print(f"\n⏭️  SKIPPED GENERATIONS ({len(skipped)}):")
        for name in skipped:
            print(f"   - {name} (disabled or no config)")
    
    if failed:
        print(f"\n❌ FAILED GENERATIONS ({len(failed)}):")
        for name, error in failed:
            print(f"   ✗ {name}: {error}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total: {len(results)}")
    print(f"   Successful: {len(successful)}")
    print(f"   Skipped: {len(skipped)}")
    print(f"   Failed: {len(failed)}")
    
    if failed:
        print(f"\n⚠️  {len(failed)} generator(s) failed. Check configuration and try again.")
    elif successful:
        print(f"\n🎉 {len(successful)} generator(s) completed successfully!")
    else:
        print(f"\n ℹ️  All generators were skipped. Check your configuration.")

def main():
    print("🔧 OpenCode Agents Initialization")
    print("-" * 40)
    
    if not check_requirements():
        sys.exit(1)
    
    print("\n🔍 Discovering generators...")
    agent_scripts, command_scripts = discover_generators()
    
    total_generators = len(agent_scripts) + len(command_scripts)
    print(f"   Found {len(agent_scripts)} agent generators")
    print(f"   Found {len(command_scripts)} command generators")
    print(f"   Total: {total_generators} generators")
    
    if total_generators == 0:
        print("❌ No generators found")
        sys.exit(1)
    
    print(f"\n⚙️  Running {total_generators} generators...")
    
    results = {}
    
    for script in agent_scripts:
        generator_class = import_generator_class(script)
        if generator_class:
            result = run_generator(generator_class)
            results[f"agent/{script.stem}"] = result
            if result['success']:
                print(f"   ✅ agent/{script.stem}")
                for warning in result.get('warnings', []):
                    print(f"      ⚠️  {warning}")
            elif result['skipped']:
                print(f"   ⏭️  agent/{script.stem} (skipped)")
            else:
                print(f"   ❌ agent/{script.stem} (failed)")
        else:
            results[f"agent/{script.stem}"] = {
                'success': False,
                'error': 'Could not import generator class',
                'skipped': False,
                'warnings': []
            }
            print(f"   ❌ agent/{script.stem} (import failed)")
    
    for script in command_scripts:
        generator_class = import_generator_class(script)
        if generator_class:
            result = run_generator(generator_class)
            results[f"command/{script.stem}"] = result
            if result['success']:
                print(f"   ✅ command/{script.stem}")
                for warning in result.get('warnings', []):
                    print(f"      ⚠️  {warning}")
            elif result['skipped']:
                print(f"   ⏭️  command/{script.stem} (skipped)")
            else:
                print(f"   ❌ command/{script.stem} (failed)")
        else:
            results[f"command/{script.stem}"] = {
                'success': False,
                'error': 'Could not import generator class',
                'skipped': False,
                'warnings': []
            }
            print(f"   ❌ command/{script.stem} (import failed)")
    
    format_results(results)

if __name__ == "__main__":
    main()
