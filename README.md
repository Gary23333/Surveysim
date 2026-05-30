# Virtual Survey / 虚拟调研

大模型驱动的模拟问卷调查与群体调研平台

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 功能特性

### 核心功能
- **多种调研场景**：问卷调查、焦点小组、深度访谈、辩论讨论
- **AI人格系统**：三层人格架构（模板/档案/行为指令），支持自定义和LLM优化
- **记忆机制**：三层记忆系统（对话历史/态度状态/经历锚点），确保回答连贯性
- **实时监控**：WebSocket实时推送，Dashboard可视化
- **灵活配置**：支持多LLM供应商，可扩展架构

### 调研模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| 问卷调查 | 标准化问题收集 | 满意度调查、市场调研 |
| 焦点小组 | 多人自由讨论 | 产品体验、用户需求 |
| 深度访谈 | 一对一深入挖掘 | 用户研究、案例分析 |
| 辩论讨论 | 正反方观点碰撞 | 观点分析、决策支持 |

### 主持人系统
- **AI主持人**：自动生成开场白、评估回答、追问引导
- **人类主持人**：实时接管、手动提问、灵活控制
- **无缝切换**：AI/人类主持人随时切换

### 思考模式 (Thinking Mode) — v0.6.0 新增
- **多供应商支持**：MiMo / DeepSeek / 豆包(火山引擎) / OpenAI 四家供应商
- **智能适配**：各家不同的思考模式参数自动适配
  - **MiMo**：toggle 模式（纯开关），思考模式下自动覆写 temperature=1.0
  - **DeepSeek**：effort 模式（开关 + 强度），支持 `high`/`max` 两档
  - **豆包**：effort_only 模式（纯强度控制），`minimal`=关闭，`low`/`medium`/`high` 四档
- **任务级控制**：创建任务时为每个 Agent 独立配置思考开关和强度
- **预置 Provider**：一键选择预设供应商配置，或自定义

### 连通性测试 & 模型检测 — v0.6.0 新增
- **真实连通性测试**：向供应商 API 发送最小请求，返回延迟和状态
- **模型检测**：从供应商 `/models` 端点拉取可用模型列表
- **一键导入**：检测到的模型可一键导入到当前 Provider 配置
- **模型行编辑器**：可视化增删改模型，支持 per-model 思考模式标记

### 预设 Provider 配置
| Provider | Base URL | 预置模型 | 思考模式 |
|----------|----------|---------|----------|
| **MiMo** | `api.xiaomimimo.com/v1` | mimo-v2.5-pro, mimo-v2.5 | toggle |
| **DeepSeek** | `api.deepseek.com` | deepseek-v4-pro, deepseek-v4-flash | effort(high/max) |
| **豆包** | `ark.cn-beijing.volces.com/api/v3` | doubao-seed-2-0-pro/lite/mini | effort_only(minimal/low/medium/high) |
| **OpenAI** | `api.openai.com/v1` | gpt-4o, gpt-4o-mini, gpt-3.5-turbo | n/a |

### 数据管理
- JSON问卷导入导出
- 结果导出（JSON/CSV）
- 问卷星/腾讯问卷格式兼容
- 丰富的模板库

### 人格分组管理 — v0.8.0
- **分组CRUD**：创建/编辑/删除人格分组
- **多对多关系**：一个人格可属于多个分组，一个分组包含多个人格
- **分组筛选**：Badge 标签快速筛选分组下的人格
- **任务导入**：创建任务时可从分组一键导入全部成员

### 题目评分系统 — v0.7.0
- **程度评分**：题目支持 `enable_rating` + `rating_config`（1~10 分）
- **评分+文字可组合**：每题独立开关，两者同时开启则都必答
- **评分配置上传时设定**：创建问卷时即可配置哪些题需要评分及评分范围

### 结果查看 & 导出 — v0.8.0
- **完整结果页**：统计卡片 + 情绪分布图 + 评分一览 + 问卷反馈 + 逐题结果
- **参与者配置展示**：每位 Agent 的人格名、行为模式、LLM 供应商、模型、思考模式
- **结果导出**：JSON（完整数据）和 CSV（表格化）两种格式
- **任务完成通知**：Dashboard 和任务列表均可直接跳转结果页

### 问卷体验反馈 — v0.8.0
- **5 维度评分**：全部答题后 Agent 对问卷打分
  - 长度感知 / 回答难度 / 问题清晰度 / 疲劳感受 / 兴趣程度
- **可视化**：5 维度水平汇总条 + 各 Agent 散点 + 评语展示

### 人工主持人增强 — v0.8.0
- **接管/交回**：随时暂停 AI 自动流程，人工驱动当前题目
- **逐题控制**：人工主持人点击"开始本题"触发全体 Agent 回答
- **追问功能**：每位 Agent 回答旁提供追问输入框
- **群发提问**：自定义问题广播给全体参与者

