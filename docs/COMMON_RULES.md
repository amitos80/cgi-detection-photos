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


## Testing

- Vitest for unit testing
- Testing Library for component tests
- Playwright for E2E tests
- When writing tests, do it one test case at a time
- Use `expect(VALUE).toXyz(...)` instead of storing in variables
- Omit "should" from test names (e.g., `it("validates input")` not `it("should validate input")`)
- Test files: `*.test.ts` or `*.spec.ts`
- Mock external dependencies appropriately

## AI

- For AI-related development, especially for Retrieval-Augmented Generation (RAG), refer to the chunking strategy guidelines in [CHUNKING.md](./CHUNKING.md).

## Security

- Use appropriate data types that limit exposure of sensitive information
- Never commit secrets or API keys to repository
- Use environment variables for sensitive data
- Validate all user inputs on both client and server
- Use HTTPS in production
- Regular dependency updates
- Follow principle of least privilege

## Git Workflow

- ALWAYS run `pnpm check` before committing
- Fix linting errors with `pnpm check:fix`
- Run `pnpm build` to verify typecheck passes
- NEVER use `git push --force` on the main branch
- Use `git push --force-with-lease` for feature branches if needed
- Always verify current branch before force operations

## Configuration

When adding new configuration options, update all relevant places:
1. Environment variables in `.env.example`
2. Configuration schemas in `src/config/`
3. Documentation in the nearest (to the files/added/deleted/changed) README.md

