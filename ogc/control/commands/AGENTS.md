# OpenCode Agents

This repository defines a comprehensive suite of task-focused agents designed to streamline development workflows across multiple languages and paradigms. Each agent follows strict security-first principles with approval-based workflows and comprehensive validation processes.

## Agent Architecture

### Primary Agents (Mode: Primary)

**`codebase-agent`** - Multi-language implementation agent

- **Model**: Claude-4 Sonnet (Temperature: 0.1)
- **Purpose**: Security-first implementation across Elixir, KMP, and TypeScript
- **Workflow**: Mandatory two-phase (Plan → Approval → Implementation)
- **Security Features**: Comprehensive input validation, authentication-first design, encrypted data handling
- **Tools**: Full access (read, edit, write, grep, glob, bash, patch)
- **Specialties**:
  - Modular architecture design with SOLID principles
  - Multi-language security implementations
  - Performance optimization and testing integration
  - Comprehensive security checklists (OWASP compliance)

**`task-manager`** - Complex feature breakdown specialist

- **Model**: Claude-4 Sonnet (Temperature: 0.1)
- **Purpose**: Breaks complex features into atomic, verifiable subtasks
- **Workflow**: Two-phase planning with structured task creation
- **Output**: Creates `/tasks/subtasks/{feature}/` directories with detailed task files
- **Tools**: Limited access (no bash execution for safety)
- **Specialties**:
  - Atomic task decomposition with dependency mapping
  - Structured YAML-based task templates
  - Clear acceptance criteria and validation steps

### Subagents (Mode: Subagent)

**`reviewer`** - Security-first code review agent

- **Model**: Claude-4 Sonnet (Temperature: 0.1)
- **Purpose**: Systematic security vulnerability detection and quality assurance
- **Workflow**: Review planning → Approval → Systematic inspection
- **Tools**: Read-only access (read, grep, glob - no modification capabilities)
- **Security Focus**:
  - OWASP Top 10 vulnerability scanning
  - Input validation and sanitization review
  - Authentication/authorization verification
  - Risk classification (P0-P3 severity levels)
- **Output**: Structured review reports with actionable recommendations

**`tester`** - Test authoring and TDD specialist

- **Model**: Google Gemini 2.5 Flash (Temperature: 0.1)
- **Purpose**: Comprehensive test implementation across all supported languages
- **Tools**: Read, grep, glob, edit access
- **Specialties**: Unit testing, integration testing, TDD workflows

**`documentation`** - Multi-language documentation agent

- **Model**: Google Gemini 2.5 Flash (Temperature: 0.2)
- **Purpose**: Documentation authoring and maintenance across language ecosystems
- **Workflow**: Documentation plan → Approval → Implementation with quality gates
- **Enhanced Features**:
  - Multi-language documentation patterns and templates
  - Quality assessment framework with documentation standards
  - Cross-language documentation pattern adaptation
  - Integration with other agents for comprehensive coverage
- **Tools**: Read, grep, glob, edit access
- **Documentation Types**: API docs, architectural guides, setup instructions, cross-language examples

**`coder-agent`** - Sequential task execution specialist

- **Model**: Claude-4 Sonnet (Temperature: 0)
- **Purpose**: Executes coding subtasks in precise sequence with validation
- **Workflow**: Subtask plan → Sequential execution → Validation → Completion
- **Tools**: Full implementation access (read, edit, write, grep, glob, bash, patch)
- **Language Support**:
  - **Elixir**: OTP patterns, GenServer implementations, ExUnit testing
  - **KMP**: expect/actual patterns, coroutines, platform-specific builds
  - **TypeScript**: Type-safe implementations, modern async patterns
- **Quality Gates**: Compilation, syntax validation, test coverage, security checks
- **Enhanced Capabilities**:
  - **Dependency Management**: Stable version policies with security auditing
  - **Learning & Research**: GitHub repository analysis, official documentation research
  - **Stable Versions**: Phoenix ~> 1.7.0, Kotlin 1.9.22, TypeScript ^5.3.0
  - **Proactive Research**: Unknown implementations trigger structured learning workflow

**`codebase-pattern-analyst`** - Multi-language pattern recognition

- **Model**: Google Gemini 2.5 Flash (Temperature: 0.1)
- **Purpose**: Advanced pattern analysis across Elixir, KMP, and TypeScript
- **Enhanced Features**:
  - Language detection system with automatic pattern classification
  - Cross-language pattern comparison and adaptation examples
  - Anti-pattern detection with language-specific recommendations
  - Universal pattern categories with paradigm-specific implementations
  - Advanced search strategies for each language ecosystem
- **Tools**: Read-only analysis tools (read, grep, glob)
- **Pattern Categories**: Architecture, Security, Performance, Testing, Error Handling

## Command Agents

Specialized agents for specific development tasks:

- **`clean`**: Repository cleanup and maintenance operations
- **`commit`**: Intelligent commit message generation and staging
- **`context`**: Context analysis and workspace understanding
- **`optimize`**: Code optimization and performance improvements
- **`prompter`**: Prompt engineering and template management
- **`test`**: Test execution and validation workflows
- **`worktrees`**: Git worktree management and branching strategies

## Dependency Management

### Stable Version Policies

Each language ecosystem maintains specific stable versions with security auditing:

**Elixir Dependencies:**

