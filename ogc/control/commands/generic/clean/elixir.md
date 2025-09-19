**Step 1: Analyze Target Scope**

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

## Language Tooling Matrix (Defaults first)

- **Elixir (default)**
  - Format: prefer alias (e.g., `mix format`)
  - Lint: prefer alias (e.g., `mix lint`); fallback `mix credo --strict --all`
  - Types: prefer alias (e.g., `mix types`); fallback `mix dialyzer` (if configured)
  - Debug cleanup: remove `IO.inspect`, excessive `Logger.debug`
