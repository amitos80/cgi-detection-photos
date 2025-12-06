# The Developer's Pact: Must Comply With All Principles For All Tasks
 This document outlines the core principles and conventions we will follow in this project. All AI assistants and human developers must adhere to these rules for building high-quality, maintainable software._



### Principle 2: Always Breakdown a Task into TODO step instruction to ./development-progress-tracking/CURRENT_TASK.md
- **When Development Plan Gets Approved: Start by creating a small detailed instruction step TODOs for the current task you work on**
- **When starting to implement a task: with the task list and update the completed steps status**

### Principle 1: Communication Protocol
- **Every time a Step of a Task in **[./development-progress-tracking/TASKS_BREAKDOWN.md]** is done run the following command in shell: ```say "step done"```**
- **Every time a Task from **[./development-progress-tracking/TASKS_BREAKDOWN.md]** is done run the following command in shell: ```say "task cone"```**
- **Every time a Development Plan **[./development-progress-tracking/CURRENT_DEVELOPMENT_PLAN.md]** is done run the following command in shell: ```say "development plan completed"```**
- **Every time you have a question for me run the following command in shell: ```say "question"```**
- **Every time you finished a task and you go to idle because the is nothing else to complete run the following command in shell: ```say "idle"```**
- **Every time context is being generated from **[./GEMINI.md]** to MCP server run the following command in shell: ```say "context loaded to MCP server"```**

### Principle 2: Architecture & Structure
- **Modularity is Key:** No single file should exceed 500 lines. If it grows too large, your first step is to propose a refactoring plan to break it into smaller, logical modules.
- **Consistent Organization:** We group files by feature. For example, a new `user` feature would have its logic in `src/users/`, its API routes in `src/api/routes/users.py`, and its tests in `tests/users/`.
- **Clean Imports:** Use absolute imports for clarity (e.g., `from src.utils import helpers`). Avoid circular dependencies.
- **Environment First:** All sensitive keys, API endpoints, or configuration variables must be managed through a `.env` file and loaded using `python-dotenv`. Never hardcode them.

### Principle 3: Quality & Reliability
- **Test Everything That Matters:** Every new function, class, or API endpoint must be accompanied by unit tests in the `tests/` directory.
- **The Test Triad:** For each feature, provide at least three tests:
    1. A "happy path" test for expected behavior.
    2. An "edge case" test for unusual but valid inputs.
    3. A "failure case" test for expected errors or invalid inputs.
- **Docstrings are Non-Negotiable:** Every function must have a Google-style docstring explaining its purpose, arguments (`Args:`), and return value (`Returns:`).

### Principle 4: Code & Style
- **Follow the Standards:** All Python code must be formatted with `black` and adhere to `PEP8` guidelines.
- **Type Safety:** Use type hints for all function signatures and variables. We use `mypy` to enforce this.
- **Data Certainty:** Use **`pydantic`** for all data validation, especially for API request and response models. This is our single source of truth for data shapes.

### Principle 5: Your Behavior as an Assistant
- **Clarify, Don't Assume:** If a requirement is ambiguous or context is missing, your first action is to ask for clarification.
- **No Hallucinations:** Do not invent libraries, functions, or file paths.
- **Plan Before You Code:** For any non-trivial task, first outline your implementation plan in a list or with pseudocode.
- **Explain the "Why":** For complex or non-obvious blocks of code, add a `# WHY:` comment explaining the reasoning behind the implementation choice.

### Principle 6: Research Tasks
- **Never Change Codebase:** For Tasks of researching/learning/finding data/calculating/executing commands(/etc...) codebase for research, reading, learning (generally any task that does not require adding code to codebase) you MUST NEVER add/edit/update/remove/write any code to project's codebase

### Principle 7: Important Rules That Must Be Followed For Every Task
- **Common Ground Rules That Applies For All Tasks:** Most basic ground rule that applies allways are in [COMMON_RULES.md](COMMON_RULES.md) 
  
