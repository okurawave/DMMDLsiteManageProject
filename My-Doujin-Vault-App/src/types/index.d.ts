// グローバル型定義（My Doujin Vault用）
export type Work = {
  id: number;
  title: string;
  circleName?: string;
  authorName?: string;
  platform: 'DLsite' | 'Fanza' | 'Other';
  productUrl?: string;
  coverImageUrl?: string;
  tags: string[];
  rating: 0 | 1 | 2 | 3 | 4 | 5;
  status: 'Unread' | 'In Progress' | 'Finished' | 'Bookmarked';
  purchaseDate?: string;
  price?: number;
  note?: string;
  createdAt: string;
  updatedAt: string;
};

export type Author = {
  id: number;
  name: string;
  aliases: string[];
};

export type Circle = {
  id: number;
  name: string;
};
