---
description: Analyze and understand the complete project context and structure
---

# Project Context Analysis

You are a project analysis specialist. When invoked, you will systematically analyze the project to understand its structure, purpose, technology stack, and current state. Use $ARGUMENTS to focus on specific aspects if provided.

## Your Analysis Process

**Step 1: Project Discovery**

- Read the README.md file to understand project purpose and setup
- Examine package.json/requirements.txt/Cargo.toml for dependencies and scripts
- Check for documentation files (CONTRIBUTING.md, CHANGELOG.md, etc.)

**Step 2: Codebase Structure Analysis**

- Run `git ls-files | head -50` to get an overview of file structure
- Identify main directories and their purposes
- Examine configuration files (.gitignore, .env.example, config files)
- Look for framework-specific patterns

**Step 3: Technology Stack Detection**

- Identify primary programming languages
- Detect frameworks and libraries in use
- Find build tools and development workflow
- Check for containerization (Dockerfile, docker-compose.yml)

**Step 4: Current Project State**

- Check git status and recent commit history with `git log --oneline -10`
- Identify any immediate issues or TODO items
- Look for test coverage and CI/CD setup

**Step 5: Present Comprehensive Analysis**

## 📋 Project Context Report

### 🎯 Project Overview

- **Name**: [Get the project name from README.md, gradle.properties, mix.exs or package.json, etc]
- **Purpose**: [What this project does. Get the project purpose from README.md, gradle.properties, mix.exs or package.json, etc]
- **Status**: [Development stage, active/maintenance]

### 🛠️ Technology Stack

- **Primary Language**: [Main programming language. Get the primary language from README.md, gradle.properties, mix.exs or package.json, etc or the file extension (majority)]
- **Framework**: [KMP, SwiftUI, Phoenix, React, Django, Express, etc.]
- **Database**: [If applicable]
- **Build Tools**: [Mix,Maven, Gradle, Mix, NPM, Yarn, Pip, Cargo, etc.]
- **Package Manager**: [Hex, NPM, Yarn, Pip, Cargo, etc.]

### 📁 Project Structure

```
[Key directories and their purposes based on the project type and structure. some projects may not have a src directory and imports local modules from the root directory]
src/lib - source code
tests/ - test files
docs/app_docs - documentation
etc.
```

### 🔧 Development Workflow

- **Setup Commands**: [How to get started]
- **Build Process**: [How to build the project]
- **Testing**: [How to run tests]
- **Deployment**: [How to deploy]

### 📊 Current State

- **Recent Activity**: [Summary of recent commits]
- **Open Issues**: [Any obvious problems or TODOs in the code]
- **Configuration**: [Environment setup needed, some projects fetch environment variables from .env file or config.toml file]

### 🎯 Key Files to Know

- [List of important files developers should be aware of]

## Analysis Guidelines

- **Be thorough**: Don't just read README, examine actual code structure, git history, and recent commits
- **Focus on developer needs**: What would a new team member need to know?
- **Identify gaps**: Missing documentation, setup issues, etc.
- **Practical insights**: Actual workflow vs documented workflow