### 题库编辑器 — v0.8.0
- **完整题目编辑**：题型选择、提问模式、文字/评分开关、选项编辑、评分配置
- **导入模板下载**：一键下载 JSON 模板，按格式填写后导入

## 技术栈

### 后端
- **框架**：FastAPI + Uvicorn
- **数据库**：SQLite（开发）/ PostgreSQL（生产）
- **ORM**：SQLModel + SQLAlchemy
- **LLM**：OpenAI / Kimi / DeepSeek
- **WebSocket**：原生FastAPI WebSocket

### 前端
- **框架**：React 18 + TypeScript
- **构建**：Vite
- **UI**：shadcn/ui + Tailwind CSS
- **状态**：Zustand
- **动画**：Framer Motion

## 功能覆盖检查

### 核心概念
- [x] 三层人格架构（模板/档案/行为指令）
- [x] 三层记忆机制（对话历史/态度状态/经历锚点）
- [x] 四种提问模式（全局/顺序/开放/追问）
- [x] 可见性控制（isolated/open）
- [x] Agent状态与情绪广播
- [x] LLM配置包（ProviderPack）
- [x] AI/人类主持人切换

### 调研场景
- [x] 问卷调查（Survey）
- [x] 焦点小组（Focus Group）
- [x] 深度访谈（IDI）
- [x] 辩论讨论（Debate）

### 数据管理
- [x] JSON问卷导出
- [x] JSON结果导出
- [x] 问卷导入模板
- [x] 问卷星/腾讯问卷兼容
- [x] Persona模板库（6个模板）
- [x] 行为提示词库（8种风格）

### 前端功能
- [x] Dashboard实时看板
- [x] 任务创建向导（含思考模式+分组导入）
- [x] 问卷编辑器（含评分配置+模板下载）
- [x] Persona管理（含分组+LLM优化+详情弹窗）
- [x] 配置管理（含供应商预设+连通测试+模型检测）
- [x] 结果页（含统计/评分一览/反馈/逐题/导出）
- [x] 任务列表进度条

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加 OpenAI API Key

# 启动服务
uvicorn virtual_survey.main:app --reload --port 8000
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 访问应用
- 前端：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 项目结构

```
virtual-survey/
├── backend/
│   ├── virtual_survey/
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心引擎
│   │   │   └── scenarios/    # 调研场景
│   │   ├── models/           # 数据模型
│   │   ├── memory/           # 记忆系统
│   │   ├── llm/              # LLM适配层
│   │   │   └── adapters/     # LLM供应商适配
│   │   ├── export/           # 导入导出
│   │   ├── prompts/          # 提示词模板
│   │   └── storage/          # 存储层
│   ├── configs/              # 配置文件
│   │   ├── providers/        # LLM配置
│   │   ├── personas/         # Persona模板
│   │   ├── surveys/          # 问卷模板
│   │   ├── behavior_prompts/ # 行为提示词
│   │   └── scenarios/        # 场景配置
│   └── tests/                # 测试
├── frontend/
│   ├── src/
│   │   ├── components/       # React组件
│   │   │   ├── ui/           # shadcn/ui组件
│   │   │   ├── layout/       # 布局组件
│   │   │   ├── dashboard/    # Dashboard组件
│   │   │   ├── task/         # 任务组件
│   │   │   ├── survey/       # 问卷组件
│   │   │   ├── persona/      # Persona组件
│   │   │   ├── config/       # 配置组件
│   │   │   └── history/      # 历史组件
│   │   ├── pages/            # 页面
│   │   ├── stores/           # 状态管理
│   │   ├── api/              # API客户端
│   │   ├── hooks/            # 自定义Hooks
│   │   ├── types/            # TypeScript类型
│   │   └── lib/              # 工具函数
│   └── public/               # 静态资源
├── docs/                     # 文档
├── examples/                 # 示例
└── scripts/                  # 脚本
```

## 配置说明

### LLM配置

在 `backend/configs/providers/` 目录下创建YAML配置文件：

```yaml
name: "OpenAI"
base_url: "https://api.openai.com/v1"
api_key: "${OPENAI_API_KEY}"
default_model: "gpt-4o-mini"
api_params:
  max_tokens_param: "max_tokens"
  auth_header: "Authorization"
thinking_config:
  mode: "effort_only"
  effort_key: "reasoning_effort"
  effort_values: ["low", "medium", "high"]
models:
  - id: "gpt-4o"
    name: "GPT-4o"
    max_tokens: 4096
    supports_thinking: false
  - id: "gpt-4o-mini"
    name: "GPT-4o Mini"
    max_tokens: 4096
    supports_thinking: false
```

