# Creating Custom OpenCode Agents

This guide walks you through creating your own custom OpenCode agents, using the blockchain agent as a real-world example.

## 📋 Prerequisites

- Python 3.11+ with `tomli` and `PyYAML` packages
- Understanding of the OpenCode agent system
- Familiarity with Markdown and TOML configuration

## 🏗️ Agent Architecture Overview

OpenCode agents consist of three main components:

1. **Template Files** - Define the agent's behavior and instructions
2. **Generator Script** - Python script that processes configuration and generates final agent
3. **Configuration** - TOML configuration that defines settings and permissions

## 🚀 Step-by-Step Guide

### Step 1: Plan Your Agent

Before creating files, define:

- **Purpose**: What specific domain/task will your agent handle?
- **Scope**: Primary agent, subagent, or command agent?
- **Languages**: Which programming languages will it support?
- **Permissions**: What access does it need (read/write/bash)?

**Example: Blockchain Agent**

- Purpose: Specialized blockchain and smart contract development
- Scope: Subagent (works with other agents)
- Languages: TypeScript, Elixir
- Permissions: Full development access + blockchain tools

### Step 2: Create Template Directory Structure

Create the template directory following the naming convention:

```bash
mkdir -p control/agents/subagents/{your-agent-name}/
```

**For language-specific agents:**

```bash
# Example structure
control/agents/subagents/blockchain-agent/
├── base.md          # Core agent instructions
├── typescript.md    # TypeScript-specific guidelines
└── elixir.md       # Elixir-specific guidelines
```

**For simple agents:**

```bash
# Single file for simple agents
control/agents/subagents/your-agent.md
```

### Step 3: Create the Base Template

Create `base.md` with comprehensive agent instructions:

```markdown
# Your Agent Name (@your-agent)

Purpose:
You are a [specialized description of your agent]. Your primary responsibility is to [main function]...

## Core Responsibilities
- [Key responsibility 1]
- [Key responsibility 2]
- [etc.]

## Workflow
1. **[Step 1 Name]** - [Description]
2. **[Step 2 Name]** - [Description]
3. **[Step 3 Name]** - [Description]

## Principles
- [Key principle 1]
- [Key principle 2]
- [etc.]

## Quality Gates
- **[Gate 1]**: [Description]
- **[Gate 2]**: [Description]

## Integration Points
- **@subagents/reviewer**: [How this agent works with reviewer]
- **@subagents/tester**: [How this agent works with tester]
- **@task-manager**: [How this agent works with task-manager]

## Constraints
- [Constraint 1]
- [Constraint 2]
- [etc.]

---
```

**Key sections to include:**

- **Purpose**: Clear definition of the agent's role
- **Core Responsibilities**: What the agent does
- **Workflow**: Step-by-step process
- **Quality Gates**: Validation requirements
- **Integration Points**: How it works with other agents
- **Constraints**: What it cannot do

### Step 4: Create Language-Specific Templates

For each supported language, create specific guidelines:

```markdown
### [Language] for [Domain] Development

- [Language-specific best practice 1]
- [Language-specific best practice 2]
- [Framework recommendations]
- [Security considerations]
- [Testing patterns]
- [etc.]
```

**Example TypeScript template:**

```markdown
### TypeScript for Blockchain Development

- Use strong typing for all blockchain interactions
- Implement comprehensive error handling for blockchain transactions
- Follow Web3.js/Ethers.js best practices
- Create type-safe contract ABIs and interfaces
- Use BigNumber/ethers.BigNumber for handling token amounts
- etc.
```

### Step 5: Create the Generator Script

Create the Python generator script at `control/agents/scripts/{agent_name}.py`:

```python
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
        sys.exit(1)

# Configuration constants
BASE_TEMPLATE_PATH = "control/agents/subagents/{your-agent-name}/base.md"
LANG_TEMPLATE_PATH = "control/agents/subagents/{your-agent-name}/{lang}.md"
OUTPUT_PATH = "generated/.opencode/agent/subagent/{your-agent-name}.md"
CONFIG_KEYS = {'enabled', 'template', 'template_file', 'additional_files', 'additional_files_strategy', 'include_base_template', 'lang'}
SUPPORTED_LANGUAGES = ['typescript', 'elixir']  # Add your supported languages

class YourAgentGenerator:
    def __init__(self, config_path: str = "config.toml"):
        # [Implementation following the blockchain_agent.py pattern]
        pass

    def validate_agent_config(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Extract your agent's config from TOML
        opencode_config = config.get('opencode', {})
        agents_config = opencode_config.get('agents', {})
        subagents_config = agents_config.get('subagents', {})
        your_agent_config = subagents_config.get('{your-agent-name}', {})

        if not your_agent_config:
            print("No {your-agent-name} configuration found in TOML file")
            return None

        if not your_agent_config.get('enabled', True):
            print("{Your-agent-name} subagent is disabled")
            return None

        return your_agent_config

    # [Copy other methods from blockchain_agent.py and adapt]

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
    generator = YourAgentGenerator(config_path)
    success = generator.generate()

    if success:
        print("{Your-agent-name} subagent configuration generated successfully")
    else:
        print("{Your-agent-name} subagent configuration generation skipped")

if __name__ == "__main__":
    main()
```

