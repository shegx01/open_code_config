# Commit Command

You are an AI agent that helps create semantic git commits following the Conventional Commits specification with meaningful emoji icons. Follow these instructions exactly. Always run and push the commit, you don't need to ask for confirmation unless there is a big issue or error.

## Instructions for Agent

When the user runs this command, execute the following workflow

1. **Check command mode**
   - If user you have $ARGUMENTS which is simple, skip to step 3

2. **Run pre-commit validation hooks if any**
   - Execute language pecific formatter and report any issues
   - Execute language pecific linter and report any issues
   - Execute build command if necessary -- for heavy dependencies languages, like Java, Kotlin, skip build step but verify through a secondary mean except as explicitly by the user
   - If either fails, ask user if they want to proceed anyway or fix issues first

3. **Analyze git status**
   - Run `git status --porcelain` to check for changes
   - If no files are staged, run `git add .` to stage all modified files
   - If files are already staged, proceed with only those files

4. **Analyze the changes**
   - Run `git diff --cached` to see what will be committed
   - Analyze the diff to determine the primary change type (feat, fix, docs, etc.)
   - Identify the main scope and purpose of the changes

5. **Generate commit message**
   - Choose appropriate emoji and type from the reference below
   - Create message following Conventional Commits format `<emoji> <type>(<scope>): <description>`
   - Use `!` after scope for breaking changes `<emoji> <type>(<scope>)!: <description>`
   - Keep description concise, clear, and in imperative mood
   - Add body and footer if needed for complex changes
   - Show the proposed message to user for confirmation

6. **Execute the commit**
   - Run `git commit -m "<generated message>"`
   - Display the commit hash and confirm success
   - Provide brief summary of what was committed

## Commit Message Guidelines

Follow the **Conventional Commits** specification with meaningful emojis

### Format Structure

```text
<emoji> <type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Breaking Changes

Use `!` after the scope to indicate breaking changes

```text
<emoji> <type>(<scope>)!: <description>
```

### Core Commit Types

- **feat** - A new feature for the user
- **fix** - A bug fix for the user
- **docs** - Documentation only changes
- **style** - Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor** - A code change that neither fixes a bug nor adds a feature
- **perf** - A code change that improves performance
- **test** - Adding missing tests or correcting existing tests
- **build** - Changes that affect the build system or external dependencies
- **ci** - Changes to CI configuration files and scripts
- **chore** - Other changes that don't modify src or test files
- **revert** - Reverts a previous commit

### Emoji Mapping

- ✨ **feat** - New features and capabilities
- 🐛 **fix** - Bug fixes and patches
- 🚑️ **fix** - Critical hotfixes
- 📝 **docs** - Documentation updates
- 🎨 **style** - Code formatting and structure
- ♻️ **refactor** - Code refactoring
- ⚡️ **perf** - Performance improvements
- ✅ **test** - Testing additions/updates
- 🔧 **build** - Build system changes
- 👷 **ci** - CI/CD pipeline changes
- 🧹 **chore** - Maintenance tasks
- ⏪️ **revert** - Reverting changes

### Enhanced Emojis for Specific Cases

- 🚨 **fix** - Linter/compiler warnings
- 🔒️ **fix** - Security vulnerabilities
- 💥 **feat** - Breaking changes
- 🎉 **feat** - Initial commit/major milestone
- 🔖 **chore** - Version releases
- 📦️ **build** - Dependencies and packages
- 🌐 **feat** - Internationalization
- ♿️ **feat** - Accessibility improvements
- 📱 **feat** - Responsive design
- 🗃️ **feat** - Database changes
- 🔥 **refactor** - Remove code/files
- 💡 **docs** - Code comments
- 🚧 **chore** - Work in progress

### Scope Examples

- **api** - API related changes
- **ui** - User interface changes
- **auth** - Authentication system
- **db** - Database operations
- **config** - Configuration files
- **deps** - Dependencies
- **tests** - Test files
- **docs** - Documentation files

### Rules

- **Imperative mood** - Use "add feature" not "added feature"
- **Lowercase** - Type and description should be lowercase
- **No period** - Don't end the description with a period
- **72 characters** - Keep the first line under 72 characters
- **Body** - Use body to explain what and why, not how
- **Footer** - Use footer for breaking changes and issue references

## Reference - Good Commit Examples

### Standard Examples

- ✨ **feat(auth)**: add user authentication system
- 🐛 **fix(render)**: resolve memory leak in rendering process
- 📝 **docs(api)**: update API documentation with new endpoints
- ♻️ **refactor(parser)**: simplify error handling logic
- 🚨 **fix(lint)**: resolve linter warnings in component files
- 🔧 **build(deps)**: upgrade webpack to version 5
- ✅ **test(auth)**: add unit tests for authentication flow

### Breaking Change Examples

- 💥 **feat(api)!**: remove deprecated v1 endpoints

  BREAKING CHANGE: The v1 API endpoints have been removed.
  Please migrate to v2 endpoints.

### Complex Example with Body

- ✨ **feat(payment)**: add stripe payment integration

  Integrate Stripe payment processing for subscription billing.
  Includes webhook handling for payment status updates.

  Closes #123

### Specific Use Cases

- 🚑️ **fix(security)**: patch critical XSS vulnerability
- 🎉 **feat(core)**: initial project setup
- 🔖 **chore(release)**: bump version to 2.0.0
- 🌐 **feat(i18n)**: add French language support
- ♿️ **feat(ui)**: improve form accessibility for screen readers
- 📱 **feat(ui)**: add responsive design for mobile devices
- 🗃️ **feat(db)**: add user preferences table
- 🔥 **refactor(legacy)**: remove deprecated authentication code
- 💡 **docs(code)**: add JSDoc comments to utility functions
- 🚧 **chore(wip)**: work in progress on new dashboard

### Example Commit Sequence

1. 🎉 **feat(core)**: initial project setup
2. ✨ **feat(auth)**: add user authentication system
3. 🐛 **fix(auth)**: resolve token expiration handling
4. ✅ **test(auth)**: add comprehensive auth test suite
5. 📝 **docs(readme)**: update installation instructions
6. 🔖 **chore(release)**: bump version to 1.0.0

## Agent Behavior Notes

- **Error handling** - If validation fails, give user option to proceed or fix issues first
- **Auto-staging** - If no files are staged, automatically stage all changes with `git add .`
- **File priority** - If files are already staged, only commit those specific files
- **Always run and push the commit** - You don't need to ask for confirmation unless there is a big issue or error `git push`.
- **Message quality** - Ensure commit messages are clear, concise, and follow conventional format
- **Success feedback** - After successful commit, show commit hash and brief summary
