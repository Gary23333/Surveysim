# SurveySim — 大模型模拟问卷调查平台

## 项目定位

SurveySim 是一个**大模型驱动的模拟问卷调查与群体调研平台**。通过配置多个具有不同人格（Persona）的 AI Agent，模拟真实人类受访者参与问卷调查或焦点小组讨论，用于**预评价问卷设计效果**、**测试问题理解度**、**发现潜在偏见**、**探索群体互动动态**。

---

## 核心概念

### 1. 三层人格架构

每个 Respondent Agent 由三层信息构成运行时人格：

```
┌──────────────────────────────────────────────┐
│  Layer 3: 运行时 System Prompt（行为指令层）    │
│  • 全局回答风格（如实/详细/简洁）               │
│  • 格式约束（JSON/自然语言）                   │
│  • 禁止事项（不迎合、不编造、不猜测调查者意图）  │
├──────────────────────────────────────────────┤
│  Layer 2: Persona 档案（人格层）                │
│  • Demographics（人口统计：年龄/性别/城市/收入） │
│  • Psychographics（心理画像：价值观/风险偏好）   │
│  • Background（背景故事：教育/职业/家庭/经历）   │
├──────────────────────────────────────────────┤
│  Layer 1: Persona 模板（生成规则层）             │
│  • 如何从人口数据批量合成 persona               │
│  • 预设人群模板（一线城市白领/小镇青年等）        │
└──────────────────────────────────────────────┘
```

**设计原则**：
- Layer 1 对普通用户隐藏，专家用户可自定义
- Layer 2 可手动配置或从模板批量生成
- Layer 3 与 Layer 2 分离，支持同一 persona 配不同行为指令做 A/B 测试

### 2. 记忆机制（Memory）

每个 Agent 拥有三层记忆，确保回答连贯性：

| 记忆类型 | 作用 | 存储内容 |
|---------|------|---------|
| **对话历史** | 保持上下文连贯 | 最近 N 轮问答（可配置） |
| **态度状态** | 追踪立场演化 | 对关键话题的立场变化时间线 |
| **经历锚点** | 具体事实引用 | 提到过的具体事件、数字、时间 |

**记忆注入方式**：在每次调用 LLM 前，将记忆以自然语言形式拼接到 system prompt 中。

**态度演化规则**：
- 初始态度来自 persona 心理画像
- 每轮回答后，LLM 提取态度变化 → 更新 attitude_state
- 递进式问题可引用之前态度："你刚才表示谨慎乐观，那如果..."

### 3. 主持人工作流（四种提问模式）

```
┌─────────────────────────────────────────────────────────────┐
│  Mode 1: 全局提问 (GlobalQuestion)                           │
│  主持人向所有 agent 同时提出同一问题                          │
│  ├─ visibility: isolated  → 各 agent 独立回答，互不可见       │
│  └─ visibility: open      → agent 可以看到其他人的答案        │
├─────────────────────────────────────────────────────────────┤
│  Mode 2: 顺序提问 (SequentialQuestion)                       │
│  主持人按顺序逐个向 agent 提问同一问题                        │
│  ├─ visibility: isolated  → 每个 agent 只看到自己的问答       │
│  └─ visibility: open      → 后续 agent 可以看到前面人的答案   │
├─────────────────────────────────────────────────────────────┤
│  Mode 3: 开放场景 (OpenScene)                                │
│  主持人设定场景，所有 agent 自由参与讨论                      │
│  （天然 open，无 isolated 模式）                              │
├─────────────────────────────────────────────────────────────┤
│  Mode 4: 追问 (FollowUp) — 自动或手动触发                     │
│  针对某个 agent 的特定回答进行深度追问                        │
│  （总是 isolated，一对一）                                    │
└─────────────────────────────────────────────────────────────┘
```

**追问触发条件**：
- 回答长度低于阈值
- 检测到矛盾（与之前态度冲突）
- 检测到模糊（"还行"、"一般"）
- 检测到异常（与 persona 背景不符）
- 人类主持人手动触发

### 4. 可见性控制（Visibility）

```python
class Visibility(Enum):
    ISOLATED = "isolated"   # 只能看到自己和主持人的对话
    OPEN = "open"           # 可以看到所有参与者的对话、状态、情绪
```

**对话历史过滤逻辑**：
- `isolated`：只保留系统消息 + 主持人消息 + 该 agent 自己的消息
- `open`：全部可见，包括其他 agent 的回答、状态、情绪

### 5. Agent 状态与情绪广播

