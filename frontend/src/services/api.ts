import axios from 'axios';
import type { Task, TaskCreate } from '../types/task';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const taskApi = {
  createTask: async (task: TaskCreate): Promise<Task> => {
    const response = await api.post<Task>('/tasks/', task);
    return response.data;
  },

  getTask: async (taskId: string): Promise<Task> => {
    const response = await api.get<Task>(`/tasks/${taskId}`);
    return response.data;
  },

  listTasks: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<{ tasks: Task[]; total: number; page: number; page_size: number; has_more: boolean }> => {
    const response = await api.get('/tasks/', { params });
    return response.data;
  },

  updateTask: async (taskId: string, updates: Partial<Task>): Promise<Task> => {
    const response = await api.put<Task>(`/tasks/${taskId}`, updates);
    return response.data;
  },

  deleteTask: async (taskId: string): Promise<void> => {
    await api.delete(`/tasks/${taskId}`);
  },
};

export const agentApi = {
  getStatus: async (taskId: string) => {
    const response = await api.get(`/agents/status/${taskId}`);
    return response.data;
  },

  executeAgent: async (taskId: string) => {
    const response = await api.post(`/agents/execute/${taskId}`);
    return response.data;
  },
};

export const healthApi = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  detailedCheck: async () => {
    const response = await api.get('/health/detailed');
    return response.data;
  },
};

export default api;

// Made with Bob
