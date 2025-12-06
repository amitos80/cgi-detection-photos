# The Developer's Pact: Must Comply With All Principles For All Tasks
 This document outlines the core principles and conventions we will follow in this project. All AI assistants and human developers must adhere to these rules for building high-quality, maintainable software._

### Principle 1: Communication Protocol
- **Every time a Step of a Task in **[./development-progress-tracking/TASKS_BREAKDOWN.md]** is done run the following command in shell: ```say "step done"```**
- **Every time a Task from **[./development-progress-tracking/TASKS_BREAKDOWN.md]** is done run the following command in shell: ```say "task cone"```**
- **Every time a Development Plan **[./development-progress-tracking/CURRENT_DEVELOPMENT_PLAN.md]** is done run the following command in shell: ```say "development plan completed"```**
- **Every time you have a question, before asking me anything you have to run the following command in shell: ```say "question"```**
- **Every time you finished a task and you go to idle because the is nothing else to complete run the following command in shell: ```say "idle"```**
- **Every time user interaction is expected (i.e: asking for user permission to execute command) run the following command in shell: ```say "waiting for your answer?"```**
- **Every time context is being generated from **[./GEMINI.md]** to MCP server run the following command in shell: ```say "context loaded to MCP server"```**

### Principle 2: Research Tasks
- **Never Change Codebase:** For Tasks of researching/learning/finding data/calculating/executing commands(/etc...) codebase for research, reading, learning (generally any task that does not require adding code to codebase) you MUST NEVER add/edit/update/remove/write any code to project's codebase

### Principle 3: Your Behavior as an Assistant
- **Clarify, Don't Assume:** If a requirement is ambiguous or context is missing, your first action is to ask for clarification.
- **No Hallucinations:** Do not invent libraries, functions, or file paths.
- **Plan Before You Code:** For any non-trivial task, first outline your implementation plan in a list or with pseudocode.
- **Explain the "Why":** For complex or non-obvious blocks of code, add a `# WHY:` comment explaining the reasoning behind the implementation choice.

### Principle 4: Important Rules That Must Be Followed For Every Task
- **Common Ground Rules That Applies For All Tasks:** Most basic ground rule that applies allways is in [COMMON_RULES.md](COMMON_RULES.md) 
  
