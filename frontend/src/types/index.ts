// Task types
export interface Task {
  id: string;
  name: string;
  description: string;
  scenario_type: ScenarioType;
  status: TaskStatus;
  survey_id: string;
  agents: AgentConfig[];
  moderator: ModeratorConfig;
  settings: TaskSettings;
  agent_count?: number;
  progress?: { current: number; total: number; answered?: number };
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface TaskCreate {
  name: string;
  description?: string;
  scenario_type: ScenarioType;
  survey_id: string;
  agents: AgentConfig[];
  moderator?: ModeratorConfig;
  settings?: TaskSettings;
}

export interface AgentConfig {
  id: string;
  name: string;
  persona_id: string;
  provider_pack: string;
  model: string;
  behavior_prompt_id: string;
  memory_config?: MemoryConfig;
  thinking_enabled?: boolean;
  thinking_intensity?: string;
}

export interface ModeratorConfig {
  type: "ai" | "human";
  provider_pack?: string;
  model?: string;
  behavior_prompt_id: string;
  human_name?: string;
  thinking_enabled?: boolean;
  thinking_intensity?: string;
}

export interface MemoryConfig {
  history_size: number;
  max_anchors: number;
  enable_attitude_tracking: boolean;
}

export interface TaskSettings {
  default_visibility: Visibility;
  auto_follow_up: boolean;
  follow_up_threshold: number;
  max_follow_up_depth: number;
  delay_between_questions: number;
  memory_window_size: number;
}

export type TaskStatus = "pending" | "running" | "paused" | "completed" | "error" | "stopped";
export type ScenarioType = "survey" | "focus_group" | "idi" | "debate";
export type Visibility = "isolated" | "open";

// Survey types
export interface Survey {
  id: string;
  name: string;
  description: string;
  version: string;
  question_count?: number;
  questions?: Question[];
  scenario_type?: ScenarioType;
}

export interface SurveyCreate {
  name: string;
  description?: string;
  questions?: Question[];
  scenario_type?: ScenarioType;
}

export interface SurveyTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  questions: Question[];
  scenario_type?: ScenarioType;
}

export interface Question {
  id: string;
  type: QuestionType;
  text: string;
  options?: string[];
  scale_config?: ScaleConfig;
  required: boolean;
  mode: QuestionMode;
  visibility?: Visibility;
  follow_up_prompts?: FollowUpPrompt[];
}

export type QuestionType = "single_choice" | "multiple_choice" | "open_ended" | "scale" | "ranking";
export type QuestionMode = "global" | "sequential" | "open";

export interface ScaleConfig {
  min_value: number;
  max_value: number;
  min_label: string;
  max_label: string;
  step: number;
}

export interface FollowUpPrompt {
  condition: string;
  prompt: string;
}

// Persona types (Detail: nested fields from GET /:id)
export interface Persona {
  id: string;
  name: string;
  version: string;
  demographics: Demographics;
  psychographics: Psychographics;
  background: Background;
  initial_attitudes: Record<string, string>;
  groups?: string[];
}

// PersonaSummary: flat fields from GET / list API
export interface PersonaSummary {
  id: string;
  name: string;
  age: number;
  gender: string;
  occupation: string;
  city: string;
  groups?: string[];
}

export interface PersonaCreate {
  name: string;
  demographics: Demographics;
  psychographics?: Psychographics;
  background?: Background;
  initial_attitudes?: Record<string, string>;
}

export interface PersonaTemplate {
  id: string;
  name: string;
  emoji: string;
  description: string;
  demographics: Demographics;
  psychographics: Psychographics;
  background: Background;
  initial_attitudes: Record<string, string>;
}

// Persona Group types
export interface PersonaGroup {
  id: string;
  name: string;
  description: string;
  persona_ids: string[];
  created_at: string;
}

export interface PersonaGroupCreate {
  name: string;
  description?: string;
  persona_ids?: string[];
}

export interface Demographics {
  age: number;
  gender: string;
  city: string;
  education: string;
  occupation: string;
  income?: string;
  marital_status?: string;
  has_children?: boolean;
}

