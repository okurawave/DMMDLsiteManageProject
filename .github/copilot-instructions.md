承知いたしました。
GitHub Copilot（ChatやCLIなど）がプロジェクトの文脈を深く理解し、より的確で質の高いコードを生成・提案できるようにするための指示書（`copilot-instructions.md`またはリポジトリの`.github/copilot/instructions.md`）を作成します。

このファイルは、AIにプロジェクトの「憲法」と「設計思想」を教え込むためのものです。

issueごとに新しいブランチを切って終わったらprを出すようにしてください。

---

### **`.github/copilot/instructions.md`**

```markdown
# My Doujin Vault - GitHub Copilot Instructions

## 1. Project Overview & Core Philosophy

**Project Name:** My Doujin Vault

**Core Mission:** This is a digital doujinshi management app. Its primary goal is to provide users a tool to manage their collection's bibliographic information in one place.

**The MOST IMPORTANT concept is the architecture:**
- **This is a SERVERLESS application.** We DO NOT have our own backend server. Do not suggest creating or calling any custom API endpoints.
- **User data is sacred and owned by the user.** All data is stored directly in the user's own Google Drive and on their local device. We must not collect any user data.
- **Offline-first.** The app must be fully functional offline. UI interactions should immediately affect the local database (SQLite), and synchronization with Google Drive should happen in the background when online.

## 2. Core Architecture & Tech Stack

- **Framework:** React Native with Expo. All code should be written for this environment.
- **Language:** TypeScript. Use strict typing. Avoid `any` type whenever possible.
- **Navigation:** Expo Router. File-based routing is the standard (`/app` directory).
- **Local Database:** Expo-SQLite. For instant read/write access and offline capabilities.
- **Data Sync & Auth:** Google Drive API and Google OAuth. This is our "backend".
- **State Management:** Zustand. For simple, minimal global state management (e.g., authentication status, loading states).
- **Styling:** Use standard React Native `StyleSheet.create`. No CSS-in-JS libraries unless specified.

## 3. Directory Structure

Please adhere to this structure when creating new files.

```
/
├── app/              # Expo Router routes. Each file/directory is a screen.
├── assets/           # Fonts, images, icons.
├── components/       # Reusable, shared UI components (e.g., Button, Card, Input).
├── constants/        # App-wide constants (colors, layout values, etc.).
├── hooks/            # Custom React hooks for reusable logic (e.g., useDatabase, useAuth).
├── lib/              # Client-side libraries for external services (e.g., `googleDriveClient.ts`).
├── services/         # Core business logic, interacting with the database (e.g., `workService.ts`).
├── store/            # Zustand store definitions.
├── types/            # Global TypeScript type definitions (e.g., `index.d.ts`).
└── test/             # Test setup and mocks.
```

## 4. Coding Conventions & Best Practices

- **Formatting:** All code is formatted by Prettier.
- **Linting:** Follow the rules in `.eslintrc.js`. Pay attention to React Hooks rules.
- **Naming:**
  - Components: `PascalCase` (e.g., `WorkListItem.tsx`)
  - Functions/Variables: `camelCase` (e.g., `fetchWorksFromDB`)
  - Types/Interfaces: `PascalCase` (e.g., `type Work = { ... }`)
  - Files: `PascalCase.tsx` for components, `camelCase.ts` for hooks/services.
- **Components:**
  - Use Function Components with Hooks ONLY.
  - Keep components small and focused on a single responsibility.
  - Separate logic from presentation. Business logic should be in `hooks/` or `services/`, not directly in UI components.
- **TypeScript:**
  - Define clear types for all function parameters and return values.
  - Use the core data models defined below as the source of truth.

## 5. Core Data Models

This is the most critical section. All data handling must conform to these types.

```typescript
// file: types/index.d.ts

export type Work = {
  id: number; // Local SQLite ID
  title: string;
  circleName?: string;
  authorName?: string;
  platform: 'DLsite' | 'Fanza' | 'Other';
  productUrl?: string;
  coverImageUrl?: string;
  tags: string[]; // Stored as a JSON string in SQLite
  rating: 0 | 1 | 2 | 3 | 4 | 5;
  status: 'Unread' | 'In Progress' | 'Finished' | 'Bookmarked';
  purchaseDate?: string; // ISO 8601 format (YYYY-MM-DD)
  price?: number;
  note?: string;
  createdAt: string; // ISO 8601 format
  updatedAt: string; // ISO 8601 format
};

// For "Detailed Mode"
export type Author = {
  id: number;
  name: string;
  aliases: string[]; // Other pen names, stored as JSON string
};

export type Circle = {
  id: number;
  name: string;
};
```

## 6. Key Implementation Patterns

### Interacting with the Local Database (Expo-SQLite)

All database operations must be wrapped in transactions and be async. Use the service layer (`services/`) for this.

```typescript
// Example in services/workService.ts
import * as SQLite from 'expo-sqlite';

const db = SQLite.openDatabaseSync('mydoujinvault.db');

export const addWork = async (work: Omit<Work, 'id' | 'createdAt' | 'updatedAt'>): Promise<void> => {
  const now = new Date().toISOString();
  await db.execAsync(
    'INSERT INTO works (title, tags, createdAt, updatedAt) VALUES (?, ?, ?, ?)',
    [work.title, JSON.stringify(work.tags), now, now]
  );
};
```

### State Management (Zustand)

Keep stores minimal. Only use for truly global state.

```typescript
// Example in store/authStore.ts
import { create } from 'zustand';

type AuthState = {
  isLoggedIn: boolean;
  accessToken: string | null;
  login: (token: string) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  isLoggedIn: false,
  accessToken: null,
  login: (token) => set({ isLoggedIn: true, accessToken: token }),
  logout: () => set({ isLoggedIn: false, accessToken: null }),
}));
```

## 7. Testing

- **Frameworks:** Jest with React Native Testing Library.
- **Location:** Test files (`*.test.tsx`) should be co-located with the files they are testing.
- **Focus:**
  - **Unit Tests:** For custom hooks and service functions. Mock dependencies.
  - **Component Tests:** For UI components. Test for rendering and user interaction, not implementation details.
```