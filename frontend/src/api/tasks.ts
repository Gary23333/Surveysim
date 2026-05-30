import apiClient from "./client";
import type { TaskCreate } from "@/types";

export const tasksApi = {
  create: async (data: TaskCreate) => { const response = await apiClient.post("/tasks/", data); return response.data; },
  list: async (params?: { status?: string; scenario_type?: string; page?: number; size?: number }) => { const response = await apiClient.get("/tasks/", { params }); return response.data; },
  get: async (taskId: string) => { const response = await apiClient.get(`/tasks/${taskId}/`); return response.data; },
  start: async (taskId: string) => { const response = await apiClient.post(`/tasks/${taskId}/start/`); return response.data; },
  pause: async (taskId: string) => { const response = await apiClient.post(`/tasks/${taskId}/pause/`); return response.data; },
  resume: async (taskId: string) => { const response = await apiClient.post(`/tasks/${taskId}/resume/`); return response.data; },
  stop: async (taskId: string) => { const response = await apiClient.post(`/tasks/${taskId}/stop/`); return response.data; },
  delete: async (taskId: string) => { const response = await apiClient.delete(`/tasks/${taskId}/`); return response.data; },
  getResults: async (taskId: string) => { const response = await apiClient.get(`/tasks/${taskId}/results/`); return response.data; },
  getStatus: async (taskId: string) => { const response = await apiClient.get(`/tasks/${taskId}/status/`); return response.data; },
  exportResults: async (taskId: string, format: string) => {
    if (format === "csv") {
      const response = await apiClient.get(`/tasks/${taskId}/export/csv/`, { responseType: "blob" });
      return response.data;
    }
    const response = await apiClient.get(`/tasks/${taskId}/export/json/`);
    return response.data;
  },
};
