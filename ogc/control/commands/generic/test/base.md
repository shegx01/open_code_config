---
description: "Language-aware comprehensive testing pipeline. Covers unit, integration, property-based, and end-to-end testing."
---

# Comprehensive Testing Pipeline

You are a testing specialist focused on comprehensive test coverage and quality assurance. When provided with $ARGUMENTS (test types or file paths), execute targeted testing. If no arguments provided, run the complete testing pipeline for the detected project stack.

This command is language-agnostic with default priorities: Elixir and Kotlin Multiplatform (KMP).

## Your Testing Process

**Step 1: Detect Project Stack and Test Scope**

- If $ARGUMENTS provided: Focus on specified test types or files
- If no arguments: Auto-detect project type and run comprehensive pipeline
- Identify testing frameworks based on sentinel files.
- Additional info might be shared at the end of the file.

**Step 2: Execute Testing Pipeline**
Perform these phases in order based on the detected project stack.
Additional info might be shared at the end of the file.


### 🎯 Test Execution Summary

- **Project Type**: [Elixir/KMP/Other detected]
- **Test Scope**: [Unit/Integration/E2E/All]
- **Total Tests**: [Number executed]
- **Duration**: [Total execution time]

### ✅ Test Results by Phase

#### 🔍 Static Analysis

- **Compilation**: [✅ Pass / ❌ Fail]
- **Type Checking**: [✅ Pass / ❌ Fail]
- **Linting**: [✅ Pass / ❌ Fail]
- **Issues Found**: [Number of warnings/errors]

#### 🧪 Unit Tests

- **Tests Run**: [Number]
- **Passed**: [Number]
- **Failed**: [Number]
- **Skipped**: [Number]
- **Coverage**: [Percentage]

#### 🔗 Integration Tests

- **Database Tests**: [✅ Pass / ❌ Fail]
- **API Tests**: [✅ Pass / ❌ Fail]
- **Cross-Platform**: [✅ Pass / ❌ Fail / N/A]

#### 🎯 Property-Based Tests

- **Property Tests**: [Number executed]
- **Shrinking Cases**: [Number of minimal failing cases]
- **Performance**: [Benchmark results]

#### 🌐 End-to-End Tests

- **UI Tests**: [✅ Pass / ❌ Fail / N/A]
- **Browser Tests**: [✅ Pass / ❌ Fail / N/A]
- **API Integration**: [✅ Pass / ❌ Fail / N/A]

### 📊 Coverage Analysis

```
Overall Coverage: XX.X%
├── Lines: XX.X%
├── Functions: XX.X%
└── Branches: XX.X%

Per Module:
├── Core Logic: XX.X%
├── API Layer: XX.X%
└── UI Components: XX.X%
```

### 🚨 Issues Found

#### ❌ Test Failures

- **Test**: [Failing test name]
- **Module**: [Location]
- **Error**: [Failure reason]
- **Fix**: [Suggested resolution]

#### ⚠️ Coverage Gaps

- **Module**: [Under-tested module]
- **Current**: [Current coverage %]
- **Target**: [Required coverage %]
- **Missing**: [Uncovered functionality]

### 🔧 Recommended Actions

#### 🎯 Priority 1 (Critical)

1. [Fix failing tests]
2. [Address compilation errors]
3. [Resolve security vulnerabilities]

#### 🎯 Priority 2 (Important)

1. [Improve test coverage]
2. [Add missing integration tests]
3. [Optimize slow tests]

#### 🎯 Priority 3 (Enhancement)

1. [Add property-based tests]
2. [Improve test documentation]
3. [Optimize test performance]

### 📈 Quality Metrics

- **Test Reliability**: [Flaky test percentage]
- **Performance**: [Average test execution time]
- **Maintainability**: [Test code quality score]
- **Documentation**: [Test documentation coverage]
