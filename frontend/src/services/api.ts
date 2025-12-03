const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface QueryRequest {
  query: string;
  mode?: 'general' | 'clinical';
  top_k?: number;
  clinical_data?: ClinicalData;
  chat_id?: string;
}

export interface ClinicalData {
  age?: number;
  gender?: string;
  weight?: number;
  height?: number;
  conditions?: string[];
  allergies?: string[];
  medications?: string[];
  diet_type?: string;
  activity_level?: string;
}

export interface Source {
  title: string;
  organization: string;
  organization_acronym?: string;
  year?: number;
  author: string;
  link?: string;
  similarity: string;
}

export interface QueryResponse {
  query: string;
  answer: string;
  sources: Source[];
}

export interface Chat {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  sources?: Source[];
  timestamp: string;
}

export interface Citation {
  id: string;
  label: string;
  organization: string;
  year: string;
  title: string;
  url?: string;
  excerpt?: string;
}

export interface ChatListResponse {
  chats: Chat[];
}

export interface ChatMessagesResponse {
  messages: Message[];
}

export interface CreateChatRequest {
  title: string;
}

export interface CreateChatResponse {
  chat_id: string;
}

export const api = {
  async query(request: QueryRequest): Promise<QueryResponse> {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  },

  async health(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/api/health`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  },

  async createChat(title: string): Promise<CreateChatResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chats`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create chat: ${response.statusText}`);
    }

    return response.json();
  },

  async listChats(limit: number = 50): Promise<ChatListResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chats?limit=${limit}`);

    if (!response.ok) {
      throw new Error(`Failed to list chats: ${response.statusText}`);
    }

    return response.json();
  },

  async getChat(chatId: string): Promise<ChatMessagesResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chats/${chatId}`);

    if (!response.ok) {
      throw new Error(`Failed to get chat: ${response.statusText}`);
    }

    return response.json();
  },

  async deleteChat(chatId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/chats/${chatId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Failed to delete chat: ${response.statusText}`);
    }
  },
};
