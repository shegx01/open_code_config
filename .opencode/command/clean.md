---
description: "Language-aware cleanup for the codebase or current task. Defaults: Elixir and Kotlin Multiplatform (KMP). Uses stack-appropriate formatters, linters, and type/static checks."
---

# Code Quality Cleanup

You are a code quality specialist. When provided with $ARGUMENTS (file paths or directories), systematically clean and optimize the code for production readiness. If no arguments provided, focus on currently open or recently modified files.

This command is language-agnostic and auto-detects the primary stack. Default priorities: Elixir and Kotlin Multiplatform (KMP).

## Your Cleanup Process

**Step 1: Analyze Target Scope**

- If $ARGUMENTS provided: Focus on specified files/directories
- If no arguments: Check git status for modified files and currently open files
- Identify language(s) by sentinel files and extensions, then select appropriate tools
  - Elixir: `mix.exs`, `lib/**/*.ex`, `test/**/*.exs`
  - KMP: `settings.gradle.kts`, `build.gradle.kts`, `**/*.kt`, `**/*.kts`, shared `commonMain`
  - Others (fallback): detect by extensions and common config files (e.g., `package.json`, `pyproject.toml`, `go.mod`)

- Discover project-defined tasks and prefer them over raw tools
  - Elixir: inspect `mix.exs` aliases for formatting/linting/type checks (e.g., `:fmt`, `:lint`, `:dialyzer`); use `mix <alias>` when present
  - KMP: list Gradle tasks/plugins (e.g., `ktlintFormat`, `detekt`, `spotlessApply`); prefer Gradle tasks over direct CLI when available
  - Generic: prefer configured scripts (e.g., `make`, `npm run`, `poetry run`) before invoking raw binaries

**Step 2: Execute Cleanup Pipeline**
Perform these actions in order:

1. **Remove Debug Code**
   - Elixir: remove `IO.inspect/1,2`, `IO.puts`, excessive `Logger.debug` (retain necessary prod logs)
   - Kotlin: remove `println`, `printStackTrace`, `TODO("...")`, `FIXME` markers where inappropriate
   - Generic: strip `console.log`, `debugger`, temporary scaffolds, and commented-out code blocks
   - Remove development-only imports/dependencies

2. **Format Code Structure**
   - Elixir: use `mix` alias if defined (e.g., `mix fmt`), otherwise `mix format`
   - Kotlin: prefer Gradle task (e.g., `./gradlew ktlintFormat` or `spotlessApply`); fallback to `ktlint -F`
   - Generic: prefer project script (e.g., `make format`, `npm run format`) before raw formatter; ensure indentation, spacing, quotes, trailing commas as per conventions

3. **Optimize Imports**
   - Kotlin: organize imports and remove unused (via IDE inspections, `ktlint` rules, or `detekt` suggestions)
   - Elixir: N/A (imports are alias/use/import statements; clean unused via linter suggestions)
   - Generic: sort/group imports; remove unused; prefer absolute paths if configured

4. **Fix Linting Issues**
   - Elixir: prefer lint alias (e.g., `mix lint`) if present; otherwise `mix credo --strict --all` (apply auto-fixes where possible)
   - Kotlin: prefer Gradle `detekt` task; enforce `ktlint` via Gradle if configured; otherwise run `ktlint` directly (apply corrections)
   - Generic: run project linter scripts first (e.g., `make lint`, `npm run lint`), apply auto-fixes, summarize manual fixes

5. **Type Safety Validation**
   - Elixir: prefer alias for Dialyzer (e.g., `mix dialyzer` via alias like `mix types`); otherwise run `mix dialyzer` if configured; fix obvious type specs; add/refine `@spec`
   - Kotlin: compile with Gradle (`./gradlew build` or stricter CI task); fix warnings/errors; enable `-Werror` if policy requires
   - Generic: run type/static analyzers via project scripts when available; otherwise call tools directly

6. **Comment Optimization**
   - Remove redundant or obvious comments
   - Improve unclear comments
   - Ensure docstring/docs completeness for public APIs (e.g., Elixir moduledoc/doc, KDoc/Javadoc)

**Step 3: Present Cleanup Report**

## 📋 Cleanup Results

### 🎯 Files Processed

- [List of files that were cleaned]

### 🔧 Actions Taken

- **Debug Code Removed**: [Number of console.logs, debuggers removed]
- **Formatting Applied**: [Files formatted]
- **Imports Optimized**: [Unused imports removed, sorting applied]
- **Linting Issues Fixed**: [Auto-fixed issues count]
- **Type/Static Issues Resolved**: [Dialyzer/Kotlin compiler/type-checker issues fixed]
- **Comments Improved**: [Redundant comments removed, unclear ones improved]

### 🚨 Manual Actions Needed

- [List any issues that require manual intervention]

### ✅ Quality Improvements

- [Summary of overall code quality improvements made]

## Quality Standards Applied

- **Production Ready**: Remove all debugging and development artifacts
- **Consistent Style**: Apply project formatting standards
- **Type Safety**: Ensure strong typing where applicable
- **Clean Imports**: Optimize dependency management
- **Clear Documentation**: Improve code readability through better comments

## Language Tooling Matrix (Defaults first)

- **Elixir (default)**
  - Format: prefer alias (e.g., `mix fmt`); fallback `mix format`
  - Lint: prefer alias (e.g., `mix lint`); fallback `mix credo --strict --all`
  - Types: prefer alias (e.g., `mix types`); fallback `mix dialyzer` (if configured)
  - Debug cleanup: remove `IO.inspect`, excessive `Logger.debug`

- **Kotlin Multiplatform (default)**
  - Format: prefer Gradle task (`ktlintFormat` or `spotlessApply`); fallback `ktlint -F`
  - Lint: prefer Gradle `detekt` task; optionally enforce ktlint via plugin
  - Build/types: `./gradlew build` (consider `-Werror`), fix compiler warnings/errors
  - Debug cleanup: remove `println`, `printStackTrace`, `TODO()`

- **Other common stacks (examples)**
  - JS/TS: prefer `npm run`/`pnpm`/`yarn` scripts (format/lint/typecheck); fallbacks: Prettier, ESLint, `tsc --noEmit`
  - Python: prefer `make`/`poetry`/`tox` scripts; fallbacks: `ruff --fix`, `black`, `mypy`
  - Go: prefer `make` targets; fallbacks: `gofmt -s -w`, `go vet`, `staticcheck`
