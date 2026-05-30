import apiClient from "./client";
import type { PersonaCreate, PersonaGroup, PersonaGroupCreate } from "@/types";

export const personasApi = {
  // 创建Persona
  create: async (data: PersonaCreate) => {
    const response = await apiClient.post("/personas", data);
    return response.data;
  },

  // 获取Persona列表
  list: async () => {
    const response = await apiClient.get("/personas");
    return response.data;
  },

  // 获取Persona模板列表
  listTemplates: async () => {
    const response = await apiClient.get("/personas/templates");
    return response.data;
  },

  // 获取Persona详情
  get: async (personaId: string) => {
    const response = await apiClient.get(`/personas/${personaId}`);
    return response.data;
  },

  // 更新Persona
  update: async (personaId: string, data: Partial<PersonaCreate>) => {
    const response = await apiClient.put(`/personas/${personaId}`, data);
    return response.data;
  },

  // 删除Persona
  delete: async (personaId: string) => {
    const response = await apiClient.delete(`/personas/${personaId}`);
    return response.data;
  },

  // LLM优化Persona
  optimize: async (data: { template_id?: string; persona_id?: string; target_description: string; provider_pack?: string; model?: string }) => {
    const baseId = data.persona_id || data.template_id || "optimize";
    const response = await apiClient.post(`/personas/${baseId}/optimize`, data);
    return response.data;
  },

  // LLM生成Persona
  generate: async (data: { description: string; count?: number }) => {
    const response = await apiClient.post("/personas/generate", data);
    return response.data;
  },

  // 从模板创建
  fromTemplate: async (templateId: string) => {
    const response = await apiClient.post(`/personas/from-template/${templateId}`);
    return response.data;
  },

  // ===== 分组管理 =====

  // 获取所有分组
  listGroups: async () => {
    const response = await apiClient.get("/personas/groups");
    return response.data as PersonaGroup[];
  },

  // 创建分组
  createGroup: async (data: PersonaGroupCreate) => {
    const response = await apiClient.post("/personas/groups", data);
    return response.data as PersonaGroup;
  },

  // 更新分组
  updateGroup: async (groupId: string, data: Partial<PersonaGroupCreate>) => {
    const response = await apiClient.put(`/personas/groups/${groupId}`, data);
    return response.data as PersonaGroup;
  },

  // 删除分组
  deleteGroup: async (groupId: string) => {
    const response = await apiClient.delete(`/personas/groups/${groupId}`);
    return response.data;
  },

  // 获取分组内的Persona
  getGroupPersonas: async (groupId: string) => {
    const response = await apiClient.get(`/personas/groups/${groupId}/personas`);
    return response.data;
  },
};
