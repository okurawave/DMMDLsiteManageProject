import type { Timestamp } from 'firebase/firestore';

export type Work = {
  id: string;
  title: string;
  uid?: string | null;
  createdAt?: Timestamp | { seconds: number; nanoseconds: number } | null;
};

export type WorkCreate = {
  title: string;
  uid?: string | null;
};
