import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface GenerationRequest {
  input_type: 'topic' | 'prompt';
  input_content: string;
}

export interface GenerationResponse {
  id: number;
  input_type: string;
  input_content: string;
  hook: string | null;
  caption: string | null;
  cta: string | null;
  final_output: string;
  cost: number;
  hook_cost: number;
  caption_cost: number;
  cta_cost: number;
  merge_cost: number;
  timestamp: string;
}

export interface GenerationListItem {
  id: number;
  input_type: string;
  input_content: string;
  final_output: string;
  cost: number;
  timestamp: string;
}

export interface HistoryResponse {
  items: GenerationListItem[];
  total: number;
  page: number;
  page_size: number;
}

export const apiService = {
  async generatePost(request: GenerationRequest): Promise<GenerationResponse> {
    const response = await api.post<GenerationResponse>('/api/generate', request);
    return response.data;
  },

  async getHistory(page: number = 1, pageSize: number = 10): Promise<HistoryResponse> {
    const response = await api.get<HistoryResponse>('/api/history', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  async getGeneration(id: number): Promise<GenerationResponse> {
    const response = await api.get<GenerationResponse>(`/api/history/${id}`);
    return response.data;
  },

  async deleteGeneration(id: number): Promise<void> {
    await api.delete(`/api/history/${id}`);
  },
};

