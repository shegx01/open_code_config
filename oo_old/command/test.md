---
description: "Language-aware comprehensive testing pipeline. Defaults: Elixir and Kotlin Multiplatform (KMP). Covers unit, integration, property-based, and end-to-end testing."
---

# Comprehensive Testing Pipeline

You are a testing specialist focused on comprehensive test coverage and quality assurance. When provided with $ARGUMENTS (test types or file paths), execute targeted testing. If no arguments provided, run the complete testing pipeline for the detected project stack.

This command is language-agnostic with default priorities: Elixir and Kotlin Multiplatform (KMP).

## Your Testing Process

**Step 1: Detect Project Stack and Test Scope**

- If $ARGUMENTS provided: Focus on specified test types or files
- If no arguments: Auto-detect project type and run comprehensive pipeline
- Identify testing frameworks by sentinel files:
  - Elixir: `mix.exs`, `test/` directory, ExUnit patterns
  - KMP: `build.gradle.kts`, `src/*/test/`, JUnit/Kotest patterns
  - Others: `package.json` (Jest/Vitest), `pyproject.toml` (pytest), `go.mod` (Go test)

**Step 2: Execute Testing Pipeline**
Perform these phases in order:

### Phase 1: Static Analysis & Type Checking

**Elixir:**

- Run `mix compile --warnings-as-errors` for compilation checks
- Execute `mix dialyzer` if configured (type analysis)
- Run `mix credo --strict` for code quality

**KMP:**

- Execute `./gradlew compileKotlin` for compilation
- Run `./gradlew detekt` for static analysis
- Execute `./gradlew ktlintCheck` for style validation

**Generic:**

- TypeScript: `tsc --noEmit` or `pnpm type:check`
- Python: `mypy .` or `pyright`
- Go: `go vet ./...`

### Phase 2: Unit Testing

**Elixir:**

- Run `mix test` for standard unit tests
- Execute `mix test --cover` for coverage analysis
- Run `mix test.watch` if available for continuous testing

**KMP:**

- Execute `./gradlew test` for JVM tests
- Run `./gradlew testDebugUnitTest` for Android tests
- Execute `./gradlew iosX64Test` for iOS tests (if configured)

**Generic:**

- JavaScript: `npm test` or `pnpm test`
- Python: `pytest` or `python -m pytest`
- Go: `go test ./...`

### Phase 3: Integration Testing

**Elixir:**

- Run `mix test --only integration` if tagged
- Execute database tests with `MIX_ENV=test mix ecto.reset`
- Test Phoenix endpoints with `mix test test/web/`

**KMP:**

- Execute `./gradlew integrationTest` if configured
- Run `./gradlew connectedAndroidTest` for Android integration
- Test shared module integration across platforms

### Phase 4: Property-Based & Advanced Testing

**Elixir:**

- Run StreamData property tests: `mix test --only property`
- Execute performance tests if configured
- Run `mix test --only slow` for long-running tests

**KMP:**

- Execute Kotest property tests if configured
- Run performance benchmarks with JMH
- Test memory usage and leak detection

### Phase 5: End-to-End Testing

**Elixir (Phoenix):**

- Run `mix test --only e2e` for browser tests
- Execute API integration tests
- Test WebSocket connections if applicable

**KMP:**

- Run UI tests: `./gradlew connectedAndroidTest`
- Execute iOS UI tests if configured
- Test cross-platform data synchronization

**Step 3: Coverage Analysis & Reporting**

**Elixir:**

- Generate coverage report: `mix test --cover`
- Export coverage: `mix coveralls.html` if configured
- Check coverage thresholds

**KMP:**

- Generate JaCoCo reports: `./gradlew jacocoTestReport`
- Combine platform coverage if configured
- Validate coverage requirements

**Step 4: Present Testing Report**

## 📋 Testing Pipeline Results

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

## Testing Framework Matrix

### **Elixir (Default)**

- **Unit**: ExUnit with `mix test`
- **Property**: StreamData for property-based testing
- **Integration**: Phoenix.ConnTest for web, Ecto for database
- **Coverage**: `mix test --cover` or ExCoveralls
- **Mocking**: Mox for concurrent-safe mocks
- **Performance**: Benchee for benchmarking

### **Kotlin Multiplatform (Default)**

- **Unit**: JUnit 5 / Kotest for multiplatform
- **Integration**: TestContainers, Ktor Test Engine
- **UI**: Espresso (Android), XCUITest (iOS)
- **Coverage**: JaCoCo for JVM, Kover for multiplatform
- **Mocking**: MockK for Kotlin-specific mocking
- **Property**: Kotest property testing

### **Other Stacks (Examples)**

- **JavaScript/TypeScript**: Jest, Vitest, Playwright for E2E
- **Python**: pytest, hypothesis for property testing
- **Go**: built-in testing, testify, GoConvey
- **Rust**: built-in testing, proptest for property testing

## Testing Best Practices Applied

- **Fast Feedback**: Unit tests run first for quick validation
- **Comprehensive Coverage**: Multi-layer testing strategy
- **Property-Based**: Generate edge cases automatically
- **Cross-Platform**: Validate KMP shared code on all targets
- **Continuous**: Support for watch mode and CI integration
- **Measurable**: Coverage tracking and quality metrics
