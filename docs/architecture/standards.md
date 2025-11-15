# Professional Project Standards & AI Development

This section covers the non-negotiable standards for code quality, dependency management, and specialized AI development workflows.

### **1. Caching Strategy: Performance & Cost Control**

Caching is not an afterthought; it is a primary architectural concern.

*   **Core Caching:** Use an in-memory cache for frequently accessed, non-critical data.
    *   **Technology:** **Redis**. It is the industry standard.
    *   **Cloud Equivalent:** **Memorystore for Redis**. Provision this via Terraform and connect to it from Cloud Run via a Serverless VPC Access Connector, just like with Cloud SQL.
    *   **Local Development:** Add a `redis` service to your `docker-compose.yml`.
*   **LLM Semantic Caching:** A critical pattern for AI applications.
    *   **Problem:** LLM calls are slow and expensive. Many user queries are semantically identical even if worded differently (e.g., "how do I reset my password?" vs. "I forgot my password").
    *   **Solution:** Before calling the LLM, check your Redis cache for a similar, previously answered query. This involves generating embeddings for the new query and performing a vector similarity search against cached queries.
    *   **Implementation:** Use a library like `gptcache` or build a simple version using Redis's vector search capabilities.

### **2. AI/ML Development & Prototyping**

*   **Agentic Frameworks:** For building applications that reason and orchestrate tool use.
    *   **Default Choice:** **LangChain & LangGraph (Python)**. It is the most mature, flexible, and widely adopted ecosystem. Its agnosticism allows you to swap components (models, vector stores) easily.
    *   **Google-Native Option:** **Google ADK (Agents & Development Kit)**. A strong contender for projects that are deeply integrated with Vertex AI from the start. Monitor its maturity. Use it if its native integrations provide a significant advantage over LangChain for your specific use case.
*   **Rapid Prototyping:**
    *   **Tool:** **Gradio**. Use this for building quick, interactive UIs to test and share your AI models and pipelines. This is for internal experimentation, not the production user-facing UI.
*   **Model & Dataset Sourcing:**
    *   **Platform:** **Hugging Face**. It is the primary resource for sourcing open-source pre-trained models (e.g., for embedding generation, classification) and datasets. Use their `transformers` library to easily download and use these models in your Python backend.

### **3. Code Quality & Dependency Management**

These are mandatory for all projects.

*   **Code Style & Linting (Enforced in CI):**
    *   **JavaScript/TypeScript:** **ESLint** (for linting) and **Prettier** (for formatting). Use a pre-commit hook to run these automatically.
    *   **Python:** **Ruff** (for ultra-fast linting and formatting). It replaces older tools like Black, isort, and Flake8.
    *   **Go:** Standard `gofmt` and `golint`.
*   **Dependency Management:**
    *   **Node.js:** Use `npm` or `pnpm`. All projects **must** have a `package-lock.json` or `pnpm-lock.yaml` file committed to the repository to ensure reproducible builds.
    *   **Python:** Use **`uv`** with a `pyproject.toml` file. This is the modern, high-speed replacement for `pip` and `venv`. The `pyproject.toml` defines all dependencies, and `uv` creates a virtual environment based on it.
