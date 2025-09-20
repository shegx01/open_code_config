# OpenCode Agents - Enterprise Multi-Language Development Ecosystem

## 🌟 Key Features
- 🛡️ **Security-First Architecture**: OWASP compliance, comprehensive validation, authentication-first design
- 🔄 **Two-Phase Approval Workflow**: Plan → Approval → Implementation with quality gates
- 🤖 **Intelligent Agent Coordination**: Primary agents, specialized subagents, and command agents
- 📚 **Learning & Research Capabilities**: Automated dependency research and best practice integration
- ⚡ **Enterprise-Grade Quality**: Comprehensive testing, documentation, and validation frameworks

## 🚀 Quick Start

### 1. Install OpenCode CLI

```bash
# Follow official documentation
curl -sSL https://opencode.dev/install.sh | bash
```

### 2. Generate Agent Configuration

```bash
# Clone this repository
git clone git@github.com:shegx01/open_code_config.git
cd opencode-agents

# Run the initialization script
python init.py
```

This will generate all agent and command configurations in the `generated/.opencode/` directory.

**What the initialization script does:**

- ✅ Checks and installs required Python packages (PyYAML, tomli)
- 🔍 Discovers all 15 generators (8 agents + 7 commands)
- ⚙️ Generates configuration files for all agents and commands
- 📊 Provides detailed success/failure/warning feedback
- 🎯 Creates ready-to-use `.opencode/` directory structure

**Generated directory structure:**

```text
generated/.opencode/
├── agent/
│   ├── codebase-agent.md          # Primary implementation agent
│   ├── task-manager.md            # Task breakdown agent
│   └── subagent/
│       ├── coder-agent.md         # Sequential task executor
│       ├── code-pattern-analyst.md # Pattern analysis
│       ├── debugger.md            # Multi-language debugger
│       ├── documentation.md       # Documentation specialist
│       ├── reviewer.md            # Security reviewer
│       └── tester.md              # Test specialist
└── command/
    ├── clean.md                   # Repository cleanup
    ├── commit.md                  # Smart commit messages
    ├── context.md                 # Context analysis
    ├── optimizer.md               # Performance optimization
    ├── prompter.md                # Prompt engineering
    ├── test.md                    # Test execution
    └── worktrees.md               # Git worktree management
```

### 3. Customize Configuration (Optional)

Before copying to your project, you can customize the generated configuration:

```bash
# Review generated agents and commands
ls -la generated/.opencode/agent/
ls -la generated/.opencode/command/

# Edit any agent configurations as needed
# Example: Modify language settings, permissions, or templates
```

### 4. Copy Generated Configuration to Your Project

```bash
# Copy the generated configuration to your project root
cp -r generated/.opencode/ /path/to/your/project/

# Navigate to your project
cd /path/to/your/project/

# Verify agent configuration
opencode --list-agents
```

### 5. Initialize Your Project with OpenCode Agents

```bash
# In your project directory (with .opencode/ folder)
opencode init

# Verify agents are available
opencode --list-agents
```

### 6. Start Development Workflow

```bash
# Complex feature development (recommended)
opencode --agent task-manager "Implement user authentication system"
# → Creates structured subtasks → Handoff to coder-agent

# Direct implementation with security focus
opencode --agent codebase-agent "Add JWT authentication to API"
# → Two-phase workflow with security checklist

# Security review
opencode --agent reviewer "Review authentication module for vulnerabilities"
# → Systematic OWASP-based security analysis
```

## 🏗️ Agent Architecture

### 🎯 Primary Agents (Mode: Primary)

**[`codebase-agent`](.opencode/agent/codebase-agent.md)** - Multi-language implementation specialist

- **Purpose**: Security-first implementation across all supported languages
- **Workflow**: Mandatory two-phase (Plan → Approval → Implementation)
- **Security**: OWASP compliance, comprehensive validation, authentication-first design

**[`task-manager`](.opencode/agent/task-manager.md)** - Complex feature breakdown specialist

- **Purpose**: Decomposes complex features into atomic, verifiable subtasks
- **Output**: Structured task files in `/tasks/subtasks/{feature}/`
- **Workflow**: Two-phase planning with dependency mapping

### 🔧 Subagents (Mode: Subagent)

**[`reviewer`](.opencode/agent/subagents/reviewer.md)** - Security-first code review

- **Focus**: OWASP Top 10 vulnerability detection, risk classification (P0-P3)
- **Access**: Read-only (no modification capabilities)
- **Output**: Structured security reports with actionable recommendations

**[`tester`](.opencode/agent/subagents/tester.md)** - Test authoring and TDD specialist

- **Purpose**: Comprehensive test implementation across all languages
- **Specialties**: Unit testing, integration testing, TDD workflows

**[`documentation`](.opencode/agent/subagents/documentation.md)** - Multi-language documentation agent

- **Enhanced**: Multi-language patterns, quality assessment framework
- **Features**: Cross-language documentation adaptation, integration with other agents

