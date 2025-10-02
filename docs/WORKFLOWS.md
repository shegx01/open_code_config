# OpenCode Agent Workflows

This guide covers common usage patterns and workflows with OpenCode agents.

## 🔄 Core Workflow Patterns

### Two-Phase Approval Workflow

Most agents follow a structured two-phase approach:

1. **Phase 1: Planning** - Analyze, plan, present for approval
2. **Phase 2: Implementation** - Execute with validation and quality gates

```bash
# Example: Complex feature development
opencode --agent task-manager "Implement user authentication system"
# → Phase 1: Creates structured plan
# → Wait for approval
# → Phase 2: Execute with coder-agent
```

### Agent Integration Patterns

- `task-manager` → `coder-agent`: Complex features → Sequential implementation
- `codebase-agent` → `reviewer`: Implementation → Security review
- `reviewer` → `tester`: Security findings → Test validation
- `*` → `documentation`: Any changes → Documentation updates

## 🎯 Common Use Cases

### 1. Complex Feature Development

**Workflow**: Task Manager → Coder Agent → Reviewer → Tester

```bash
# Step 1: Break down complex feature
opencode --agent task-manager "Implement OAuth2 authentication with JWT tokens"

# Step 2: Execute subtasks sequentially
opencode --agent coder-agent "Execute authentication subtasks in order"

# Step 3: Security review
opencode --agent reviewer "Review authentication implementation for vulnerabilities"

# Step 4: Test coverage
opencode --agent tester "Create comprehensive tests for authentication flow"
```

### 2. Direct Implementation with Security Focus

**Workflow**: Codebase Agent → Reviewer

```bash
# Single-phase implementation
opencode --agent codebase-agent "Add JWT authentication to API endpoints"

# Follow-up security review
opencode --agent reviewer "Security audit of JWT implementation"
```

### 3. Blockchain Development

**Workflow**: Blockchain Agent → Reviewer → Tester

```bash
# Smart contract development
opencode --agent blockchain-agent "Create ERC20 token contract with minting functionality"

# Security audit
opencode --agent reviewer "Audit smart contract for common vulnerabilities"

# Test suite
opencode --agent tester "Create comprehensive smart contract tests including edge cases"
```

### 4. Documentation Maintenance

**Workflow**: Documentation Agent

```bash
# Update project documentation
opencode --agent documentation "Update API documentation for new authentication endpoints"

# Cross-language documentation
opencode --agent documentation "Create TypeScript and Elixir examples for the new API"
```

### 5. Code Quality and Optimization

**Workflow**: Pattern Analyst → Optimizer → Reviewer

```bash
# Analyze existing patterns
opencode --agent codebase-pattern-analyst "Analyze authentication patterns across the codebase"

# Optimize performance
opencode --command optimize "Optimize database queries in authentication module"

# Verify changes
opencode --agent reviewer "Review optimization changes for potential issues"
```

## 🛠️ Command Workflows

### Repository Maintenance

```bash
# Clean up repository
opencode --command clean "Remove unused dependencies and clean build artifacts"

# Update worktrees
opencode --command worktrees "Create feature branch for authentication work"
```

### Development Support

```bash
# Generate commit messages
opencode --command commit "Generate commit message for authentication changes"

# Analyze context
opencode --command context "Analyze current codebase structure and dependencies"

# Run tests
opencode --command test "Execute all authentication-related tests"
```

## 🔀 Multi-Language Workflows

### Cross-Platform Development

```bash
# TypeScript frontend + Elixir backend
opencode --agent codebase-agent --lang typescript "Implement frontend authentication UI"
opencode --agent codebase-agent --lang elixir "Create backend authentication API"

# Pattern analysis across languages
opencode --agent codebase-pattern-analyst "Compare authentication patterns between TS and Elixir"
```

### Mobile + Web Development

```bash
# Kotlin mobile app
opencode --agent codebase-agent --lang kotlin "Implement mobile authentication flow"

# TypeScript web interface
opencode --agent codebase-agent --lang typescript "Create web authentication interface"

# Unified documentation
opencode --agent documentation "Create cross-platform authentication guide"
```

## 🚨 Security-First Workflows

### OWASP Compliance