### Step 6: Register Your Agent

Add your agent to the generator registry in `init.py`:

```python
class_name_map = {
    'coder_agent': 'CoderAgentGenerator',
    'blockchain_agent': 'BlockchainAgentGenerator',
    'your_agent': 'YourAgentGenerator',  # Add this line
    # ... other agents
}
```

### Step 7: Add Configuration to config.toml

Add your agent's configuration section:

```toml
[opencode.agents.subagents.your-agent-name]
enabled = true
template = "default"
lang = "typescript"  # Default language
additional_files = []
additional_files_strategy = "merge"
include_base_template = true
description = "Brief description of your agent"
mode = "subagent"
model = "anthropic/claude-sonnet-4-20250514"
temperature = 0

[opencode.agents.subagents.your-agent-name.permissions.tools]
read = true
edit = true
write = true
grep = true
glob = true
bash = true
patch = true

[opencode.agents.subagents.your-agent-name.permissions.bash_rules]
"*" = "allow"
"rm -rf *" = "ask"
"sudo *" = "ask"
# Add domain-specific tool allowances

[opencode.agents.subagents.your-agent-name.permissions.edit_rules]
"**/*.env*" = "deny"
"**/*.key" = "deny"
"**/*.secret" = "deny"
# Add domain-specific file restrictions
```

### Step 8: Test Your Agent

Run the generator to test your agent:

```bash
python3 init.py
```

Check for:

- ✅ Your agent appears in the generator list
- ✅ Configuration is generated successfully
- ✅ No errors in the output
- ✅ Generated file exists in `generated/.opencode/agent/subagent/`

### Step 9: Validate Generated Agent

Review the generated agent file:

```bash
cat generated/.opencode/agent/subagent/your-agent-name.md
```

Verify:

- **Frontmatter**: Contains correct configuration and permissions
- **Base Content**: Your base template is included
- **Language Content**: Language-specific sections are properly formatted
- **Structure**: All sections are properly formatted

## 🔧 Advanced Customization

### Custom Template Processing

You can override template processing methods:

```python
def validate_and_read_template(self, agent_config: Dict[str, Any]) -> str:
    # Custom template processing logic
    # Add domain-specific validations
    # Custom content formatting
    pass
```

### Custom Permissions

Define domain-specific permissions:

```toml
[opencode.agents.subagents.blockchain-agent.permissions.bash_rules]
"npm install *" = "allow"
"yarn install *" = "allow"
"npx hardhat *" = "allow"  # Blockchain-specific tools
"truffle *" = "allow"
"forge *" = "allow"
"cast *" = "allow"
```

### Multi-Language Support

Add language-specific validation:

```python
SUPPORTED_LANGUAGES = ['typescript', 'elixir', 'python']

def validate_language(self, lang: str) -> bool:
    if lang and lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {lang}")
    return True
```

## 📚 Best Practices

### 1. Follow Naming Conventions

- **Agent Names**: Use kebab-case (e.g., `blockchain-agent`)
- **File Names**: Match directory structure
- **Class Names**: Use PascalCase with "Generator" suffix

### 2. Comprehensive Documentation

- Include clear purpose and scope
- Document all constraints and limitations
- Provide integration guidelines
- Include handoff recommendations

### 3. Security Considerations

- Define restrictive permissions by default
- Explicitly allow only necessary tools
- Block access to sensitive files
- Use "ask" permission for potentially dangerous operations

### 4. Quality Gates

- Define clear validation criteria
- Include compilation/syntax checks
- Specify testing requirements
- Document quality standards

### 5. Integration Patterns

- Define how your agent works with others
- Provide clear handoff protocols
- Document expected inputs/outputs

## 🔍 Troubleshooting

### Common Issues

**Generator not found:**

- Check `class_name_map` in `init.py`
- Verify file name matches expected pattern
- Ensure class name follows convention

**TOML syntax errors:**

- Validate TOML syntax with online validators
- Check quotes around strings with special characters
- Ensure proper escaping of paths

**Template not found:**

- Verify file paths in generator script
- Check directory structure
- Ensure file names match constants

**Permission errors:**

- Check TOML syntax in permissions section
- Verify rule format: `"pattern" = "action"`
- Ensure proper quote escaping

## 🎯 Real-World Example

The blockchain agent created in this repository demonstrates:

- ✅ Comprehensive base template with security focus
- ✅ TypeScript and Elixir language specializations
- ✅ Domain-specific permissions (blockchain tools)
- ✅ Integration with existing agent ecosystem
- ✅ Proper error handling and validation
- ✅ Complete generator script with robust template processing

Use `control/agents/subagents/blockchain-agent/` and `control/agents/scripts/blockchain_agent.py` as reference implementations.

## 📄 Next Steps

1. **Test thoroughly** with different configurations
2. **Document** your agent's capabilities and usage
3. **Integrate** with existing workflows
4. **Share** your agent with the community
5. **Iterate** based on real-world usage

---

**Success Criteria**: Your agent should integrate seamlessly with the OpenCode ecosystem, provide clear value for its domain, and maintain the same quality standards as built-in agents.
