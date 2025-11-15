# Developer Tooling & Cloud SDKs

This final section specifies the essential, non-negotiable tools for interacting with Google Cloud and ensuring a productive, language-specific development experience.

### **1. The Universal Requirement: Google Cloud CLI**

Every developer on the project **must** have the **Google Cloud CLI (`gcloud`)** installed and authenticated. It is the foundational tool for all manual and scripted interactions with the project's cloud environment.

### **2. Language-Specific Google Cloud SDKs**

Your application code **must** use the official Google Cloud Client Libraries to interact with GCP services. These libraries handle authentication (via Workload Identity), retries, and provide an idiomatic interface.

*   **Node.js (TypeScript):** Use the `@google-cloud/[SERVICE]` packages (e.g., `@google-cloud/storage`, `@google-cloud/pubsub`).
*   **Python:** Use the `google-cloud-[SERVICE]` packages (e.g., `google-cloud-storage`, `google-cloud-pubsub`).
*   **Go:** Use the `cloud.google.com/go/[SERVICE]` packages.

### **3. Language-Specific Ecosystem Enhancements**

These tools are not optional; they are part of the standard toolkit for their respective languages to ensure productivity and code quality.

*   **Node.js (TypeScript) / Frontend:**
    *   **Configuration Management:** Use **`zod`** for validating environment variables at runtime. This prevents misconfigurations and ensures your application starts in a known-good state.
*   **Python:**
    *   **Configuration Management:** Use **`pydantic`** for settings management. It provides the same benefits as `zod` for the Python ecosystem.
    *   **CLI Tooling:** For any Python-based CLIs, use **`Typer`** or **`Click`**. They provide a simple, declarative way to build robust command-line interfaces.
*   **Go:**
    *   **Configuration Management:** Use **`viper`** for handling configuration from files, environment variables, and flags.
    *   **CLI Tooling:** Use **`cobra`** to build powerful, modern CLI applications. It is the foundation of many popular tools like `kubectl` and `hugo`.
