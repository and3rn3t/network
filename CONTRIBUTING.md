# Contributing

Thank you for your interest in contributing! This guide will help you get started.

## How to Contribute

1. **Fork** the repository
2. **Create a branch** from `main` (see [Branch Naming](#branch-naming))
3. **Make your changes** with clear, focused commits
4. **Push** your branch and open a **Pull Request**

## Development Setup

<!-- TODO: Replace these steps with your project's actual setup instructions. -->

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Install dependencies
npm install        # TODO: Replace with your install command

# Run tests
npm test           # TODO: Replace with your test command

# Start development server
npm run dev        # TODO: Replace with your dev command
```

## Branch Naming

Use the format `type/short-description`:

- `feature/user-authentication`
- `fix/login-redirect-loop`
- `docs/update-api-reference`
- `chore/upgrade-dependencies`

See [git-conventions.instructions.md](.github/instructions/git-conventions.instructions.md) for full details.

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): short description

Optional longer body explaining what and why.

Refs: #123
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `perf`

**Examples:**

```
feat(auth): add OAuth2 login flow
fix(api): handle null response from user endpoint
docs: update contributing guide
test(cart): add edge case tests for empty cart
```

## Pull Request Process

1. Fill out the [PR template](.github/pull_request_template.md) completely
2. Ensure all checks pass (lint, tests, build)
3. Request a review from at least one maintainer
4. Address review feedback
5. A maintainer will merge your PR once approved

Keep PRs focused on a single logical change. Large changes should be split into smaller PRs.

## Code Style

This project uses shared code style guidelines enforced through:

- [`.editorconfig`](.editorconfig) — Cross-editor formatting
- [Code style instructions](.github/instructions/code-style.instructions.md) — Naming, formatting, and organization conventions

Run the linter before submitting:

```bash
npm run lint       # TODO: Replace with your lint command
```

## Testing

All new code should include tests. Follow the patterns documented in:

- [Testing instructions](.github/instructions/testing.instructions.md) — Unit test patterns and conventions

```bash
npm test           # TODO: Replace with your test command
```

## AI-Assisted Development

This repository includes configuration files for AI coding assistants (Copilot, Cursor, Windsurf, Cline, Claude Code). These files define project conventions so AI tools produce consistent, high-quality code.

- See [docs/AI-CUSTOMIZATION-GUIDE.md](docs/AI-CUSTOMIZATION-GUIDE.md) for details
- AI instructions in `.github/instructions/` are auto-loaded based on file patterns
- Prompts in `.github/prompts/` provide reusable task templates

You can use AI tools while contributing — the config files ensure generated code aligns with project standards.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code. Report unacceptable behavior to the project maintainers.

## Questions?

<!-- TODO: Add your preferred communication channel. -->

Open a [GitHub Discussion](https://github.com/YOUR_ORG/YOUR_REPO/discussions) or file an issue.
