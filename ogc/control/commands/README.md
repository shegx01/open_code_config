# OpenCode Agents - Multi-Language Development Ecosystem

A comprehensive suite of security-first agents designed for enterprise-grade development across Elixir, Kotlin Multiplatform (KMP), and TypeScript ecosystems.

## Quick Start

1. **Install OpenCode CLI** (see [official documentation](https://opencode.dev))
2. **Configure defaults** via `.opencode/config.json`
3. **Review agent roles** in `AGENTS.md`
4. **Start with task breakdown**: `opencode --agent task-manager "Your feature description"`

## Agent Architecture

### 🎯 Primary Agents (Mode: Primary)

**`codebase-agent`** - Multi-language implementation specialist

- **Purpose**: Security-first implementation across all supported languages
- **Workflow**: Mandatory two-phase (Plan → Approval → Implementation)
- **Security**: OWASP compliance, comprehensive validation, authentication-first design
- **Languages**: Elixir (OTP), KMP (expect/actual), TypeScript (type-safe)

**`task-manager`** - Complex feature breakdown specialist

- **Purpose**: Decomposes complex features into atomic, verifiable subtasks
- **Output**: Structured task files in `/tasks/subtasks/{feature}/`
- **Workflow**: Two-phase planning with dependency mapping

### 🔧 Subagents (Mode: Subagent)

**`reviewer`** - Security-first code review

- **Focus**: OWASP Top 10 vulnerability detection, risk classification (P0-P3)
- **Access**: Read-only (no modification capabilities)
- **Output**: Structured security reports with actionable recommendations

**`tester`** - Test authoring and TDD specialist

- **Purpose**: Comprehensive test implementation across all languages
- **Specialties**: Unit testing, integration testing, TDD workflows

**`documentation`** - Multi-language documentation agent

- **Enhanced**: Multi-language patterns, quality assessment framework
- **Features**: Cross-language documentation adaptation, integration with other agents

**`coder-agent`** - Sequential task execution specialist

- **Purpose**: Executes coding subtasks with precise validation
- **Enhanced**: Dependency management, learning & research capabilities
- **Stable Versions**: Phoenix ~> 1.7.0, Kotlin 1.9.22, TypeScript ^5.3.0

**`codebase-pattern-analyst`** - Multi-language pattern recognition

- **Features**: Language detection, cross-language pattern comparison
- **Capabilities**: Anti-pattern detection, universal pattern categories

### ⚡ Command Agents

Specialized agents for development tasks:

- **`clean`**: Repository cleanup and maintenance
- **`commit`**: Intelligent commit message generation
- **`context`**: Context analysis and workspace understanding
- **`optimize`**: Performance improvements
- **`test`**: Test execution and validation

## Multi-Language Support

### 🟣 Elixir Ecosystem

- **Architecture**: OTP applications with supervision trees
- **Patterns**: GenServer, Agent, Task, Supervisor
- **Security**: Process isolation, secure random generation
- **Testing**: ExUnit with property-based testing (StreamData)
- **Dependencies**: Phoenix ~> 1.7.0, Ecto ~> 3.11.0, Jason ~> 1.4.0

### 🟠 Kotlin Multiplatform (KMP)

- **Architecture**: Shared business logic with platform-specific implementations
- **Patterns**: expect/actual declarations, sealed classes, coroutines
- **Security**: Platform-specific security APIs, certificate pinning
- **Testing**: Kotlin Test framework with platform validation
- **Dependencies**: Kotlin 1.9.22, Coroutines 1.7.3, Ktor 2.3.7

### 🔵 TypeScript

- **Architecture**: Modular, functional applications with type safety
- **Patterns**: Result/Either types, async/await, reactive patterns
- **Security**: XSS prevention, CSRF protection, secure cookies
- **Testing**: Jest/Vitest with comprehensive mocking
- **Dependencies**: TypeScript ^5.3.0, Node.js ^20.10.0, Jest ^29.7.0

## Security Framework

### 🛡️ Universal Security Principles

- **Input Validation**: All external inputs validated for type, length, format, range
- **Authentication First**: Protected operations require authentication
- **Data Protection**: Encryption in transit (TLS 1.3+) and at rest
- **Error Handling**: No sensitive information leakage
- **Dependency Security**: Regular audits and updates

### 🔒 Language-Specific Security

- **Elixir**: Process isolation, secure ETS tables, Phoenix security headers
- **KMP**: Platform-specific secure storage, network security per platform
- **TypeScript**: Content Security Policy, dependency auditing, secure API design

## Workflow Patterns

### 📋 Two-Phase Approval Workflow

1. **Phase 1: Planning** - Analyze, plan, present for approval
2. **Phase 2: Implementation** - Execute with validation and quality gates

### 🔄 Agent Integration Patterns

- `task-manager` → `coder-agent`: Complex features → Sequential implementation
- `codebase-agent` → `reviewer`: Implementation → Security review
- `reviewer` → `tester`: Security findings → Test validation
- `*` → `documentation`: Any changes → Documentation updates

## Usage Examples

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
```

## Permissions & Safety

### 🚫 Universal Restrictions

- **Sensitive Files**: No access to `*.env*`, `*.key`, `*.secret`, `*.pem`
- **Build Artifacts**: No modification of `node_modules/`, `_build/`, `deps/`, `build/`
- **Version Control**: No direct `.git/` modifications

### ⚠️ Bash Command Safety

- **Denied**: `rm -rf *`, `sudo *` (destructive operations)
- **Allowed**: Language tools (`mix *`, `./gradlew *`, `npm *`, `yarn *`, `git *`)
- **Ask Permission**: System operations (`chmod *`, `curl *`, `docker *`)

Repository guardrails live in `.opencode/permissions.json`. Scope rules per-agent inside each agent file under `permissions`.

## Commands & Plugins

### Custom Commands

Custom commands live in `.opencode/commands/`. Examples:

- `/feature-setup`: Initialize new feature structure
- `/security-check`: Run comprehensive security validation
- `/cross-lang-pattern`: Analyze patterns across languages

### Notifications

Notifications enabled via `.opencode/plugin/notification.js`. On macOS uses `osascript` for:

- Session completion alerts
- Approval-required events
- Security findings notifications

## Quality Assurance

### ✅ Validation Requirements

- **Compilation**: All code must compile without errors
- **Testing**: Relevant tests must pass before completion
- **Security**: Security checklists must be validated
- **Documentation**: Code includes necessary annotations
- **Performance**: Performance targets must be met

### 🤝 Handoff Protocols

Each agent provides structured handoff recommendations:

- Security concerns → `@reviewer`
- Testing needs → `@tester`
- Documentation updates → `@documentation`
- Complex breakdowns → `@task-manager`

---

**Assessment**: This agent ecosystem provides enterprise-grade, security-first development workflows with comprehensive multi-language support, clear accountability, and quality assurance at every step.
