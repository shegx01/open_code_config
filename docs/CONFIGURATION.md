# OpenCode Agents Configuration Guide

This guide covers the configuration and setup of OpenCode agents.

## 🔧 Configuration Files

### config.toml Structure

The `config.toml` file defines all agent and command configurations:

```toml
[gh.workflow]
env_key = "ANTHROPIC_API_KEY"
model = "anthropic/claude-sonnet-4-20250514"

[opencode.agents]
# Primary agents configuration

[opencode.agents.subagents]
# Subagents configuration

[opencode.commands]
# Command agents configuration
```

### Agent Configuration Format

Each agent requires:

```toml
[opencode.agents.subagents.agent-name]
enabled = true
template = "default"
lang = "typescript"
additional_files = []
additional_files_strategy = "merge"
include_base_template = true
description = "Agent description"
mode = "subagent"
model = "anthropic/claude-sonnet-4-20250514"
temperature = 0

[opencode.agents.subagents.agent-name.permissions.tools]
read = true
edit = true
write = true
grep = true
glob = true
bash = true
patch = true

[opencode.agents.subagents.agent-name.permissions.bash_rules]
"*" = "allow"
"rm -rf *" = "ask"
"sudo *" = "ask"

[opencode.agents.subagents.agent-name.permissions.edit_rules]
"**/*.env*" = "deny"
"**/*.key" = "deny"
"**/*.secret" = "deny"
```

## 🛡️ Security & Permissions

### Permission Levels

- **allow**: Operation is permitted
- **ask**: Request user confirmation
- **deny**: Operation is blocked

### Universal Security Restrictions

All agents block access to:
- `**/*.env*` - Environment files
- `**/*.key` - Private key files
- `**/*.secret` - Secret files
- `**/*.pem` - Certificate files

### Bash Command Safety

- **Blocked**: `rm -rf *`, `sudo *` (destructive operations)
- **Allowed**: Language tools (`mix *`, `npm *`, `yarn *`, `git *`)
- **Confirmation Required**: System operations (`chmod *`, `curl *`, `docker *`)

## 🏗️ Directory Structure

```
.opencode/
├── agent/
│   ├── codebase-agent.md
│   ├── task-manager.md
│   └── subagent/
│       ├── blockchain-agent.md
│       ├── coder-agent.md
│       ├── debugger.md
│       ├── documentation.md
│       ├── reviewer.md
│       └── tester.md
├── command/
│   ├── clean.md
│   ├── commit.md
│   ├── context.md
│   ├── optimizer.md
│   ├── test.md
│   └── worktrees.md
└── plugin/
    └── notification.js
```

## ⚙️ Language Support

### Supported Languages

- **Elixir**: Phoenix, OTP, Mix
- **TypeScript**: Node.js, React, Express
- **Kotlin Multiplatform**: Android, JVM, Native

### Language-Specific Settings

```toml
# Elixir focus
lang = "elixir"

# TypeScript focus  
lang = "typescript"

# Kotlin Multiplatform focus
lang = "kotlin"
```

## 🔄 Template System

### Template Types

- **default**: Uses base + language templates
- **custom**: Uses custom template file

### Template Strategy

- **merge**: Combine base, language, and additional files
- **replace**: Use only additional files

## 📱 Notifications

Configure notifications in `.opencode/plugin/notification.js`:

```javascript
// macOS notification support
function notify(message, title = "OpenCode") {
    // osascript implementation
}
```

## 🧪 Testing Configuration

Validate your configuration:

```bash
# Test generation
python3 init.py

# Verify agents
opencode --list-agents

# Check specific agent
cat generated/.opencode/agent/subagent/your-agent.md
```

## 🔍 Troubleshooting

### Common Configuration Issues

1. **TOML Syntax Errors**: Use online TOML validators
2. **Path Issues**: Check file paths and directory structure
3. **Permission Conflicts**: Verify permission rule format
4. **Missing Templates**: Ensure all referenced files exist

### Debug Commands

```bash
# Check TOML validity
python3 -c "import tomli; tomli.loads(open('config.toml', 'rb').read())"

# Verify directory structure
find control/agents -name "*.md" -type f

# Test specific generator
python3 control/agents/scripts/your_agent.py
```