**[`coder-agent`](.opencode/agent/subagents/coder-agent.md)** - Sequential task execution specialist

- **Purpose**: Executes coding subtasks with precise validation
- **Enhanced**: Dependency management, learning & research capabilities
- **Stable Versions**: Phoenix ~> 1.7.0, Kotlin 1.9.22, TypeScript ^5.3.0

**[`codebase-pattern-analyst`](.opencode/agent/subagents/codebase-pattern-analyst.md)** - Multi-language pattern recognition

- **Features**: Language detection, cross-language pattern comparison
- **Capabilities**: Anti-pattern detection, universal pattern categories

### ⚡ Command Agents

Specialized agents for development tasks:

- **[`clean`](.opencode/command/clean.md)**: Repository cleanup and maintenance
- **[`commit`](.opencode/command/commit.md)**: Intelligent commit message generation
- **[`context`](.opencode/command/context.md)**: Context analysis and workspace understanding
- **[`optimize`](.opencode/command/optimize.md)**: Performance improvements
- **[`test`](.opencode/command/test.md)**: Test execution and validation

## 🛡️ Security Framework

### Universal Security Principles

- **Input Validation**: All external inputs validated for type, length, format, range
- **Authentication First**: Protected operations require authentication
- **Data Protection**: Encryption in transit (TLS 1.3+) and at rest
- **Error Handling**: No sensitive information leakage
- **Dependency Security**: Regular audits and updates

### Language-Specific Security

- **Elixir**: Process isolation, secure ETS tables, Phoenix security headers
- **KMP**: Platform-specific secure storage, network security per platform
- **TypeScript**: Content Security Policy, dependency auditing, secure API design

## 🔄 Workflow Patterns

### Two-Phase Approval Workflow

1. **Phase 1: Planning** - Analyze, plan, present for approval
2. **Phase 2: Implementation** - Execute with validation and quality gates

### Agent Integration Patterns

- `task-manager` → `coder-agent`: Complex features → Sequential implementation
- `codebase-agent` → `reviewer`: Implementation → Security review
- `reviewer` → `tester`: Security findings → Test validation
- `*` → `documentation`: Any changes → Documentation updates

## 📋 Usage Examples

```bash
# Complex feature development
opencode --agent task-manager "Implement user authentication system"
# → Creates structured subtasks → Handoff to coder-agent

# Direct implementation with security focus
opencode --agent codebase-agent "Add JWT authentication to API"
# → Two-phase workflow with security checklist

# Security review
opencode --agent reviewer "Review authentication module for vulnerabilities"
# → Systematic OWASP-based security analysis

# Sequential task execution
opencode --agent coder-agent "Execute authentication subtasks in order"
# → Precise sequential implementation with validation

# Pattern analysis across languages
opencode --agent codebase-pattern-analyst "Analyze authentication patterns"
# → Cross-language pattern comparison and recommendations
```

## 🔒 Permissions & Safety

### Universal Restrictions

- **Sensitive Files**: No access to `*.env*`, `*.key`, `*.secret`, `*.pem`
- **Build Artifacts**: No modification of `node_modules/`, `_build/`, `deps/`, `build/`
- **Version Control**: No direct `.git/` modifications

### Bash Command Safety

- **Denied**: `rm -rf *`, `sudo *` (destructive operations)
- **Allowed**: Language tools (`mix *`, `./gradlew *`, `npm *`, `yarn *`, `git *`)
- **Ask Permission**: System operations (`chmod *`, `curl *`, `docker *`)

Repository guardrails live in `.opencode/permissions.json`. Scope rules per-agent inside each agent file under `permissions`.

## 🔧 Configuration

### Environment Setup (Optional)

```bash
# Copy the example environment file
cp env.example .env

# Configure Telegram notifications (optional)
# Get bot token from @BotFather on Telegram
# Get chat ID by messaging your bot and checking the API
```

### Available Commands

Command agents are available in `.opencode/command/` for specialized development tasks:

- **`clean`**: Repository cleanup and maintenance operations
- **`commit`**: Intelligent commit message generation and staging
- **`context`**: Context analysis and workspace understanding
- **`optimize`**: Code optimization and performance improvements
- **`prompter`**: Prompt engineering and template management
- **`test`**: Test execution and validation workflows
- **`worktrees`**: Git worktree management and branching strategies

### Notifications

Notifications enabled via `.opencode/plugin/notification.js`. On macOS uses `osascript` for:

- Session completion alerts
- Approval-required events
- Security findings notifications

## ✅ Quality Assurance

### Validation Requirements

- **Compilation**: All code must compile without errors
- **Testing**: Relevant tests must pass before completion
- **Security**: Security checklists must be validated
- **Documentation**: Code includes necessary annotations
- **Performance**: Performance targets must be met

### Handoff Protocols

Each agent provides structured handoff recommendations:

- Security concerns → `@reviewer`
- Testing needs → `@tester`
- Documentation updates → `@documentation`
- Complex breakdowns → `@task-manager`

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