每个 Agent 回答时，系统要求 LLM 同时输出：

```json
{
  "content": "回答内容",
  "emotion": "谨慎好奇",
  "emotion_intensity": 0.7,
  "state": "responding"
}
```

**广播范围**：
- Dashboard 前端（实时可视化）
- 其他 Agent（在 Open 模式下注入 prompt）

**Agent 感知其他 Agent 的 prompt 注入示例**：
```
【其他参与者的状态】
- 张小花: 情绪=兴奋(0.8)，刚表示"AI能提高工作效率"
- 李明: 情绪=谨慎(0.6)，提到"担心隐私问题"

你可以参考他们的观点，但请保持你自己的立场。
```

### 6. LLM 配置包（ProviderPack）

```
ProviderPack（配置包）
├── name: "我的 OpenAI 账号"
├── base_url: "https://api.openai.com/v1"
├── api_key: "sk-..."
├── default_model: "gpt-4o"
└── models: [
      {"id": "gpt-4o", "name": "GPT-4o", "max_tokens": 4096},
      {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "max_tokens": 4096}
    ]
```

**Agent 选择时**：`provider_pack`（一级）+ `model`（二级）

**支持环境变量**：`api_key: "${OPENAI_API_KEY}"`

---

## 系统架构

### 前后端分离

