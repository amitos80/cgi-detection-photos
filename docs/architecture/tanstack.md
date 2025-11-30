```markdown
# 💡 Frontend Architecture Specification for AI Assistant

This document outlines the architectural specifications for the frontend application, which is built on the **Vite + React + TypeScript** stack, utilizing **TanStack Query** for server state management and **TanStack Router** for type-safe routing.

---

## 1. Core Technology Stack

| Area | Technology | Purpose & Rationale |
| :--- | :--- | :--- |
| **Build & Tooling** | **Vite** | Fast development server and optimized production builds. Essential for performance. |
| **Language** | **TypeScript** | Enforced for type safety, reducing runtime errors, and enhancing developer experience, especially critical when handling complex AI API responses. |
| **UI Framework** | **React** | Component-based UI development. |
| **Routing** | **TanStack Router** | **Type-safe routing**. Crucial for managing complex application states and search parameters (e.g., chat ID). |
| **Server State** | **TanStack Query** (React Query) | Manages all asynchronous data (API calls to the AI backend). Handles caching, automatic refetching, background updates, and loading states. |
| **Local State** | **Zustand** (or React Context) | For simple, non-API-related application state (e.g., UI theme, modal visibility). |
| **Styling** | **Tailwind CSS** | Consistency, speed, and easy theming/responsiveness. |

---

## 2. Project Structure & Organization

The project will follow a Feature-Sliced Design (FSD) or a modified Domain/Feature-Driven structure to ensure high cohesion and low coupling.

```

src/
├── assets/             \# Static files (images, fonts, svgs)
├── components/         \# Reusable, application-agnostic UI components
│   ├── ui/             \# Core design system components (Button, Input)
│   └── shared/         \# Simple, non-feature components
├── features/           \# **Core of the app - Grouped by domain/feature**
│   ├── chat/           \# (e.g., The main AI Chat/Conversation flow)
│   │   ├── api/        \# TanStack Query Hooks (useGetChat, useSendMessage)
│   │   ├── components/ \# Chat-specific components (ChatWindow, Message, MessageStream)
│   │   ├── hooks/      \# Feature-specific custom hooks
│   │   └── types/      \# Feature-specific TypeScript types/interfaces
│   ├── auth/           \# (e.g., Login, Signup, Auth API)
│   └── settings/       \# (e.g., User preferences, API key configuration)
├── hooks/              \# Application-wide, reusable custom hooks (e.g., useLocalStorage)
├── layouts/            \# Wrappers for entire page structures (e.g., MainLayout, AuthLayout)
├── pages/              \# Route components (often simple wrappers for feature components)
├── services/           \# Low-level API client, QueryClient setup, error interceptors
├── store/              \# Global local state (Zustand store definitions)
├── styles/             \# Global CSS, theme definitions, utility classes
└── main.tsx            \# Entry point

````

---

## 3. State Management Strategy

### 3.1. Server State (The AI Data) - TanStack Query

* **Source of Truth:** The backend API.
* **Query Keys:** Strictly enforced key factories (e.g., `chatKeys.detail(id)`) co-located within the feature's `api/` directory.
* **Mutations:** Used for write operations (sending prompts). **Optimistic Updates** are used to display the user's message immediately.
* **Real-time/Streaming:** Streamed AI responses **bypass the standard query cache** during transmission but rely on `queryClient.setQueryData` for incremental updates and final persistence (see Section 7).

### 3.2. Local UI State - Zustand / React Context

* **Global Local State (Zustand):** Used sparingly for simple, non-async state needed application-wide (e.g., sidebar visibility).
* **Component Local State:** Use `useState`/`useReducer` for all component-specific state.

---

## 4. API Layer & Data Flow

* **Unidirectional Data Flow (UDF):** Data flows downward; events flow upward.
* **API Client (`services/api-client.ts`):** A thin wrapper around `fetch` or `Axios` handling base headers, global error responses (401), and standardizing payloads.
* **Repository Pattern:** TanStack Query hooks act as the data access layer, abstracting fetching and caching logic from the UI.
* **TypeScript Enforced:** Every API payload must have a corresponding TypeScript interface.

---

## 5. AI-Specific Considerations