### 环境变量

创建 `backend/.env` 文件：

```env
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./data/surveysim.db
# 以下三家供应商已预置配置和API Key
MIMO_API_KEY=your_mimo_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
VOLCENGINE_API_KEY=your_volcengine_api_key_here
```

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

### 主要API端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/tasks | 创建任务 |
| GET | /api/v1/tasks | 任务列表（含进度） |
| POST | /api/v1/tasks/{id}/start | 启动任务 |
| POST | /api/v1/tasks/{id}/pause | 暂停任务 |
| POST | /api/v1/tasks/{id}/resume | 恢复任务 |
| POST | /api/v1/tasks/{id}/stop | 停止任务 |
| GET | /api/v1/tasks/{id}/results | 查看结果（含参与者配置+反馈） |
| GET | /api/v1/tasks/{id}/export/json | 导出结果 JSON |
| GET | /api/v1/tasks/{id}/export/csv | 导出结果 CSV |
| POST | /api/v1/surveys | 创建问卷 |
| GET | /api/v1/surveys/templates | 问卷模板 |
| POST | /api/v1/personas | 创建Persona |
| POST | /api/v1/personas/{id}/optimize | LLM优化Persona |
| GET | /api/v1/personas/groups | 人格分组列表 |
| POST | /api/v1/personas/groups | 创建人格分组 |
| GET | /api/v1/personas/groups/{id}/personas | 分组内人格列表 |
| POST | /api/v1/providers/{name}/test-connect | 连通性测试 |
| POST | /api/v1/providers/{name}/detect-models | 检测模型列表 |
| WS | /ws/sessions/{session_id} | WebSocket实时通信 |

## 开发指南

### 添加新的调研场景

1. 在 `backend/virtual_survey/core/scenarios/` 创建新场景文件
2. 继承 `Scenario` 基类
3. 实现 `initialize()` 和 `execute()` 方法
4. 在 `core/engine.py` 中注册新场景

### 添加新的LLM供应商

1. 在 `backend/virtual_survey/llm/adapters/` 创建适配器
2. 继承 `LLMProvider` 基类
3. 实现 `chat()` 和 `chat_json()` 方法
4. 在 `llm/manager.py` 中注册适配器

## 更新日志

### v0.8.0 — 结果系统 & 人格分组 & 人工主持增强
- **完整结果页**：统计卡片 + 情绪分布图 + 评分一览 + 问卷反馈 + 逐题展开 + 参与者配置
- **参与者配置展示**：结果页显示每位 Agent 的人格名、职业、行为模式、LLM/模型、思考模式状态
- **结果导出**：JSON（完整结构化）/ CSV（表格化含评分列）两种格式
- **问卷体验反馈**：全部答题后 5 维度打分（长度/难度/清晰度/疲劳/兴趣）+ 评语
- **反馈可视化**：5 维度水平汇总色条 + 各 Agent 评分散点 + 评语展示
- **人格分组系统**：CRUD + 多对多关系 + 分组筛选 + 任务创建从分组一键导入
- **人格详情弹窗**：完整人口统计、性格特征、背景故事、经历、态度、分组
- **人格编辑弹窗**：全字段表单编辑（年龄/职业/背景故事/经历/态度等）
- **人工主持人增强**：接管暂停 AI 流程 → 逐题控制（开始本题/追问/群发提问）→ 交回恢复 AI
- **问卷编辑器重建**：题目类型/模式/文字开关/评分开关/选项编辑器/评分配置 + 模板下载
- **Trailing Slash 修复**：前后端路由统一，POST/PUT/DELETE 请求不再重定向丢失 body
- **Provider 自动注册**：启动时遍历 YAML 配置自动注册所有供应商
- **SurveyWrapper**：dict 和 Pydantic 模型统一访问层，修复运行时 `questions` 属性访问错误
- **Jinja2 修复**：`dict.values` 与模板保留字冲突修复，改用 `.get('values')`

### v0.7.0 — 评分系统 & 问卷体验反馈
- **RatingConfig 模型**：1~10 评分范围、最小/最大标签
- **题目级评分**：`enable_rating` + `rating_config`，Agent 自动输出 `score` 字段
- **评分+文字组合**：每题独立开关，两者同开则都必答
- **评分可视化**：结果页「评分一览」色条 + 各 Agent 散点标记
- **CSV 评分列**：导出含评分数据
- **5 维度问卷反馈**：长度/难度/清晰度/疲劳/兴趣 + 评语

