# Elixir debugging tools

```yaml
language_support:
  elixir:
    file_patterns: ["*.ex", "*.exs", "mix.exs", "config/*.exs"]
    debugging_tools: ["iex", "observer_cli", "recon", "sys_module", "telemetry"]
    build_commands: ["mix compile", "mix test"]
    safety_level: "production_safe"
```

## Elixir Debugging Techniques

### Core Tools & Commands

**Basic Debugging:**

```elixir
# Pipeline inspection
data |> IO.inspect(label: "checkpoint") |> process()

# Enhanced debugging (Elixir 1.14+)
result |> dbg()

# Interactive debugging
iex --dbg pry -S mix
```

**OTP Process Debugging:**

```elixir
# GenServer inspection
:sys.get_state(pid)
:sys.get_status(pid)
:sys.trace(pid, true)
:sys.no_debug(pid)  # ALWAYS cleanup
```

**Production-Safe Tools:**

```elixir
# System monitoring
:observer_cli.start()

# Safe tracing with limits
:recon_trace.calls({Module, :function, :return_trace}, 10)
:recon.proc_count(:memory, 5)
```

### Elixir Safety Guidelines

**Production Debugging Rules:**

- Always use `recon` and `observer_cli` for production
- Set explicit limits on all tracing operations
- Clean up debugging after investigation
- Monitor system resources during debugging
- Have rollback plan ready

**Never Do:**

```elixir
# DANGEROUS - unlimited tracing
:erlang.trace(:all, true, [:all])

# DANGEROUS - unlimited process inspection
Process.list() |> Enum.map(&:erlang.process_info/1)
```
