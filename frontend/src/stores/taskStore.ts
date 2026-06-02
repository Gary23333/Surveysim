import { create } from "zustand";
import type { Task, TaskCreate, SessionStatus, TaskResult } from "@/types";
import { tasksApi } from "@/api/tasks";

interface TaskStore {
  tasks: Task[];
  currentTask: Task | null;
  sessionStatus: SessionStatus | null;
  results: TaskResult | null;
  loading: boolean;
  error: string | null;

  fetchTasks: () => Promise<void>;
  fetchTask: (taskId: string) => Promise<void>;
  createTask: (data: TaskCreate) => Promise<Task>;
  startTask: (taskId: string) => Promise<void>;
  pauseTask: (taskId: string) => Promise<void>;
  resumeTask: (taskId: string) => Promise<void>;
  stopTask: (taskId: string) => Promise<void>;
  deleteTask: (taskId: string) => Promise<void>;
  fetchStatus: (taskId: string) => Promise<void>;
  fetchResults: (taskId: string) => Promise<void>;
  applySummaries: (summaries: Record<string, string>) => void;
  setCurrentTask: (task: Task | null) => void;
  clearError: () => void;
}

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  currentTask: null,
  sessionStatus: null,
  results: null,
  loading: false,
  error: null,

  fetchTasks: async () => {
    set({ loading: true, error: null });
    try { const tasks = await tasksApi.list(); set({ tasks, loading: false }); }
    catch (error: any) { set({ error: error.message, loading: false }); }
  },
  fetchTask: async (taskId: string) => {
    set({ loading: true, error: null });
    try { const task = await tasksApi.get(taskId); set({ currentTask: task, loading: false }); }
    catch (error: any) { set({ error: error.message, loading: false }); }
  },
  createTask: async (data: TaskCreate) => {
    set({ loading: true, error: null });
    try {
      const result = await tasksApi.create(data);
      const task = await tasksApi.get(result.id);
      set((state) => ({ tasks: [...state.tasks, task], loading: false }));
      return task;
    } catch (error: any) { set({ error: error.message, loading: false }); throw error; }
  },
  startTask: async (taskId: string) => { try { await tasksApi.start(taskId); await get().fetchStatus(taskId); } catch (error: any) { set({ error: error.message }); } },
  pauseTask: async (taskId: string) => { try { await tasksApi.pause(taskId); await get().fetchStatus(taskId); } catch (error: any) { set({ error: error.message }); } },
  resumeTask: async (taskId: string) => { try { await tasksApi.resume(taskId); await get().fetchStatus(taskId); } catch (error: any) { set({ error: error.message }); } },
  stopTask: async (taskId: string) => { try { await tasksApi.stop(taskId); await get().fetchStatus(taskId); } catch (error: any) { set({ error: error.message }); } },
  deleteTask: async (taskId: string) => {
    try {
      await tasksApi.delete(taskId);
      set((state) => ({ tasks: state.tasks.filter((t) => t.id !== taskId), currentTask: state.currentTask?.id === taskId ? null : state.currentTask }));
    } catch (error: any) { set({ error: error.message }); }
  },
  fetchStatus: async (taskId: string) => { try { const status = await tasksApi.getStatus(taskId); set({ sessionStatus: status }); } catch (error: any) { console.error("Failed to fetch status:", error); } },
  fetchResults: async (taskId: string) => { set({ loading: true }); try { const results = await tasksApi.getResults(taskId); set({ results, loading: false }); } catch (error: any) { set({ error: error.message, loading: false }); } },
  applySummaries: (summaries: Record<string, string>) => {
    const { results } = get();
    if (!results) return;
    const updatedResults = {
      ...results,
      question_results: results.question_results.map(qr => ({
        ...qr,
        ai_summary: summaries[qr.question_id] || qr.ai_summary,
      })),
    };
    set({ results: updatedResults });
  },
  setCurrentTask: (task: Task | null) => { set({ currentTask: task }); },
  clearError: () => { set({ error: null }); },
}));
