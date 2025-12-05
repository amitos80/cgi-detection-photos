# AI Agents Project Instructions

You are the primary Gemini assistant for this repository. Your mission is to strictly enforce the following vendor-neutral project documents:

1.  **Behavioral Mandate:** Always review the files above before starting a task.
2.  **Project Rules (Mandatory):** **[[RULES_OF_ENGAGEMENT.md](docs/RULES_OF_ENGAGEMENT.md)]**
3.  **Common Rules For All Projects:** See **[[COMMON_RULES.md](docs/COMMON_RULES.md)]** for basic strict rules (e.g., NEVER use `git push --force` on the main branch).
4.  **Development PLAN is always in:**[[CURRENT_DEVELOPMENT_PLAN.md](development-progress-tracking/CURRENT_DEVELOPMENT_PLAN.md)]**
5.  **All Tasks Of Current Development Plan Broken Down To TODO Lists By Task:**[[TASKS_BREAKDOWN.md](development-progress-tracking/TASKS_BREAKDOWN.md)]**
6.  **All relevant online resources are always in:**[[RESOURCES.md](docs/RESOURCES.md)]**
7.  **All about project architecture**[[ARCHITECTURE.md](docs/ARCHITECTURE.md)]**

## Development Progress Reporting Rules - Mandatory to preappend this to all promts from now on

- Every time a Step of a Task in **[./development-progress-tracking/TASKS_BREAKDOWN.md]** is done run the following command in shell: say "step done"
- Every time a Task from **[./development-progress-tracking/TASKS_BREAKDOWN.md]** is done run the following command in shell: say "task cone"
- Every time a Development Plan **[./development-progress-tracking/CURRENT_DEVELOPMENT_PLAN.md]** is done run the following command in shell: say "development plan completed"
- Every time you have a question for me run the following command in shell: say "question"
- Every time you finished a task and you go to idle because the is nothing else to complete run the following command in shell: say "idle"
- Every time context is being generated from **[./GEMINI.md]** to MCP server run the following command in shell: say "context loaded to MCP server"
