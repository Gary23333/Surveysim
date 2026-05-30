import apiClient from "./client";
import type { SurveyCreate } from "@/types";

export const surveysApi = {
  // 创建问卷
  create: async (data: SurveyCreate) => {
    const response = await apiClient.post("/surveys", data);
    return response.data;
  },

  // 获取问卷列表
  list: async () => {
    const response = await apiClient.get("/surveys");
    return response.data;
  },

  // 获取问卷模板列表
  listTemplates: async () => {
    const response = await apiClient.get("/surveys/templates");
    return response.data;
  },

  // 获取问卷详情
  get: async (surveyId: string) => {
    const response = await apiClient.get(`/surveys/${surveyId}`);
    return response.data;
  },

  // 更新问卷
  update: async (surveyId: string, data: Partial<SurveyCreate>) => {
    const response = await apiClient.put(`/surveys/${surveyId}`, data);
    return response.data;
  },

  // 删除问卷
  delete: async (surveyId: string) => {
    const response = await apiClient.delete(`/surveys/${surveyId}`);
    return response.data;
  },

  // 导入问卷
  import: async (file: File, format: string = "auto") => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post("/surveys/import", formData, {
      params: { format },
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  // 导出问卷
  export: async (surveyId: string, format: string = "json") => {
    const response = await apiClient.get(`/surveys/${surveyId}/export`, {
      params: { format },
    });
    return response.data;
  },

  // 从模板创建
  fromTemplate: async (templateId: string) => {
    const response = await apiClient.post(`/surveys/from-template/${templateId}`);
    return response.data;
  },
};