```bash
# Implementation with security focus
opencode --agent codebase-agent "Implement secure password reset functionality following OWASP guidelines"

# Security validation
opencode --agent reviewer "OWASP Top 10 security review of password reset feature"

# Security testing
opencode --agent tester "Create security tests for password reset including attack scenarios"
```

### Vulnerability Assessment

```bash
# Comprehensive security review
opencode --agent reviewer "Full security audit of user management module"

# Fix identified issues
opencode --agent codebase-agent "Implement fixes for P0 and P1 security findings"

# Validate fixes
opencode --agent reviewer "Verify security fixes and re-assess risk levels"
```

## 📊 Quality Assurance Workflows

### Test-Driven Development

```bash
# Start with tests
opencode --agent tester "Create TDD test suite for user profile management"

# Implement features
opencode --agent coder-agent "Implement user profile features to pass TDD tests"

# Review and optimize
opencode --agent reviewer "Review TDD implementation for quality and security"
```

### Documentation-Driven Development

```bash
# Start with documentation
opencode --agent documentation "Create API specification for user management endpoints"

# Implement based on docs
opencode --agent codebase-agent "Implement user management API following the specification"

# Update docs with changes
opencode --agent documentation "Update API docs based on implementation changes"
```

## 🔄 Iterative Workflows

### Feature Development Cycle

```bash
# 1. Planning Phase
opencode --agent task-manager "Plan user notification system implementation"

# 2. Implementation Phase
opencode --agent coder-agent "Execute notification system subtasks"

# 3. Review Phase
opencode --agent reviewer "Security and quality review of notification system"

# 4. Testing Phase
opencode --agent tester "Create comprehensive tests for notification system"

# 5. Documentation Phase
opencode --agent documentation "Document notification system API and usage"

# 6. Optimization Phase (if needed)
opencode --command optimize "Optimize notification delivery performance"
```

### Bug Fix Workflow

```bash
# 1. Analyze the issue
opencode --agent codebase-pattern-analyst "Analyze authentication bug patterns"

# 2. Implement fix
opencode --agent codebase-agent "Fix authentication token expiration issue"

# 3. Security check
opencode --agent reviewer "Verify bug fix doesn't introduce security issues"

# 4. Test coverage
opencode --agent tester "Create regression tests for authentication bug"
```

## 🎛️ Advanced Workflows

### Custom Agent Integration

```bash
# Use custom blockchain agent
opencode --agent blockchain-agent "Deploy smart contract to testnet with proper gas optimization"

# Standard security review
opencode --agent reviewer "Audit smart contract deployment for security issues"

# Blockchain-specific testing
opencode --agent tester "Create integration tests for smart contract deployment"
```

### Multi-Stage Deployment

```bash
# Development stage
opencode --agent codebase-agent "Implement feature for development environment"

# Staging validation
opencode --command test "Run full test suite in staging environment"

# Security pre-production check
opencode --agent reviewer "Final security review before production deployment"

# Production readiness
opencode --agent documentation "Update production deployment documentation"
```

## 📈 Performance Workflows

### Optimization Cycle

```bash
# Baseline analysis
opencode --agent codebase-pattern-analyst "Analyze performance patterns in user module"

# Optimization implementation
opencode --command optimize "Optimize database queries and caching in user module"

# Performance validation
opencode --command test "Run performance tests to validate optimizations"

# Document improvements
opencode --agent documentation "Document performance improvements and benchmarks"
```

## 🛡️ Security Workflows

### Regular Security Assessment

```bash
# Monthly security review
opencode --agent reviewer "Comprehensive security audit of all authentication modules"

# Address findings
opencode --agent codebase-agent "Implement security improvements from monthly audit"

# Validate fixes
opencode --agent tester "Create security tests for newly implemented fixes"
```

### Dependency Security

```bash
# Analyze dependencies
opencode --command context "Analyze security status of all project dependencies"

# Update dependencies
opencode --agent coder-agent "Update dependencies with security vulnerabilities"

# Test after updates
opencode --command test "Run full test suite after dependency updates"

# Security verification
opencode --agent reviewer "Verify dependency updates don't introduce new vulnerabilities"
```

---

**Best Practice**: Always follow the appropriate workflow for your use case, ensuring security, quality, and documentation are maintained throughout the development process.
