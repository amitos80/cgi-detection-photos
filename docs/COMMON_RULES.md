# Common Rules For All Projects Must Be Complied With At All Times

## Shell/Terminal Work Guidelines Mandatory Rules

1. Infinite wait for command's input/status/etc prevention:
   a. use flags for minimal shell-interactions, important examples:
      1. flags -y or --yes: Automatically answers "yes" to any confirmation prompts. This is common in package managers like apt, yum, or brew
      2. flags -f or --force: Forces an action without asking for confirmation, even if the operation is potentially dangerous (e.g., in rm or cp)
      3. flags -q or --quiet: Suppresses non-error output, useful for scripts where you only need to know if the command succeeded or failed (e.g., grep -q)
      4. flags -s or --silent: Similar to --quiet, often suppressing even error messages in some commands
      5. flags -n or --no-act / --dry-run: Instructs the program to show what it would do without actually performing the action. This is a safety measure, not a way to run the command non-interactively in production
   
   6. b. infinit wait detection by using timeouts
      1. before executing a shell/terminal command always start a timeout of the most reasonable value for the command to finish running  
      2. if a timeout passed before the command finished, abort the command   
      3. notify the user in the by running the following command in shell/terminal: say "shell command timeout passed, aborted command"

## Code Style

- Tabs for indentation (2 spaces for YAML/JSON/MD)
- Use JSDoc docstrings for documenting TypeScript definitions, not `//` comments
- The number of characters in a single line show never exceeds 120 
- In CamelCase names, use "URL" (not "Url"), "API" (not "Api"), "ID" (not "Id")
- NEVER supress/ignore errors without asking for permission first (i.e: `@ts-expect-error` or `@ts-ignore` to suppress type errors)
- Modularity is Key: No single file should exceed 200 lines. If it grows too large, your first step is to propose a refactoring plan to break it into smaller, logical modules.
- Consistent Organization: We group files by feature. For example, a new `user` feature would have its logic in `src/users/`, its API routes in `src/api/routes/users.py`, and its tests in `tests/users/`.
- Clean Imports: Use absolute imports for clarity (e.g., `from src.utils import helpers`). Avoid circular dependencies.
- Environment First: All sensitive keys, API endpoints, or configuration variables must be managed through a `.env` file and loaded using `python-dotenv`. Never hardcode them.
- Follow the Standards: All Python code must be formatted with `black` and adhere to `PEP8` guidelines.
- Type Safety: Use type hints for all function signatures and variables. We use `mypy` to enforce this.
- Data Certainty: Use `pydantic` for all data validation, especially for API request and response models. This is our single source of truth for data shapes.


## Code Quality & Reliability
- Test Everything That Matters: Every new function, class, or API endpoint must be accompanied by unit tests in the `tests/` directory.
- The Test Triad* For each feature, provide at least three tests:
    1. A "happy path" test for expected behavior.
    2. An "edge case" test for unusual but valid inputs.
    3. A "failure case" test for expected errors or invalid inputs.
- Docstrings are Non-Negotiable: Every function must have a Google-style docstring explaining its purpose, arguments (`Args:`), and return value (`Returns:`).

## Testing

- Vitest for unit testing
- Testing Library for component tests
- Playwright for E2E tests
- When writing tests, do it one test case at a time
- Use `expect(VALUE).toXyz(...)` instead of storing in variables
- Omit "should" from test names (e.g., `it("validates input")` not `it("should validate input")`)
- Test files: `*.test.ts` or `*.spec.ts`
- Mock external dependencies appropriately

## Security

- Use appropriate data types that limit exposure of sensitive information
- Never commit secrets or API keys to repository
- Use environment variables for sensitive data
- Validate all user inputs on both client and server
- Use HTTPS in production
- Regular dependency updates
- Follow principle of least privilege

## Configuration

When adding new configuration options, update all relevant places:
1. Environment variables in `.env.example`
2. Configuration schemas in `src/config/`

## Documentation

When adding new features, changing existing features etc
1. Write/Edit the documentation in the nearest (to the files/added/deleted/changed) README.md
