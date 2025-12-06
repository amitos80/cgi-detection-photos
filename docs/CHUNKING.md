## Optimized CHUNCKING.md: Codebase Chunking Strategy for RAG 🤖

This strategy is optimized for **Code Generation and Implementation** in a codebase with concise, medium-sized functional files. The priority is providing the AI with **minimal functional units** and the **API context of neighboring functions**.

### 1. Guiding Principle (Reinforced)

**Retrieve the Minimal, Most Relevant, and Functionally Complete Code Block.**

This ensures the lowest possible token count per query while preserving the integrity of the code unit (function/method) required for generation tasks.

---

### 2. Universal Chunk Definition

A "chunk" is a single, self-contained logical unit.

| Code Language / Type | Recommended Chunk Boundary | Rationale |
| :--- | :--- | :--- |
| **Python** (`.py`) | **Function** or **Method** (the entire `def ...` block). | Single-responsibility principle. |
| **JS/TS/React** | **Function**, **`export`ed unit**, or **React Component**. | Focus on callable/renderable units for implementation. |
| **Interface/Type Defs** | **Entire Interface** or **Type Definition** block. | Necessary to maintain full type context. |
| **Configuration** (`.json`, `.yaml`) | A single **top-level object** or **array element**. | Treat entire configurations or routes as a single unit. |

---

### 3. Max Token / Character Limit (Tuned for Efficiency)

Given the concise file sizes, the token limit is reduced to maximize RAG efficiency.

* **Max Chunk Size:** **400 tokens** (approx. 1600 characters).
    * *If a unit exceeds this, the chunking process must implement a **hard split**, using comments or blank lines as heuristic guides, or be flagged as an exception.*

---

### 4. Context Augmentation (Metadata)

The following metadata **MUST** be stored for retrieval. The `entity_signature` is crucial for your priority.

| Metadata Field | Description | Purpose |
| :--- | :--- | :--- |
| `file_path` | Full path to the source file. | Locating the code for the user. |
| `entity_name` | The name of the entity (e.g., `calculate_tax`, `UserService`). | **Primary Semantic Filter.** |
| **`entity_signature`** | The full function/method signature (Name, parameters, return type). | **Crucial for implementation context.** |
| `docstring_summary` | The first sentence of the docstring/comment. | **Primary Retrieval Filter:** Matches user intent to purpose. |

---

### 5. Retrieval Strategy Notes (Optimized for Priority C)

1.  **Prioritize Functional Units:** Always retrieve the chunk matching the user's semantic intent first.
2.  **Retrieve Signatures for Context:** When a primary chunk is selected, the AI system **MUST** also retrieve the `entity_signature` metadata for all chunks immediately preceding and following the primary chunk *within the same file*.
3.  **Include Imports (Low Priority):** If the retrieved chunk is a function or method, include the file's top-level **local import statements** (e.g., `import { User } from './types'`) as a lower priority context addition.

---

### 6. Exclusion Rules (Standard)

The following files and directories **MUST NOT** be chunked or indexed:

* **Dependencies:** `node_modules/`, `vendor/`, `__pycache__`, compiled directories.
* **Build/Configuration:** `.git/`, `.gitignore`, `package-lock.json`, `yarn.lock`, `dist/`, `build/`.
* **Testing:** `tests/`, `__tests__/`, files ending in `.test.*`, `.spec.*`.