```
┌─────────────────────────────────────────────────────────────┐
│                      前端 (Frontend)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │  Dashboard  │ │ 任务创建/配置 │ │     任务历史        │   │
│  │  实时调研看板 │ │  (React/Vue) │ │   (历史回放)        │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
│         ↑ WebSocket (实时状态/情绪/对话流)                    │
└─────────┼───────────────────────────────────────────────────┘
          │ HTTP API (配置/任务管理)
┌─────────┼───────────────────────────────────────────────────┐
│         ↓                                                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              后端 API 层 (FastAPI)                       │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │ │
│  │  │ /tasks   │ │ /agents  │ │ /surveys │ │ /config  │   │ │
│  │  │ 任务CRUD  │ │ Agent管理│ │ 问卷管理 │ │ 配置管理 │   │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │ │
│  │  ┌─────────────────────────────────────────────────┐   │ │
│  │  │  /ws/sessions/{id}  WebSocket 实时调研流         │   │ │
│  │  │  • Agent 回答推送                                │   │ │
│  │  │  • Agent 状态/情绪广播                           │   │ │
│  │  │  • 人类主持人指令接收                            │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
│         ↓                                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              核心引擎 (Core Engine)                      │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │ │
│  │  │ Session  │ │ Moderator│ │Respondent│ │  Memory  │   │ │
│  │  │ 会话管理  │ │ 主持人   │ │ 受访者   │ │ 记忆管理 │   │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐   │ │
│  │  │ 提问模式 │ │ 可见性   │ │ 状态/情绪广播系统     │   │ │
│  │  │ 调度器   │ │ 过滤器   │ │ (Agent 互相感知)      │   │ │
│  │  └──────────┘ └──────────┘ └──────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
│         ↓                                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              LLM 适配层 (Provider Layer)                 │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐          │ │
│  │  │ OpenAI │ │  Kimi  │ │DeepSeek│ │ 更多... │          │ │
│  │  └────────┘ └────────┘ └────────┘ └────────┘          │ │
│  └─────────────────────────────────────────────────────────┘ │
│         ↓                                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              数据层 (Storage)                            │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐               │ │
│  │  │ SQLite/  │ │  Config  │ │  Task    │               │ │
│  │  │ PostgreSQL│ │  Files   │ │  History │               │ │
│  │  │ (任务数据)│ │ (YAML)   │ │ (归档)   │               │ │
│  │  └──────────┘ └──────────┘ └──────────┘               │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 全部配置存储在后端

- LLM ProviderPack 配置 → `backend/configs/providers/*.yaml`
- Persona 配置 → `backend/configs/personas/*.yaml`
- 问卷配置 → `backend/configs/surveys/*.yaml`
- 行为提示词模板 → `backend/configs/behavior_prompts/*.yaml`
- 任务历史 → SQLite/PostgreSQL

---

## API 设计

### REST API

```http
# 任务管理
POST   /api/v1/tasks              # 创建任务
GET    /api/v1/tasks              # 任务列表（支持分页/筛选）
GET    /api/v1/tasks/{id}         # 任务详情
POST   /api/v1/tasks/{id}/start   # 启动任务
POST   /api/v1/tasks/{id}/pause   # 暂停任务
POST   /api/v1/tasks/{id}/stop    # 停止任务
POST   /api/v1/tasks/{id}/clone   # 克隆任务
DELETE /api/v1/tasks/{id}         # 删除任务

# 配置管理
GET    /api/v1/config/providers          # LLM 配置包列表
POST   /api/v1/config/providers          # 新增配置包
PUT    /api/v1/config/providers/{name}   # 更新配置包
DELETE /api/v1/config/providers/{name}   # 删除配置包
GET    /api/v1/config/providers/{name}/models  # 获取配置包支持的模型列表

GET    /api/v1/config/personas           # Persona 列表
POST   /api/v1/config/personas           # 新增 Persona
PUT    /api/v1/config/personas/{id}      # 更新 Persona
DELETE /api/v1/config/personas/{id}      # 删除 Persona

GET    /api/v1/config/surveys            # 问卷列表
POST   /api/v1/config/surveys            # 新增问卷
# ... 同理

# 结果分析
GET    /api/v1/tasks/{id}/results        # 获取任务结果
GET    /api/v1/tasks/{id}/analysis       # 获取分析报告
GET    /api/v1/tasks/{id}/export         # 导出结果（CSV/JSON）
```

### WebSocket API

```http
WS /ws/sessions/{session_id}
```

**消息协议**：

```typescript
// Server → Client: Agent 回答
interface AgentResponseMessage {
  type: "agent_response";
  agent_id: string;
  agent_name: string;
  content: string;
  emotion: string;
  emotion_intensity: number;
  timestamp: string;
  question_id?: string;
}

// Server → Client: Agent 状态更新
interface AgentStateMessage {
  type: "agent_state";
  agent_id: string;
  state: "idle" | "thinking" | "responding" | "error";
  emotion: string;
  progress: {
    current_question: number;
    total_questions: number;
  };
}

// Server → Client: 情绪广播
interface EmotionBroadcastMessage {
  type: "emotion_broadcast";
  agent_id: string;
  agent_name: string;
  emotion: string;
  intensity: number;
  context: string;
  timestamp: string;
}

// Server → Client: 系统事件
interface SystemEventMessage {
  type: "system_event";
  event: "session_started" | "session_paused" | "session_ended" | "question_changed" | "moderator_switched";
  data: Record<string, any>;
}

// Client → Server: 人类主持人指令
interface ModeratorCommandMessage {
  type: "moderator_command";
  command: "ask_question" | "follow_up" | "skip_question" | "change_visibility" | "end_session";
  target?: string;        // agent_id，空=全部
  question?: string;      // 问题内容
  visibility?: "isolated" | "open";
}

// Client → Server: 接管/交回主持人
interface ModeratorTakeoverMessage {
  type: "moderator_takeover";
  action: "takeover" | "release";
  human_name?: string;    // 人类主持人名字
}
```

---

## 人类主持人模式

### 模式切换

```
AI 主持人 ←──[接管按钮]──→ 人类主持人
```

**接管流程**：
1. 前端点击"接管主持人"
2. AI 主持人暂停，保存完整上下文
3. 广播 `moderator_switched` 事件
4. 前端显示"人类主持人：{name}"
5. 人类通过 WebSocket 发送指令控制流程

**人类主持人能力**：
- 手动提问（指定 agent 或全部）
- 触发追问（针对特定回答）
- 跳过当前问题
- 修改 agent 可见性（isolated/open）
- 实时查看所有 agent 的记忆和态度状态
- 随时交回给 AI 主持人

**AI 主持人恢复**：
- 人类点击"交回 AI"
- 系统恢复保存的上下文
- AI 主持人从断点继续

---

## 数据模型

### Task（任务）

```python
class Task(BaseModel):
    id: str                    # UUID
    name: str                  # 任务名称
    description: str           # 任务描述
    status: TaskStatus         # pending | running | paused | completed | error
    
    # 问卷配置
    survey_id: str             # 关联问卷
    
    # Agent 配置
    agents: list[AgentConfig]  # 参与的 agent 列表
    
    # 主持人配置
    moderator: ModeratorConfig # AI/人类主持人配置
    
    # 运行配置
    settings: TaskSettings     # 全局设置
    
    # 时间戳
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

class AgentConfig(BaseModel):
    id: str
    name: str                  # 显示名称
    persona_id: str            # 关联 persona
    provider_pack: str         # LLM 配置包名称
    model: str                 # 具体模型
    behavior_prompt_id: str    # 行为提示词模板
    memory_settings: MemorySettings

class ModeratorConfig(BaseModel):
    type: "ai" | "human"       # 主持人类型
    provider_pack: str | None  # AI 主持人用
    model: str | None          # AI 主持人用
    behavior_prompt_id: str    # 主持人行为提示词
    human_name: str | None     # 人类主持人用

class TaskSettings(BaseModel):
    default_visibility: Visibility
    auto_follow_up: bool       # 是否自动追问
    follow_up_threshold: int   # 回答长度阈值
    max_follow_up_depth: int   # 最大追问深度
    delay_between_questions: float  # 问题间隔（秒）
    memory_window_size: int    # 记忆窗口大小
```

### Persona（人格档案）

```python
class Persona(BaseModel):
    id: str
    name: str                  # 人格名称
    version: str               # 版本号
    
    # 人口统计
    demographics: Demographics
    
    # 心理画像
    psychographics: Psychographics
    
    # 背景故事
    background: Background
    
    # 初始态度（用于初始化 attitude_state）
    initial_attitudes: dict[str, str]

class Demographics(BaseModel):
    age: int | range           # 年龄或年龄范围
    gender: str
    city: str                  # 居住城市
    education: str             # 教育水平
    occupation: str            # 职业
    income: str | range        # 年收入范围
    marital_status: str        # 婚姻状况
    has_children: bool | None
    
class Psychographics(BaseModel):
    values: list[str]          # 核心价值观
    personality_traits: list[str]  # 性格特征（大五人格等）
    risk_appetite: str         # 风险偏好
    tech_savviness: str        # 科技接受度
    political_leaning: str | None  # 政治倾向
    
class Background(BaseModel):
    life_story: str            # 生平简述
    key_experiences: list[str] # 关键经历
    current_concerns: list[str]  # 当前关注
    daily_routine: str | None  # 日常生活
```

### Survey（问卷）

```python
class Survey(BaseModel):
    id: str
    name: str
    description: str
    questions: list[Question]
    
class Question(BaseModel):
    id: str
    type: QuestionType         # single_choice | multiple_choice | open_ended | scale | ranking
    text: str                  # 问题文本
    options: list[str] | None  # 选项（选择题）
    scale: ScaleConfig | None  # 量表配置
    follow_up_prompts: list[FollowUpPrompt]  # 预设追问
    required: bool
    
class FollowUpPrompt(BaseModel):
    condition: str             # 触发条件（如 "answer.length < 20"）
    prompt: str                # 追问文本
```

---

## 核心引擎工作流

### 任务启动流程

```
1. 加载任务配置（问卷 + Agent 列表 + 主持人配置）
2. 初始化每个 Agent：
   a. 加载 Persona
   b. 初始化 Memory（空历史 + 初始态度）
   c. 初始化 LLM Provider
   d. 构建初始 System Prompt
3. 初始化主持人（AI 或等待人类接管）
4. 建立 WebSocket 连接，广播 session_started
5. 主持人开场白 → 逐题执行
```

### 单题执行流程（Global + Isolated 示例）

```
1. 主持人生成问题文本
2. 对每个 Agent（并行）：
   a. 根据 visibility 过滤对话历史
   b. 拼接 System Prompt + Memory + 当前问题
   c. 调用 LLM（要求输出 content + emotion + state）
   d. 解析响应，更新 Agent Memory
   e. 通过 WebSocket 广播 agent_response + agent_state
3. 主持人评估是否需要追问
4. 如需追问，进入 FollowUp 模式
5. 广播 question_changed，进入下一题
```

### 开放场景执行流程

```
1. 主持人设定场景和初始话题
2. 所有 Agent 同时收到场景描述（OPEN 模式）
3. Agent 自由响应（带情绪/状态）
4. 其他 Agent 在下一轮可以看到之前的响应
5. 主持人可介入引导方向
6. 达到结束条件（时间/轮数/话题枯竭）后总结
```

---

## 提示词模板

### Respondent Agent System Prompt 模板

```markdown
# 角色设定

你是 {persona.name}，{persona.demographics.age}岁，{persona.demographics.gender}性，
居住在{persona.demographics.city}，职业是{persona.demographics.occupation}。

## 背景

{persona.background.life_story}

## 性格与价值观

- 核心价值观：{persona.psychographics.values}
- 性格特征：{persona.psychographics.personality_traits}
- 风险偏好：{persona.psychographics.risk_appetite}

## 记忆

{memory.experience_anchors}

## 当前态度

{memory.attitude_state}

## 近期对话

{memory.conversation_history}

---

# 行为指令

{behavior_prompt}

---

# 当前场景

{survey_context}

{other_agents_state}  # 仅在 OPEN 模式下包含

---

# 输出格式

请以 JSON 格式输出：
{{
  "content": "你的回答内容",
  "emotion": "当前情绪（如：兴奋、谨慎、困惑）",
  "emotion_intensity": 0.0-1.0,
  "state": "responding"
}}
```

### AI 主持人 System Prompt 模板

```markdown
# 角色设定

你是一位专业的问卷调查主持人。你的职责是：
1. 引导受访者完成问卷
2. 在必要时进行追问
3. 确保回答质量
4. 控制调查节奏

## 行为准则

- 语言自然，不机械读题
- 追问有针对性，不重复
- 尊重受访者，不引导答案
- 发现矛盾时温和指出

## 当前任务

问卷：{survey.name}
当前进度：{progress.current}/{progress.total}
当前模式：{mode}（{visibility}）

## 受访者信息

{agents_summary}

---

# 输出格式

{{
  "action": "ask|follow_up|skip|end",
  "target": "agent_id 或 all",
  "content": "主持人说的话",
  "reason": "决策理由"
}}
```

### 行为提示词模板示例（如实回答）

```markdown
## 回答要求

1. **如实回答**：基于你的真实经历和想法，不要猜测调查者想要的答案
2. **具体详细**：用具体例子支撑观点，避免"还行"、"一般"等模糊回答
3. **保持立场**：即使与其他人观点不同，也要坚持自己的想法
4. **不编造**：不知道就说不了解，不要虚构经历
5. **自然表达**：像日常对话一样，不需要过于正式
```

---

## 前端页面设计

### 1. Dashboard（实时调研看板）

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│  顶部：任务信息 + 进度条 + 控制按钮（暂停/停止/接管）      │
├─────────────────────────────────────────────────────────┤
│  左侧：Agent 列表（头像+名字+状态+情绪）                   │
│       点击展开：人口信息 + 当前态度 + 记忆摘要              │
├─────────────────────────────────────────────────────────┤
│  中间：对话流（时间线形式）                                │
│       • 主持人消息（蓝色）                                 │
│       • Agent 回答（彩色气泡，带情绪标签）                  │
│       • 系统事件（灰色）                                   │
├─────────────────────────────────────────────────────────┤
│  右侧：实时统计                                            │
│       • 当前问题                                          │
│       • 回答分布（选择题）或词云（开放题）                   │
│       • 情绪热力图                                         │
└─────────────────────────────────────────────────────────┘
```

**交互**：
- 实时滚动对话流
- 点击 Agent 查看详情
- 人类主持人模式下显示输入框
- 支持倍速回放历史任务

### 2. 任务创建向导

**步骤**：
1. **基本信息**：任务名称、描述
2. **选择问卷**：从已有问卷选择或新建
3. **配置 Agent**：
   - 数量（2-15）
   - 每个 Agent：选择/创建 Persona + ProviderPack + 模型 + 行为提示词
   - 支持"随机生成 persona"快捷按钮
4. **主持人设置**：AI/人类 + 配置
5. **运行设置**：可见性默认、自动追问、间隔时间等
6. **预览确认**：显示完整配置，可保存为模板

### 3. 任务历史

**列表视图**：
- 任务名称、状态、创建时间、完成时间
- Agent 数量、问卷名称
- 快捷操作：查看结果、重新运行、克隆、删除

**详情视图**：
- 完整对话回放（带时间轴拖动）
- 结果统计图表
- 导出选项

### 4. 配置管理页面

**ProviderPack 管理**：
- 列表：名称、base_url、模型数量、状态
- 测试连接按钮
- 新增/编辑/删除

**Persona 管理**：
- 列表：名称、人口标签、版本
- 编辑器：表单形式编辑各字段
- 预览：查看生成的 system prompt

**问卷管理**：
- 列表：名称、题数、类型
- 编辑器：拖拽式题目编辑
- 导入：支持问卷星/腾讯问卷格式

---

## 技术栈

### 后端
- **框架**：FastAPI + asyncio
- **数据库**：SQLite（开发）/ PostgreSQL（生产）
- **ORM**：SQLModel / SQLAlchemy
- **WebSocket**：原生 FastAPI WebSocket
- **LLM 调用**：httpx（异步 HTTP）+ 各供应商 SDK
- **配置存储**：YAML 文件 + 数据库
- **任务队列**：asyncio Queue（MVP）/ Celery（扩展）

### 前端
- **框架**：React 18 + TypeScript
- **构建**：Vite
- **状态管理**：Zustand
- **UI 组件**：Ant Design / shadcn/ui
- **实时通信**：原生 WebSocket
- **图表**：ECharts / D3.js

### 部署
- **后端**：uvicorn + gunicorn
- **前端**：nginx 静态托管
- **容器**：Docker + Docker Compose

---

## 项目结构

```
surveysim/
├── backend/
│   ├── surveysim/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py
│   │   │   ├── config.py
│   │   │   └── websocket.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   ├── session.py
│   │   │   ├── moderator.py
│   │   │   └── respondent.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── task.py
│   │   │   ├── persona.py
│   │   │   ├── survey.py
│   │   │   └── message.py
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── store.py
│   │   │   └── attitude.py
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── provider.py
│   │   │   ├── pack.py
│   │   │   └── adapters/
│   │   │       ├── openai.py
│   │   │       ├── kimi.py
│   │   │       └── deepseek.py
│   │   └── storage/
│   │       ├── __init__.py
│   │       ├── database.py
│   │       └── config_store.py
│   ├── configs/
│   │   ├── providers/
│   │   ├── personas/
│   │   ├── surveys/
│   │   └── behavior_prompts/
│   ├── main.py
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   ├── TaskCreator/
│   │   │   ├── TaskHistory/
│   │   │   ├── AgentConfig/
│   │   │   └── Common/
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── TaskCreatePage.tsx
│   │   │   ├── TaskHistoryPage.tsx
│   │   │   └── ConfigPage.tsx
│   │   ├── stores/
│   │   │   ├── taskStore.ts
│   │   │   ├── configStore.ts
│   │   │   └── websocketStore.ts
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── tasks.ts
│   │   │   └── config.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── examples/
│   └── demo_survey.py
│
├── docs/
│   └── api.md
│
└── README.md
```

---

## 开发里程碑

### MVP（最小可用产品）
- [ ] 后端：FastAPI 骨架 + SQLite + 核心引擎
- [ ] 后端：OpenAI/Kimi/DeepSeek 适配器
- [ ] 后端：AI 主持人（Global + Sequential 模式）
- [ ] 后端：WebSocket 实时推送
- [ ] 前端：Dashboard 基础版（对话流 + Agent 状态）
- [ ] 前端：任务创建表单
- [ ] 端到端测试：3 Agent + 5 题问卷

### v0.2
- [ ] 开放场景模式
- [ ] 人类主持人接管
- [ ] 追问机制（自动 + 手动）
- [ ] Agent 状态/情绪广播
- [ ] 任务历史 + 回放

### v0.3
- [ ] Persona 模板库
- [ ] 问卷导入（问卷星/腾讯问卷）
- [ ] 结果分析（统计图表 + 偏见检测）
- [ ] 多语言支持

### v1.0
- [ ] 完整的配置管理 UI
- [ ] 用户认证与权限
- [ ] PostgreSQL 支持
- [ ] Docker 部署
- [ ] 文档与示例

---

## 命名规范

- **项目名**：SurveySim
- **模块名**：snake_case（`respondent.py`）
- **类名**：PascalCase（`RespondentAgent`）
- **函数名**：snake_case（`ask_question`）
- **常量**：UPPER_SNAKE_CASE
- **API 路径**：kebab-case（`/api/v1/tasks`）
- **配置文件名**：kebab-case（`openai-production.yaml`）

---

## 关键设计决策记录

1. **Persona 与 System Prompt 分离**：支持 A/B 测试和批量生成
2. **记忆三层设计**：对话历史 + 态度状态 + 经历锚点，确保连贯性
3. **四种提问模式**：覆盖问卷和焦点小组两种场景
4. **可见性独立配置**：isolated/open 可与任何模式组合
5. **LLM 配置包**：接入点+key+多模型，Agent 选择时两级配置
6. **全部配置存后端**：前端无状态，便于协作和版本管理
7. **WebSocket 实时流**：支持 Dashboard 和人类主持人模式
8. **Agent 状态/情绪广播**：群体调研中 agent 互相感知的基础
9. **人类主持人可接管**：AI 和人类无缝切换，保存完整上下文
10. **SQLite → PostgreSQL**：MVP 用 SQLite 降低门槛，生产可切换

---

*文档版本：v1.0*
*创建时间：2026-05-29*
*作者：SurveySim Team*