- Phoenix ~> 1.7.0 (Web framework)
- Ecto ~> 3.11.0 (Database wrapper)
- Jason ~> 1.4.0 (JSON library)
- ExUnit (Built-in testing)
- StreamData (Property-based testing)
- Validation: `mix deps.audit`, `mix hex.outdated`

**Kotlin Multiplatform Dependencies:**

- Kotlin 1.9.22 (Language version)
- Coroutines 1.7.3 (Async programming)
- Ktor 2.3.7 (HTTP client/server)
- Gradle Version Catalogs for dependency management
- Validation: `./gradlew dependencyUpdates`, cross-platform testing

**TypeScript Dependencies:**

- TypeScript ^5.3.0 (Language compiler)
- Node.js ^20.10.0 (Runtime)
- Jest ^29.7.0 (Testing framework)
- @types packages for type definitions
- Validation: `npm audit`, `yarn audit`, Node.js compatibility checks

### Learning and Research Capabilities

**Automated Research Workflow:**

1. **GitHub Repository Analysis**: Test cases, examples, official documentation
2. **Web Search Integration**: Official docs, migration guides, best practices
3. **Structured Learning**: Unknown implementations trigger research and validation
4. **Knowledge Integration**: Research findings integrated into implementation workflow

**Research Sources:**

- Official language documentation and guides
- GitHub repositories with comprehensive examples
- Community best practices and migration guides
- Security advisories and dependency updates

## Multi-Language Support

### Elixir Ecosystem

- **Architecture**: OTP applications with supervision trees
- **Patterns**: GenServer, Agent, Task, Supervisor patterns
- **Security**: Process isolation, secure random generation, input validation
- **Testing**: ExUnit with property-based testing (StreamData)
- **Validation**: `mix compile`, `mix credo`, `mix dialyzer`, `mix test`

### Kotlin Multiplatform (KMP)

- **Architecture**: Shared business logic with platform-specific implementations
- **Patterns**: expect/actual declarations, sealed classes, coroutines
- **Security**: Platform-specific security APIs, certificate pinning
- **Testing**: Kotlin Test framework, platform-specific validation
- **Validation**: `./gradlew build`, platform-specific linting

### TypeScript

- **Architecture**: Modular, functional applications with type safety
- **Patterns**: Result/Either types, async/await, reactive patterns
- **Security**: XSS prevention, CSRF protection, secure cookie handling
- **Testing**: Jest/Vitest with comprehensive mocking
- **Validation**: `tsc --noEmit`, `eslint`, build verification

## Security Framework

### Universal Security Principles

- **Input Validation**: All external inputs validated for type, length, format, range
- **Authentication First**: Protected operations require authentication before execution
- **Data Protection**: Encryption in transit (TLS 1.3+) and at rest
- **Error Handling**: No sensitive information leakage in error messages
- **Dependency Security**: Regular security audits and updates

### Language-Specific Security

- **Elixir**: Process isolation, secure ETS tables, Phoenix security headers
- **KMP**: Platform-specific secure storage, network security per platform
- **TypeScript**: Content Security Policy, dependency auditing, secure API design

## Workflow Patterns

### Two-Phase Approval Workflow

1. **Phase 1: Planning**
   - Analyze requirements and scope
   - Create detailed implementation plan
   - Present structured plan for approval
   - Wait for explicit approval before proceeding

2. **Phase 2: Implementation**
   - Execute approved plan with validation at each step
   - Run language-specific quality gates
   - Provide structured progress updates
   - Complete with handoff recommendations

### Agent Integration Patterns

- **`task-manager` → `coder-agent`**: Complex features → Sequential implementation
- **`codebase-agent` → `reviewer`**: Implementation → Security review
- **`reviewer` → `tester`**: Security findings → Test validation
- **`*` → `documentation`**: Any changes → Documentation updates

## Usage Examples

```bash
# Complex feature development
opencode --agent task-manager "Implement user authentication system"
# → Creates structured subtasks
# → Handoff to coder-agent for implementation

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

### Universal Restrictions

- **Sensitive Files**: No access to `*.env*`, `*.key`, `*.secret`, `*.pem` files
- **Build Artifacts**: No modification of `node_modules/`, `_build/`, `deps/`, `build/`, `.gradle/`, `dist/`
- **Version Control**: No direct `.git/` modifications

### Agent-Specific Permissions

- **Primary Agents**: Full implementation capabilities with security restrictions
- **Reviewer**: Read-only access to prevent accidental modifications
- **Subagents**: Targeted permissions based on specific responsibilities

### Bash Command Safety

- **Denied**: `rm -rf *`, `sudo *` (destructive operations)
- **Allowed**: Language-specific tools (`mix *`, `./gradlew *`, `npm *`, `yarn *`, `git *`)
- **Ask Permission**: System-level operations (`chmod *`, `curl *`, `docker *`)

## Quality Assurance

### Validation Requirements

- **Compilation**: All code must compile without errors
- **Testing**: Relevant tests must pass before task completion
- **Security**: Security checklists must be validated
- **Documentation**: Code includes necessary annotations and comments
- **Performance**: Performance targets must be met

### Handoff Protocols

Each agent provides structured handoff recommendations to appropriate specialists:

- Security concerns → `@reviewer`
- Testing needs → `@tester`
- Documentation updates → `@documentation`
- Complex breakdowns → `@task-manager`

This agent ecosystem provides comprehensive, security-first development workflows with clear accountability, validation, and quality assurance at every step.
