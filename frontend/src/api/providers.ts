import apiClient from "./client";
import type { Provider, BehaviorPrompt } from "@/types";

export const providersApi = {
  // 获取Provider列表
  list: async () => {
    const response = await apiClient.get("/providers");
    return response.data;
  },

  // 获取Provider详情
  get: async (providerName: string) => {
    const response = await apiClient.get(`/providers/${providerName}`);
    return response.data;
  },

  // 创建Provider
  create: async (data: Provider) => {
    const response = await apiClient.post("/providers", data);
    return response.data;
  },

  // 更新Provider
  update: async (providerName: string, data: Partial<Provider>) => {
    const response = await apiClient.put(`/providers/${providerName}`, data);
    return response.data;
  },

  // 删除Provider
  delete: async (providerName: string) => {
    const response = await apiClient.delete(`/providers/${providerName}`);
    return response.data;
  },

  // 获取Provider支持的模型列表
  listModels: async (providerName: string) => {
    const response = await apiClient.get(`/providers/${providerName}/models`);
    return response.data;
  },

  // 测试Provider连接
  test: async (providerName: string) => {
    const response = await apiClient.post(`/providers/${providerName}/test`);
    return response.data;
  },

  // 真实连通性测试
  testConnect: async (providerName: string) => {
    const response = await apiClient.post(`/providers/${providerName}/test-connect`);
    return response.data;
  },

  // 从API检测可用模型
  detectModels: async (providerName: string) => {
    const response = await apiClient.post(`/providers/${providerName}/detect-models`);
    return response.data;
  },
};

export const behaviorPromptsApi = {
  // 获取行为提示词列表
  list: async () => {
    const response = await apiClient.get("/behavior-prompts");
    return response.data;
  },

  // 获取行为提示词详情
  get: async (promptId: string) => {
    const response = await apiClient.get(`/behavior-prompts/${promptId}`);
    return response.data;
  },

  // 创建行为提示词
  create: async (data: BehaviorPrompt) => {
    const response = await apiClient.post("/behavior-prompts", data);
    return response.data;
  },

  // 更新行为提示词
  update: async (promptId: string, data: Partial<BehaviorPrompt>) => {
    const response = await apiClient.put(`/behavior-prompts/${promptId}`, data);
    return response.data;
  },

  // 删除行为提示词
  delete: async (promptId: string) => {
    const response = await apiClient.delete(`/behavior-prompts/${promptId}`);
    return response.data;
  },
};