1.  **Response Streaming:** The component must handle incremental data chunks efficiently. A dedicated custom hook (`useStreamedResponse` or logic embedded in `useMutation`) manages chunk aggregation.
2.  **Latency & Loading States:** Utilize TanStack Query’s `isLoading`, `isFetching`, and `isError` for explicit user feedback (e.g., Skeleton loaders).
3.  **Cancellation:** Implement **request cancellation** (`AbortController`) for long-running stream requests to allow users to interrupt or send a new prompt quickly.

---

## 6. TanStack Router Setup

### 6.1. File-Based Routing and Type Safety

* **Vite Plugin:** Use `@tanstack/router-vite-plugin` to auto-generate the type-safe route tree (`routeTree.gen.ts`) based on files in `src/routes/`.
* **Route Structure:** Follows the file system (e.g., `src/routes/chat/$chatId.tsx` maps to `/chat/:chatId`). The `__root.tsx` file defines the mandatory root layout and error boundaries.

### 6.2. Route Example with Search Parameters

```typescript
// Example Search Parameter Validation
import { z } from 'zod';
const searchSchema = z.object({
  model: z.enum(['GPT-4', 'Claude-3']).optional().default('GPT-4'),
});

// Route Configuration
export const Route = createFileRoute('/chat/$chatId')({
  validateSearch: searchSchema, // Enforces type-safe access to 'model' search parameter
  loader: async ({ params, context }) => {
    // Uses context.queryClient.fetchQuery to get initial data, 
    // ensuring the data is also cached by TanStack Query.
  },
  // ...
});
````

-----

## 7\. AI Response Streaming Implementation (Deep Dive)

The streaming mechanism combines Mutation and manual cache updates to manage the real-time nature of AI responses.

### A. Core Logic Summary

1.  **Optimistic Update:** The `useMutation` function performs a manual `queryClient.setQueryData` to immediately add the user's message and an empty AI message placeholder to the cache.
2.  **Streaming:** The low-level API function initiates the fetch stream. Inside a `while(true)` loop, it incrementally updates the content of the AI message placeholder directly in the cache via repeated `queryClient.setQueryData` calls.
3.  **Finalization:** Once the stream is `done`, a final `setQueryData` call updates the message object, marking `isStreaming: false` and ensuring the final content is persistent.

### B. Code Snippet Example (Conceptual)

```typescript
// Inside streamMessage low-level function:

// 1. Add placeholder to cache
queryClient.setQueryData(chatKeys.detail(conversationId), (oldData) => {
	// ... add user message and AI placeholder ...
});

// 2. Streaming Loop (Incremental Updates)
try {
  while (true) {
    // ... read chunk and decode ...
    // Update content in cache iteratively
    queryClient.setQueryData(
      chatKeys.detail(conversationId),
      (oldData) => (
        // ... map over oldData.messages and update the content of the AI placeholder ...
        console.log('oldData ', oldData)
      )
    );
  }
} finally {
  // 3. Finalization
  queryClient.setQueryData(chatKeys.detail(conversationId), (oldData) => {
	  // ... map over messages and set isStreaming: false for the final message ...
  });
}
```

-----

## 8\. Advanced Error Handling Strategy

Errors are handled at three distinct layers: Data, Routing, and Rendering.

### 8.1. TanStack Query Error Handling (Data Layer)

* **Global Network Error:** Default options are set for automatic retries. Failed retries trigger a global notification (toast).
* **Authentication Error (401):** An API client interceptor detects the 401 status, clears the local session, and forces a `router.navigate('/login')`.
* **Mutation Failure:** Handled via the `onError` callback in `useMutation`, which manages local state rollback and displays component-specific feedback.

### 8.2. TanStack Router Error Handling (Route Layer)

| Error Type          | Router Mechanism                                      | Resolution                                                                                    |
|:--------------------|:------------------------------------------------------|:----------------------------------------------------------------------------------------------|
| **Route Not Found** | Explicitly throwing `notFound()` from the `loader`.   | Renders the nearest ancestor route's `notFoundComponent` (typically defined on `__root.tsx`). |
| **Loader Failure**  | A generic JS `Error` thrown by the `loader` function. | Renders the nearest ancestor route's `errorComponent`. The error should be logged globally.   |

### 8.3. Component Error Boundaries (Rendering Layer)

* **Placement:** Error Boundaries (using `react-error-boundary` or equivalent) are wrapped around major feature components (e.g., `<ChatWindow />`).
* **Purpose:** To catch and gracefully manage rendering and lifecycle errors, preventing a single component crash from bringing down the entire application UI.

<!-- end list -->

```
```