### v0.6.0 — 思考模式 & 多供应商支持
- **多供应商预置**：MiMo / DeepSeek / 豆包(火山引擎) 三家供应商一键配置
- **思考模式引擎**：三种思考模式（toggle/effort/effort_only）
- **智能参数适配**：各供应商特有的参数自动处理
  - MiMo：`thinking: {type: enabled}` + temperature 覆写 + `max_completion_tokens`
  - DeepSeek：`thinking: {type: enabled}` + `reasoning_effort: high/max` + 禁用参数
  - 豆包：`reasoning_effort: minimal/low/medium/high`
- **连通性测试**：`POST /test-connect` 真实 API 调用验证
- **模型检测**：`POST /detect-models` 从 API 拉取模型列表
- **模型行编辑器**：可视化增删改模型，per-model 思考模式标记
- **前端**：ConfigPage 预设卡片 + TaskCreatePage 思考模式控件
- **后端**：pack.py 扩展 thinking_config，LLM Adapter 动态参数注入

### 端到端测试报告 (2026-05-29)

**5 Agent × 15 题 × DeepSeek/MiMo 双供应商混合测试：**

| 项目 | 结果 |
|------|------|
| 状态 | ✅ completed |
| 总题数 | 15 |
| 总回答 | 77（含 2 次追问） |
| 评分数 | 15（q6/q12/q15 × 5 人） |
| 情绪类型 | 14 种 |
| 问卷反馈 | 5 条（5 Agent × 5 维度 + 评语） |
| 参与者信息 | 5 条（人格名/职业/LLM/模型/行为模式/思考状态） |

**Agent 配置分布：**
- 赵伟：赵伟(技术总监) × DeepSeek/deepseek-v4-pro × neutral × 🧠high
- 王小飞：王小飞(全栈独立开发者) × DeepSeek/deepseek-v4-pro × detailed × 🧠max
- 张婷：张婷(产品经理) × MiMo/mimo-v2.5-pro × honest × 关
- 孙晓芸：孙晓芸(数据分析师) × DeepSeek/deepseek-v4-pro × analytical × 关
- 周博文：周博文(计算机研究生) × MiMo/mimo-v2.5-pro × emotional × 🧠high

**反馈摘要：**
- 问卷设计合理，但部分技术问题可以更深入（赵伟）
- 问题覆盖全面，但中间部分略有重复感（王小飞）
- 题型多样，总体清晰，问卷长度适中（孙晓芸）

### API 测试报告 (2026-05-29)
| Provider | 模型 | 基础对话 | 思考模式 | 流式输出 | 延迟 |
|----------|------|---------|---------|---------|------|
| MiMo | mimo-v2.5-pro | ✅ | ✅ (toggle, 16 tokens) | ✅ | 1922ms |
| DeepSeek | deepseek-v4-pro | ✅ | ✅ (effort, 29 tokens) | ✅ | 1191ms |
| 豆包 | doubao-seed-2-0-pro-260215 | ✅ | ✅ (effort_only) | ✅ | 5274ms |
| 豆包 | doubao-seed-2-0-mini | ❌ AccessDenied | - | - | - |
| 豆包 | doubao-seed-2-0-lite | ❌ AccessDenied | - | - | - |

> 注：豆包 mini/lite 模型因当前 API Key 权限不足不可用，pro 模型正常。

### v0.5.0 (阶段5完成)
- 前端基础架构
- React + TypeScript + Vite项目
- shadcn/ui + Tailwind CSS样式
- Zustand状态管理
- WebSocket实时通信
- 布局组件（Sidebar/Header/MainLayout）
- 核心页面（任务列表/任务创建/问卷管理/人格管理/系统配置）

### v0.3.0 (阶段3完成)
- REST API实现（任务/问卷/Persona/Provider/行为提示词）
- WebSocket实时通信
- 问卷导入导出（JSON/问卷星/腾讯问卷格式）
- FastAPI主应用（CORS/生命周期管理）

### v0.2.0 (阶段2完成)
- 核心引擎实现
- 四种调研场景（问卷调查/焦点小组/深度访谈/辩论讨论）
- AI主持人系统（开场/评估/追问/引导/总结）
- 人类主持人支持（接管/释放）
- 受访者Agent（回答/态度提取/经历记忆）
- 任务执行引擎（会话管理/暂停恢复/状态广播）

### v0.1.0 (阶段1完成)
- 项目结构搭建
- 数据模型定义（Task/Persona/Survey/Message/Scenario）
- 存储层实现（SQLite + YAML配置）
- LLM适配层（OpenAI适配器 + 限流 + 重试）
- 三层记忆系统（对话历史/态度状态/经历锚点）
- 提示词模板系统（Jinja2模板）
- 配置文件（Provider/Persona/问卷/行为提示词/场景模板）

## 许可证

MIT License

## 联系方式

- 项目地址：https://github.com/your-username/SurveySim
- 问题反馈：https://github.com/your-username/SurveySim/issues
