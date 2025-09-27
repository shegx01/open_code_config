# OpenCode Agents - Custom Agent Configuration

A comprehensive, security-first agent configuration system for OpenCode with multi-language support and specialized domain expertise.

## 🚀 Quick Start

### 1. Install OpenCode CLI

```bash
# Follow official documentation at https://opencode.ai
curl -sSL https://opencode.dev/install.sh | bash

# Or via package managers
brew install sst/tap/opencode        # macOS
npm install -g opencode-ai          # Node.js
bun install -g opencode-ai          # Bun
```

### 2. Generate Agent Configuration

```bash
# Clone this repository
git clone git@github.com:shegx01/open_code_config.git
cd open_code_config

# Run the initialization script
./setup.sh
```

**What happens:**

- ✅ Installs required packages (PyYAML, tomli)
- 🔍 Discovers 17+ generators (9 agents + 8 commands)
- ⚙️ Generates ready-to-use `.opencode/` configuration
- 🎯 Includes specialized agents (blockchain, security, testing, etc.)

### 3. Copy to Your Project

```bash
# Copy generated configuration
cp -r generated/.opencode/ /path/to/your/project/

# Initialize in your project
cd /path/to/your/project/
opencode init
opencode --list-agents
```

### 4. Start Using Agents

```bash
# Complex feature development
opencode --agent task-manager "Implement user authentication system"

# Blockchain development
opencode --agent blockchain-agent "Create ERC20 token contract"

# Security review
opencode --agent reviewer "Review code for vulnerabilities"
```

## 🏗️ Available Agents

### 🎯 Primary Agents

- **`codebase-agent`** - Security-first implementation with two-phase workflow
- **`task-manager`** - Complex feature breakdown into atomic subtasks

### 🔧 Specialized Subagents

- **`blockchain-agent`** - Smart contract and Web3 development specialist
- **`coder-agent`** - Sequential task execution with validation
- **`reviewer`** - OWASP-compliant security code review
- **`tester`** - Comprehensive test authoring and TDD
- **`documentation`** - Multi-language documentation specialist
- **`debugger`** - Advanced debugging across languages
- **`code-pattern-analyst`** - Pattern recognition and analysis

### ⚡ Command Agents

- **`clean`** - Repository cleanup and maintenance
- **`commit`** - Intelligent commit message generation
- **`context`** - Workspace analysis and understanding
- **`optimize`** - Performance improvements
- **`test`** - Test execution and validation
- **`worktrees`** - Git worktree management

## 📋 Usage Examples

```bash
# Complex feature development
opencode --agent task-manager "Implement user authentication system"

# Blockchain smart contract development
opencode --agent blockchain-agent "Create ERC20 token with minting functionality"

# Direct implementation with security focus
opencode --agent codebase-agent "Add JWT authentication to API"

# Security review
opencode --agent reviewer "Review authentication module for vulnerabilities"

# Documentation updates
opencode --agent documentation "Update API documentation for new endpoints"

# Repository cleanup
opencode --command clean "Remove unused dependencies and artifacts"
```

## 🔒 Security & Permissions

All agents follow strict security guidelines:

- 🚫 **Blocked**: Access to sensitive files (`*.env`, `*.key`, `*.secret`)
- ⚠️ **Restricted**: Destructive operations (`rm -rf`, `sudo`)
- ✅ **Allowed**: Language-specific development tools
- ❓ **Ask Permission**: System-level operations

**See**: [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) for detailed security settings.

## 📚 Documentation

- **[Agent Details](.opencode/AGENTS.md)**: Comprehensive agent specifications
- **[Configuration Guide](.opencode/README.md)**: Detailed setup and usage
- **[Plugin Documentation](.opencode/plugin/README.md)**: Plugin system and notifications

## 🤝 Contributing

1. Follow established multi-language conventions and security standards
2. Write comprehensive tests for all supported languages
3. Update documentation for any changes across all language ecosystems
4. Ensure OWASP security best practices are followed
5. Validate changes across Elixir, KMP, and TypeScript environments

## 📄 License

This project is licensed under the MIT License.

---

**Assessment**: This agent ecosystem provides enterprise-grade, security-first development workflows with comprehensive multi-language support, clear accountability, and quality assurance at every step.
