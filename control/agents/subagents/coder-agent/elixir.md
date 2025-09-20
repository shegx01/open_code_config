### Elixir

- Use OTP patterns (GenServer, Supervisor, Agent) for state management
- Follow Elixir naming conventions (snake_case for functions, PascalCase for modules)
- Implement must be fault-tolerant and follow OTP principles
- Use `mix` for project management, dependencies, and testing
- Write comprehensive ExUnit tests, follow coverage guidelines in `mix.exs`
- Include proper `@doc` and `@spec` annotations but exclude for private functions
- Handle errors with `{:ok, result}` and `{:error, reason}` tuples
- Avoid using `try`/`catch`/`rescue` macros
- Leverage pattern matching and guard clauses
- When available, always use `with` but not for single line expressions
- Avoid excessive comments in the code base
