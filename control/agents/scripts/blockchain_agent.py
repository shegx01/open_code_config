import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: Neither tomllib (Python 3.11+) nor tomli package is available.", file=sys.stderr)
        print("Please install tomli: pip install tomli", file=sys.stderr)
        sys.exit(1)

BASE_TEMPLATE_PATH = "control/agents/subagents/blockchain-agent/base.md"
LANG_TEMPLATE_PATH = "control/agents/subagents/blockchain-agent/{lang}.md"
OUTPUT_PATH = "generated/.opencode/agent/subagent/blockchain-agent.md"
CONFIG_KEYS = {'enabled', 'template', 'template_file', 'additional_files', 'additional_files_strategy', 'include_base_template', 'lang'}
SUPPORTED_LANGUAGES = ['elixir', 'typescript']


class BlockchainAgentGenerator:

    def __init__(self, config_path: str = "config.toml"):
        self.config_path = Path(config_path)
        if self.config_path.is_absolute():
            self.project_root = self.config_path.parent
        else:
            self.config_path = self.config_path.resolve()
            self.project_root = self.config_path.parent

    def load_toml_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'rb') as f:
                return tomllib.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML configuration: {e}")

    def validate_blockchain_agent_config(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        opencode_config = config.get('opencode', {})
        agents_config = opencode_config.get('agents', {})
        subagents_config = agents_config.get('subagents', {})
        blockchain_agent_config = subagents_config.get('blockchain-agent', {})

        if not blockchain_agent_config:
            print("No blockchain-agent configuration found in TOML file")
            return None

        if not blockchain_agent_config.get('enabled', True):
            print("Blockchain-agent subagent is disabled (enabled = false)")
            return None

        return blockchain_agent_config

    def validate_and_read_template(self, blockchain_agent_config: Dict[str, Any]) -> str:
        template_type = blockchain_agent_config.get('template', 'default')
        template_file = blockchain_agent_config.get('template_file', '')
        additional_files = blockchain_agent_config.get('additional_files', [])
        additional_files_strategy = blockchain_agent_config.get('additional_files_strategy', 'merge')
        include_base_template = blockchain_agent_config.get('include_base_template', True)
        lang = blockchain_agent_config.get('lang', '')

        if lang and lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {lang}. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}")

        if additional_files_strategy not in ['merge', 'replace']:
            raise ValueError(f"Invalid additional_files_strategy: {additional_files_strategy}. Must be 'merge' or 'replace'")

        if template_type == 'custom' and not template_file:
            raise ValueError("Custom template specified but template_file is empty")
        
        if template_type == 'default' and template_file:
            print(f"Warning: template_file '{template_file}' specified but template is 'default'. template_file will be ignored.")

        main_template_content = ""
        if additional_files_strategy != 'replace' or not additional_files:
            if template_type == 'default':
                template_content_parts = []

                if include_base_template:
                    base_template_path = self.project_root / BASE_TEMPLATE_PATH
                    if not base_template_path.exists():
                        raise FileNotFoundError(f"Base template not found: {base_template_path}")

                    try:
                        with open(base_template_path, 'r', encoding='utf-8') as f:
                            base_content = f.read()
                            template_content_parts.append(base_content)
                    except Exception as e:
                        raise ValueError(f"Failed to read base template {base_template_path}: {e}")

                if lang:
                    lang_template_path = self.project_root / LANG_TEMPLATE_PATH.format(lang=lang)
                    if not lang_template_path.exists():
                        raise FileNotFoundError(f"Language template not found: {lang_template_path}")

                    if lang_template_path.stat().st_size == 0:
                        print(f"Warning: Language template is empty: {lang_template_path}. Skipping language-specific content.")
                    else:
                        try:
                            with open(lang_template_path, 'r', encoding='utf-8') as f:
                                lang_content = f.read()
                                template_content_parts.append(f"\n\n# {lang.title()} Blockchain Development Specifics\n\n{lang_content}")
                        except Exception as e:
                            raise ValueError(f"Failed to read language template {lang_template_path}: {e}")

                if template_content_parts:
                    main_template_content = "\n".join(template_content_parts)
                else:
                    raise ValueError("No template content available. Either include_base_template must be true or a language must be specified.")

            elif template_type == 'custom':
                if not template_file:
                    raise ValueError("Custom template specified but template_file is empty")

                custom_template_path = Path(template_file)
                if not custom_template_path.is_absolute():
                    custom_template_path = self.project_root / custom_template_path

                if not custom_template_path.exists():
                    raise FileNotFoundError(f"Custom template file not found: {custom_template_path}")

                if custom_template_path.stat().st_size == 0:
                    raise ValueError(f"Custom template file is empty: {custom_template_path}")

                try:
                    with open(custom_template_path, 'r', encoding='utf-8') as f:
                        main_template_content = f.read()
                except Exception as e:
                    raise ValueError(f"Failed to read custom template file {custom_template_path}: {e}")
            else:
                raise ValueError(f"Unknown template type: {template_type}")

        additional_content = self._process_additional_files(additional_files)

        if additional_files_strategy == 'replace' and additional_files:
            return additional_content
        elif additional_files_strategy == 'merge':
            if additional_content:
                return f"{main_template_content}\n\n# Additional Files\n\n{additional_content}"
            else:
                return main_template_content
        else:
            return main_template_content

    def _process_additional_files(self, additional_files: list) -> str:
        if not additional_files:
            return ""

        combined_content = []

        for file_path in additional_files:
            additional_file_path = Path(file_path)
            if not additional_file_path.is_absolute():
                additional_file_path = self.project_root / additional_file_path

            if not additional_file_path.exists():
                raise FileNotFoundError(f"Additional file not found: {additional_file_path}")

            try:
                with open(additional_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        combined_content.append(f"## {additional_file_path.name}\n\n{content}")
            except Exception as e:
                raise ValueError(f"Failed to read additional file {additional_file_path}: {e}")

        return "\n\n".join(combined_content)

    def _get_output_path(self, blockchain_agent_config: Dict[str, Any]) -> str:
        return OUTPUT_PATH

    def _extract_agent_config(self, blockchain_agent_config: Dict[str, Any]) -> Dict[str, Any]:
        agent_config = {}
        for key, value in blockchain_agent_config.items():
            if key not in CONFIG_KEYS:
                agent_config[key] = value

        return agent_config

    def _format_permissions(self, permissions: Dict[str, Any]) -> Dict[str, Any]:
        if not permissions:
            return {}

        formatted_permissions = {}

        tools = permissions.get('tools', {})
        if tools:
            formatted_permissions['tools'] = tools

        bash_rules = permissions.get('bash_rules', {})
        if bash_rules:
            formatted_permissions['bash'] = bash_rules

        edit_rules = permissions.get('edit_rules', {})
        if edit_rules:
            formatted_permissions['edit'] = edit_rules

        return formatted_permissions

    def write_agent_config(self, blockchain_agent_config: Dict[str, Any], template_content: str) -> None:
        output_path = self._get_output_path(blockchain_agent_config)
        output_file = self.project_root / output_path

        output_file.parent.mkdir(parents=True, exist_ok=True)

        clean_content = self._strip_frontmatter(template_content)

        agent_config = self._extract_agent_config(blockchain_agent_config)

        if 'permissions' in agent_config:
            agent_config['permissions'] = self._format_permissions(agent_config['permissions'])

        frontmatter_lines = ["---"]

        for key, value in agent_config.items():
            if key == 'permissions':
                frontmatter_lines.append(f"{key}:")
                for perm_key, perm_value in value.items():
                    if isinstance(perm_value, dict):
                        frontmatter_lines.append(f"  {perm_key}:")
                        for sub_key, sub_value in perm_value.items():
                            if isinstance(sub_value, str):
                                frontmatter_lines.append(f'    "{sub_key}": "{sub_value}"')
                            else:
                                frontmatter_lines.append(f'    {sub_key}: {str(sub_value).lower()}')
                    else:
                        frontmatter_lines.append(f"  {perm_key}: {str(value).lower()}")
            elif isinstance(value, str):
                frontmatter_lines.append(f'{key}: "{value}"')
            elif isinstance(value, (int, float)):
                frontmatter_lines.append(f'{key}: {value}')
            elif isinstance(value, bool):
                frontmatter_lines.append(f'{key}: {str(value).lower()}')
            else:
                frontmatter_lines.append(f'{key}: {value}')

        frontmatter_lines.append("---")
        frontmatter_lines.append("")

        complete_content = "\n".join(frontmatter_lines) + clean_content

        with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(complete_content)

        print(f"Generated blockchain-agent subagent configuration: {output_file}")

    def _strip_frontmatter(self, content: str) -> str:
        lines = content.split('\n')

        if lines and lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    remaining_lines = lines[i+1:]
                    while remaining_lines and not remaining_lines[0].strip():
                        remaining_lines = remaining_lines[1:]
                    return '\n'.join(remaining_lines)

        return content

    def generate(self) -> bool:
        try:
            config = self.load_toml_config()

            blockchain_agent_config = self.validate_blockchain_agent_config(config)
            if blockchain_agent_config is None:
                return False

            template_content = self.validate_and_read_template(blockchain_agent_config)

            self.write_agent_config(blockchain_agent_config, template_content)

            return True

        except Exception as e:
            print(f"Error generating blockchain-agent subagent configuration: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.toml"

    generator = BlockchainAgentGenerator(config_path)
    success = generator.generate()

    if success:
        print("Blockchain-agent subagent configuration generated successfully")
    else:
        print("Blockchain-agent subagent configuration generation skipped")


if __name__ == "__main__":
    main()