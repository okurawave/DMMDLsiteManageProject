import { create, type StateCreator } from 'zustand';

interface CounterState {
  count: number;
  inc: () => void;
  dec: () => void;
}

const creator: StateCreator<CounterState> = (set) => ({
  count: 0,
  inc: () => set((s) => ({ count: s.count + 1 })),
  dec: () => set((s) => ({ count: s.count - 1 })),
});

export const useCounter = create<CounterState>(creator);
