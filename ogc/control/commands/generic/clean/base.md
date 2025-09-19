# Code Quality Cleanup

You are a code quality specialist. When provided with $ARGUMENTS (file paths or directories), systematically clean and optimize the code for production readiness. If no arguments provided, focus on currently open or recently modified files.

This command is language-agnostic and auto-detects the primary stack. Default priorities: Elixir and Kotlin Multiplatform (KMP).

## Your Cleanup Process

**Step 1: Analyze Target Scope**

- If $ARGUMENTS provided: Focus on specified files/directories
- If no arguments: Check git status for modified files and currently open files
- Identify language(s) by sentinel files and extensions, then select appropriate tools

**Step 2: Clean and Optimize**

- For each language, run appropriate cleanup tools (e.g., formatter, linter, optimizer)
- Remove language specific unused variables, logger, and insect files
- Additional cleanup steps may include:

## Step 3: Present Cleanup Report

### 📋 Cleanup Results

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
