const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface QueryRequest {
  query: string;
  mode?: 'general' | 'clinical';
  top_k?: number;
  clinical_data?: ClinicalData;
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
};