export interface Psychographics {
  values: string[];
  personality_traits: string[];
  risk_appetite: string;
  tech_savviness: string;
}

export interface Background {
  life_story: string;
  key_experiences: string[];
  current_concerns: string[];
  daily_routine?: string;
}

// Message types
export interface WSMessage {
  type: string;
}

export interface AgentResponseMessage extends WSMessage {
  type: "agent_response";
  agent_id: string;
  agent_name: string;
  content: string;
  emotion: string;
  emotion_intensity: number;
  timestamp: string;
  score?: number;
}

export interface AgentStateMessage extends WSMessage {
  type: "agent_state";
  agent_id: string;
  state: "idle" | "thinking" | "responding" | "error";
  emotion: string;
  progress?: {
    current: number;
    total: number;
  };
}

export interface SystemEventMessage extends WSMessage {
  type: "system_event";
  event: string;
  data: Record<string, any>;
}

export interface ModeratorCommandMessage extends WSMessage {
  type: "moderator_command";
  command: "ask_question" | "follow_up" | "skip" | "change_visibility" | "end"
    | "next_question" | "moderator_opening" | "moderator_guidance" | "moderator_summary" | "moderator_decision";
  target?: string;
  question?: string;
  content?: string;
  visibility?: Visibility;
  index?: number;
}

export interface ModeratorTakeoverMessage extends WSMessage {
  type: "moderator_takeover";
  action: "takeover" | "release";
  human_name?: string;
}

// Provider types
export interface Provider {
  name: string;
  base_url: string;
  default_model: string;
  models: ModelInfo[];
  api_params?: Record<string, any>;
  thinking_config?: ThinkingConfig;
  configured?: boolean;
}

export interface ThinkingConfig {
  mode: "toggle" | "effort" | "effort_only" | "none";
  toggle_key?: string;
  toggle_value?: string;
  effort_key?: string;
  effort_values: string[];
  effort_off_value?: string;
  restrictions?: Record<string, any>;
}

export interface ModelInfo {
  id: string;
  name: string;
  max_tokens: number;
  supports_thinking?: boolean;
  default_thinking?: boolean;
}

// Behavior Prompt types
export interface BehaviorPrompt {
  id: string;
  name: string;
  description: string;
  prompt: string;
}

// Agent State
export interface AgentState {
  id: string;
  name: string;
  state: "idle" | "thinking" | "responding" | "error";
  emotion: string;
  emotion_intensity: number;
}

// Session Status
export interface SessionStatus {
  task_id: string;
  status: TaskStatus;
  agents: Record<string, AgentState>;
  progress: {
    current: number;
    total: number;
  };
}

// ===== Result types =====
export interface TaskResult {
  task_id: string;
  status: string;
  scenario_type: string;
  total_questions: number;
  total_responses: number;
  total_follow_ups: number;
  avg_response_length: number;
  emotion_distribution: Record<string, number>;
  question_results: QuestionResult[];
  survey_feedback: SurveyFeedback[];
  agents: AgentInfo[];
  summary: string;
}

export interface AgentInfo {
  agent_id: string;
  agent_name: string;
  persona_id: string;
  persona_name: string;
  occupation: string;
  provider_pack: string;
  model: string;
  behavior_prompt_id: string;
  thinking_enabled: boolean;
  thinking_intensity: string;
}

export interface SurveyFeedback {
  agent_id: string;
  agent_name: string;
  length_rating: number;
  difficulty_rating: number;
  clarity_rating: number;
  fatigue_rating: number;
  interest_rating: number;
  comment: string;
}

export interface QuestionResult {
  question_id: string;
  question_text: string;
  responses: ResponseItem[];
  follow_ups: FollowUpItem[];
  ai_summary?: string;
}

export interface ResponseItem {
  agent_id: string;
  agent_name: string;
  content: string;
  emotion: string;
  emotion_intensity: number;
  score?: number;
  timestamp: string;
}

export interface FollowUpItem {
  question: string;
  response: ResponseItem | null;
  depth: number;
}
