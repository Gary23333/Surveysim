import { create } from "zustand";
import type { WSMessage, AgentResponseMessage, AgentStateMessage, SystemEventMessage } from "@/types";

interface WebSocketStore {
  connected: boolean;
  messages: WSMessage[];
  agentResponses: AgentResponseMessage[];
  agentStates: Record<string, AgentStateMessage>;
  systemEvents: SystemEventMessage[];

  // Actions
  setConnected: (connected: boolean) => void;
  addMessage: (message: WSMessage) => void;
  clearMessages: () => void;
  handleMessage: (message: WSMessage) => void;
}

export const useWebSocketStore = create<WebSocketStore>((set) => ({
  connected: false,
  messages: [],
  agentResponses: [],
  agentStates: {},
  systemEvents: [],

  setConnected: (connected: boolean) => {
    set({ connected });
  },

  addMessage: (message: WSMessage) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  clearMessages: () => {
    set({
      messages: [],
      agentResponses: [],
      agentStates: {},
      systemEvents: [],
    });
  },

  handleMessage: (message: WSMessage) => {
    const { type } = message;

    switch (type) {
      case "agent_response":
        const responseMsg = message as AgentResponseMessage;
        set((state) => ({
          agentResponses: [...state.agentResponses, responseMsg],
          messages: [...state.messages, message],
        }));
        break;

      case "agent_state":
        const stateMsg = message as AgentStateMessage;
        set((state) => ({
          agentStates: {
            ...state.agentStates,
            [stateMsg.agent_id]: stateMsg,
          },
          messages: [...state.messages, message],
        }));
        break;

      case "system_event":
        const eventMsg = message as SystemEventMessage;
        set((state) => ({
          systemEvents: [...state.systemEvents, eventMsg],
          messages: [...state.messages, message],
        }));
        break;

      default:
        set((state) => ({
          messages: [...state.messages, message],
        }));
    }
  },
}));
