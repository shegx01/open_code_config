# GitHub Workflow Generator for OpenCode

This directory contains tools for generating GitHub workflows for [OpenCode](https://opencode.ai), an AI-powered coding assistant that works directly in GitHub issues and pull requests.

## Overview

The `generate_workflow.py` script automatically generates GitHub workflow files for OpenCode by reading configuration from properties files and substituting values into a standardized workflow template.

## Quick Start

1. **Configure your settings** in `ogc/config.toml`:

   ```toml
   [gh.workflow]
   env_key = "ANTHROPIC_API_KEY"
   model = "anthropic/claude-sonnet-4-20250514"
   ```

2. **Generate the workflow**:

   ```bash
   python ogc/github/generate_workflow.py --config ogc/config.toml --verbose
   ```

3. **Copy the generated workflow** from `ogc/github/generated/.github/workflows/opencode.yml` to your repository's `.github/workflows/` directory.

## Configuration File Format

The configuration file uses TOML format with structured sections:

```toml
# OpenCode Workflow Configuration
[gh.workflow]
env_key = "ANTHROPIC_API_KEY"  # The environment variable name for API key
model = "anthropic/claude-sonnet-4-20250514"  # AI model to use

# You can add other sections for different tools
[commands]
# Additional commands configuration can go here
```

### Supported Configuration Keys

| Key | Description | Default Value | Required |
|-----|-------------|---------------|----------|
| `gh.workflow.env_key` | Environment variable name for the API key | `ANTHROPIC_API_KEY` | No |
| `gh.workflow.model` | AI model in `provider/model` format | `anthropic/claude-sonnet-4-20250514` | No |

### Supported AI Models

The script supports any model format accepted by OpenCode:

- **Anthropic**: `anthropic/claude-sonnet-4-20250514`, `anthropic/claude-haiku-3-20240307`
- **OpenAI**: `openai/gpt-4`, `openai/gpt-3.5-turbo`
- **Other providers**: Follow the `provider/model` format

## Script Usage

### Basic Usage

```bash
# Generate workflow with default settings
python ogc/github/generate_workflow.py

# Use specific configuration file
python ogc/github/generate_workflow.py --config ogc/config.toml

# Show configuration summary
python ogc/github/generate_workflow.py --config ogc/config.toml --verbose
```

### Advanced Usage

```bash
# Custom output location
python ogc/generate_workflow.py \
  --config ogc/config.toml \
  --output custom/.github/workflows/opencode.yml

# Print to stdout (useful for piping or inspection)
python ogc/generate_workflow.py \
  --config ogc/config.toml \
  --output - \
  --verbose

# Generate for different environments
python ogc/generate_workflow.py \
  --config environments/production.properties \
  --output production/.github/workflows/opencode.yml
```

### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--config` | `-c` | Path to configuration file | `config.toml` |
| `--output` | `-o` | Output file path | `ogc/generated/.github/workflows/opencode.yml` |
| `--verbose` | `-v` | Show configuration summary | `false` |
| `--help` | `-h` | Show help message | - |

## Generated Workflow Structure

The generated workflow includes:

- **Trigger**: Responds to issue comments containing `/oc` or `/opencode`
- **Permissions**: Proper GitHub Actions permissions for repository operations
- **Security**: Only allows repository owners and members to trigger
- **Environment**: Configurable API key and model settings

### Example Generated Workflow

```yaml
name: opencode

on:
  issue_comment:
    types: [created]

jobs:
  opencode:
    if: |
      (contains(github.event.comment.body, '/oc') ||
       contains(github.event.comment.body, '/opencode')) &&
      (github.event.comment.author_association == 'OWNER' ||
       github.event.comment.author_association == 'MEMBER')
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: write
      pull-requests: write
      issues: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Run opencode
        uses: sst/opencode/github@latest
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        with:
          model: anthropic/claude-sonnet-4-20250514
```

## Setup Instructions

### 1. Install OpenCode GitHub App

Visit [github.com/apps/opencode-agent](https://github.com/apps/opencode-agent) and install the app on your target repository.

### 2. Configure API Keys

In your repository settings:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add your API key as a secret (e.g., `ANTHROPIC_API_KEY`)
3. Ensure the secret name matches your `workflow.env_key` configuration

### 3. Deploy the Workflow

1. Generate the workflow using this script
2. Copy the generated file to `.github/workflows/opencode.yml` in your repository
3. Commit and push the changes

### 4. Test the Setup

Create a GitHub issue and comment with `/opencode explain this issue` to test the integration.

## Multiple Environment Support

You can maintain different configurations for different environments:

```bash
# Development environment
python ogc/generate_workflow.py \
  --config environments/dev.properties \
  --output dev/.github/workflows/opencode.yml

# Production environment
python ogc/generate_workflow.py \
  --config environments/prod.properties \
  --output prod/.github/workflows/opencode.yml
```

Example environment-specific configurations:

**environments/dev.toml**:

```toml
[gh.workflow]
env_key = "ANTHROPIC_API_KEY_DEV"
model = "anthropic/claude-haiku-3-20240307"  # Faster, cheaper model for dev
```

**environments/prod.toml**:

```toml
[gh.workflow]
env_key = "ANTHROPIC_API_KEY_PROD"
model = "anthropic/claude-sonnet-4-20250514"  # More capable model for production
```

## Configuration Validation

The script includes comprehensive validation to ensure your configuration is correct:

### ✅ **Validation Features**

- **Model Format**: Ensures models follow the `provider/model` format
- **Environment Variables**: Validates environment variable names
- **Empty Values**: Prevents empty configuration values
- **Missing Keys**: Warns about missing keys and shows defaults being used

### **Example Validation Output**

**Valid Configuration**:

```bash
python ogc/control/github/generate_workflow.py --config ogc/config.toml --verbose
# ✅ Workflow generated successfully
```

**Invalid Model Format**:

```bash
❌ Configuration Errors:
   • Invalid model format 'invalid-model' - expected format: provider/model (e.g., 'anthropic/claude-sonnet-4-20250514')
```

**Missing Configuration Keys**:

```bash
⚠️  Configuration Warnings:
   • Missing 'gh.workflow.env_key' - using default: ANTHROPIC_API_KEY
   • Missing 'gh.workflow.model' - using default: anthropic/claude-sonnet-4-20250514
```

## Troubleshooting

### Common Issues

1. **File not found error**:

   ```bash
   ❌ Error: Configuration file not found: config.toml
   ```

   **Solution**: Ensure the configuration file exists or specify the correct path with `--config`.

2. **Permission denied**:

   ```bash
   PermissionError: [Errno 13] Permission denied: 'ogc/generated/.github/workflows/opencode.yml'
   ```

   **Solution**: Check file permissions or ensure the output directory is writable.

3. **Invalid TOML format**:

   ```bash
   ❌ TOML parsing error: Invalid TOML syntax
   ```

   **Solution**: Ensure your TOML file follows proper TOML syntax with sections like `[gh.workflow]`.

4. **Invalid model format**:

   ```bash
   ❌ Configuration Errors:
      • Invalid model format 'gpt4' - expected format: provider/model
   ```

   **Solution**: Use the correct format like `openai/gpt-4` or `anthropic/claude-sonnet-4-20250514`.

5. **Empty configuration values**:

   ```bash
   ❌ Configuration Errors:
      • Configuration key 'gh.workflow.env_key' has an empty value
   ```

   **Solution**: Provide a value for all configuration keys or remove the line to use defaults.

6. **Missing TOML library**:

   ```bash
   📦 TOML parsing library not found. Installing tomli...
   ✅ Successfully installed tomli
   ```

   **Note**: The script automatically installs the required TOML parsing library if not available.

### Validation

To validate your generated workflow:

```bash
# Generate and inspect the output
python ogc/generate_workflow.py --config ogc/config.toml --output - --verbose

# Check the generated file
cat ogc/generated/.github/workflows/opencode.yml
```

## Integration with OpenCode Agents

This workflow generator is part of the larger OpenCode Agents ecosystem. The generated workflows integrate seamlessly with:

- **Task Management**: Automatic issue triage and task breakdown
- **Code Review**: AI-powered code review and suggestions
- **Documentation**: Automatic documentation generation
- **Testing**: Automated test generation and validation

## Contributing

When modifying the workflow generator:

1. **Test thoroughly** with different configuration combinations
2. **Validate output** against OpenCode documentation
3. **Update documentation** to reflect any changes
4. **Follow security best practices** for handling API keys

## References

- [OpenCode Documentation](https://opencode.ai/docs)
- [OpenCode GitHub Integration](https://opencode.ai/docs/github)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OpenCode GitHub App](https://github.com/apps/opencode-agent)
