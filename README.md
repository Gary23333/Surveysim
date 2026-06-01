<div align="center">

# 🎭 SurveySim — 虚拟调研实验室

### ✨ 让 AI 替你完成一万份问卷 ✨

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?style=for-the-badge&logo=react)](https://reactjs.org/)
[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg?style=for-the-badge)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <img src="https://img.shields.io/badge/🧠-大模型驱动-ff6b6b?style=flat-square" />
  <img src="https://img.shields.io/badge/👥-多Agent模拟-4ecdc4?style=flat-square" />
  <img src="https://img.shields.io/badge/📊-实时可视化-45b7d1?style=flat-square" />
  <img src="https://img.shields.io/badge/🎭-人格模拟-f7dc6f?style=flat-square" />
  <img src="https://img.shields.io/badge/🎤-人工主持-9b59b6?style=flat-square" />
</p>

**🚀 大模型驱动的模拟问卷调查与群体调研平台**

> 配置多个具有不同人格的 AI Agent，模拟真实人类受访者参与问卷调查或焦点小组讨论，
> 用于**预评价问卷设计效果**、**测试问题理解度**、**发现潜在偏见**、**探索群体互动动态**。

**English Version**: [README_EN.md](README_EN.md)

[🎬 快速开始](#-快速开始) • [📖 功能介绍](#-功能特性) • [🎤 人工主持](#-人工主持人模式) • [🏗️ 架构设计](#-核心架构) • [🛠️ 技术栈](#-技术栈)

</div>

---

## 🌟 为什么需要 SurveySim？

传统问卷调研的痛点 😫：

| 😤 找人难 | 😵 成本高 | 😰 周期长 | 😵‍💫 偏见盲区 |
|---------|---------|---------|------------|
| 招募目标受访者费时费力 | 每份问卷都要真金白银 | 等回收、等分析，黄花菜都凉了 | 设计者自己意识不到的引导性偏差 |

**SurveySim 的解决方案 💡：**

> 🎯 **在发布真实问卷之前，先用 AI 模拟一轮！**

- 🧪 用 AI Agent 模拟不同背景的受访者，提前发现问卷缺陷
- ⚡ 几分钟完成数百份"虚拟回答"，快速迭代问卷设计
- 🎭 观察不同人格的 Agent 如何互动，预判真实群体动态
- 💰 零成本预测试，把预算留给真正需要真实用户的环节

---

## 🎪 四大调研场景

SurveySim 不只是问卷工具，更是一个完整的**虚拟调研实验室** 🔬

| 场景 | 图标 | 说明 | 适用场景 |
|------|------|------|----------|
| **📋 问卷调查** | 📝 | 标准化问题收集，每个 Agent 独立回答 | 满意度调查、市场调研 |
| **🗣️ 焦点小组** | 💬 | 多人自由讨论，Agent 互相可见、互相影响 | 产品体验、用户需求 |
| **🎤 深度访谈** | 🕵️ | 一对一深入挖掘，主持人逐题追问 | 用户研究、案例分析 |
| **⚔️ 辩论讨论** | 🥊 | 正反方观点碰撞，观察态度演化 | 观点分析、决策支持 |

---

## 🧬 核心架构

### 🎭 三层人格架构 — 让每个 Agent 都是"活人"

```
┌──────────────────────────────────────────────┐
│  🎨 Layer 3: 行为指令层                        │
│  • 全局回答风格（如实/详细/简洁/批判...）       │
│  • 格式约束（JSON/自然语言）                   │
│  • 禁止事项（不迎合、不编造、不猜测）          │
├──────────────────────────────────────────────┤
│  👤 Layer 2: 人格档案层                        │
│  • 人口统计：年龄/性别/城市/收入/职业           │
│  • 心理画像：价值观/性格/风险偏好               │
│  • 背景故事：教育/家庭/关键经历                │
├──────────────────────────────────────────────┤
│  🧬 Layer 1: 模板生成层                        │
│  • 预设人群模板（一线城市白领/小镇青年...）     │
│  • 批量合成虚拟人格                            │
└──────────────────────────────────────────────┘
```

### 🧠 三层记忆系统 — 回答不再"前后矛盾"

| 记忆类型 | 🧩 作用 | 💾 存储内容 |
|---------|--------|------------|
| **💬 对话历史** | 保持上下文连贯 | 最近 N 轮问答 |
| **🎭 态度状态** | 追踪立场演化 | 对关键话题的立场变化时间线 |
| **⚓ 经历锚点** | 具体事实引用 | 提到过的具体事件、数字、时间 |

> 🎯 **递进式追问示例**："你刚才表示谨慎乐观，那如果预算砍掉一半，你还会坚持这个观点吗？"

### 🎤 主持人系统 — AI / 人类无缝切换

```
🤖 AI 主持人 ←——【一键接管】——→ 🧑‍💼 人类主持人
```

- 🤖 **AI 主持人**：自动生成开场白、评估回答质量、智能追问引导
- 🧑‍💼 **人类主持人**：全程手动控制，开场白/提问/追问/引导/总结均由你输入
- 🔄 **无缝切换**：随时在 AI 自动和人工控制之间切换

---

## ✨ 功能特性

### 🎤 人工主持人模式 — v1.0.0 全新上线！

支持人类全程控制调研流程，AI Agent 退居幕后只负责回答：

- 🎬 **开场白**：由你撰写，介绍调研主题和参与者
- 📋 **逐题推进**：手动触发每一道题，不自动推进
- 💬 **自由提问**：随时向全体或个别 Agent 提问
- 🔄 **追问决策**：每条回答后由你决定是否追问、追问什么
- 📖 **轮间引导**：焦点小组每轮结束后输入引导语
- 📝 **最终总结**：由你撰写调研总结
- ⏸️ **等待指示器**：实时显示当前等待你输入的类型

### 🧠 思考模式

支持 **4 家顶级大模型供应商**，智能适配各家思考模式：

| 供应商 | 🧩 思考模式 | ✨ 特色 |
|--------|-----------|--------|
| **🟢 MiMo** | toggle 开关 | 纯开关模式，自动覆写 temperature=1.0 |
| **🔵 DeepSeek** | effort 强度 | 开关 + 强度控制，`high` / `max` 两档 |
| **🟠 豆包(火山引擎)** | effort_only | 纯强度控制，四档精细调节 |
| **⚪ OpenAI** | — | 标准对话模式 |

- 🔌 **连通性测试**：一键测试 API 连接，实时返回延迟和状态
- 🔍 **模型检测**：自动拉取供应商可用模型列表，一键导入
- 🎛️ **任务级控制**：每个 Agent 独立配置思考开关和强度

### 👥 人格分组管理

- 📁 **分组 CRUD**：创建/编辑/删除人格分组
- 🔗 **多对多关系**：一个人格可属于多个分组
- 🏷️ **Badge 筛选**：快速筛选分组下的人格
- 📥 **一键导入**：创建任务时从分组批量导入成员

### ⭐ 题目评分系统

- 📊 **程度评分**：1~10 分独立评分 + 文字回答
- ⚙️ **灵活配置**：每题独立开关，评分范围自定义
- 📈 **可视化展示**：结果页色条 + 散点图直观呈现

### 📊 结果查看 & 导出

- 📋 **统计卡片**：情绪分布、评分汇总一目了然
- 📉 **情绪热力图**：观察 Agent 情绪波动轨迹
- 📥 **多格式导出**：JSON（完整数据）/ CSV（表格化）
- 📝 **问卷反馈**：5 维度体验评分 + Agent 评语

### 🛠️ 更多亮点

- 🎯 **智能追问**：回答太短、矛盾、模糊、异常时自动触发追问
- 👁️ **可见性控制**：`isolated`（互不可见）/ `open`（互相感知）两种模式
- 🌊 **WebSocket 实时流**：Dashboard 实时看板，情绪/状态秒级更新
- 📦 **Docker 一键部署**：`docker-compose up` 即可运行
- 📝 **问卷模板库**：满意度调查、市场调研、产品反馈开箱即用
- 🔄 **问卷导入导出**：JSON / 问卷星 / 腾讯问卷格式兼容

---

## 🎤 人工主持人模式

### 使用流程

1. **创建任务时选择人工主持人** — 在创建向导第一步选择「🧑‍💼 人工主持人」
2. **进入实时监控面板** — 创建完成后自动跳转 Dashboard
3. **点击「接管主持人」** — AI 自动流程暂停，你获得完全控制权
4. **撰写开场白** — 系统提示等待开场白，输入后广播给所有 Agent
5. **逐题推进** — 点击「开始本题」触发 Agent 回答
6. **决定是否追问** — 每条回答后系统提示你决定：继续下一题 or 追问
7. **群发提问** — 随时输入自由问题，向全体或指定 Agent 提问
8. **撰写总结** — 所有题目完成后输入调研总结
9. **交回 AI** — 随时可将控制权交回 AI 继续自动运行

### 等待状态指示器

Dashboard 顶部会实时显示当前等待你输入的类型：

| 指示器 | 含义 |
|--------|------|
| 🎤 等待开场白 | 需要输入调研开场白 |
| 📖 等待引导语 | 焦点小组轮间需要引导 |
| ⬅️ 等待推进下一题 | 需要点击开始下一题 |
| 🤔 等待追问决策 | 需要决定是否追问 |
| 📝 等待总结 | 需要输入调研总结 |

每个等待状态都带有「跳过」按钮，可以跳过当前输入。

---

## 🖼️ 界面预览

> 🚧 截图正在制作中，以下是功能区域示意：

```
┌─────────────────────────────────────────────────────────┐
│  🎯 SurveySim Dashboard — 实时调研看板     🟢 已连接     │
├─────────────────────────────────────────────────────────┤
│  🤖 AI 主持中  [🎤 接管主持人]                            │
│                                                         │
│  ┌── ⏸️ 等待推进下一题 ──────────────────────────────┐  │
│  │  第 3 / 10 题  [开始本题] [结束调研]               │  │
│  │  群发提问: [________________] [发送]               │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  参与者回答                                    12 条     │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 🧑‍🦱 张小花  😊 兴奋                               │  │
│  │ "我觉得这个功能特别实用..."                        │  │
│  │                              [💬 追问]             │  │
│  │───────────────────────────────────────────────── │  │
│  │ 🧑‍🦲 李明    😐 谨慎                               │  │
│  │ "隐私方面我有些顾虑..."                            │  │
│  │                              [💬 追问]             │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 📦 环境要求

- 🐍 Python 3.10+
- 🟢 Node.js 18+
- 📦 npm 或 yarn

### 🖥️ 后端启动

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
# 编辑 .env 文件，填入你的 API Key

# 启动服务
uvicorn virtual_survey.main:app --reload --port 8000
```

### 🎨 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 🐳 Docker 一键部署（推荐）

```bash
# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入你的 API Key

# 一键启动
docker-compose up --build
```

### 🌐 访问应用

| 服务 | 地址 |
|------|------|
| 🎨 前端 | http://localhost:3000 |
| 🔧 后端 API | http://localhost:8000 |
| 📚 API 文档 | http://localhost:8000/docs |

---

## 🛠️ 技术栈

### 后端

| 技术 | 说明 |
|------|------|
| ⚡ **FastAPI** | 高性能异步 Web 框架 |
| 🗄️ **SQLModel** | 现代化的 Python ORM |
| 🔌 **WebSocket** | 原生 FastAPI 实时通信 |
| 🤖 **多 LLM 适配** | OpenAI / DeepSeek / MiMo / 豆包 |
| 🐍 **Python 3.11** | 异步引擎驱动 |

### 前端

| 技术 | 说明 |
|------|------|
| ⚛️ **React 18** | 声明式 UI 框架 |
| 🔷 **TypeScript** | 类型安全 |
| ⚡ **Vite** | 极速构建工具 |
| 🎨 **shadcn/ui** | 精美组件库 |
| 🌊 **Tailwind CSS** | 原子化样式 |
| 🏪 **Zustand** | 轻量级状态管理 |
| ✨ **Framer Motion** | 流畅动画 |

---

## 📁 项目结构

```
🎭 SurveySim/
├── 🖥️ backend/                  # 后端服务
│   ├── 🧠 virtual_survey/       # 核心应用代码
│   │   ├── 🔌 api/              # REST API + WebSocket
│   │   ├── ⚙️ core/             # 调研引擎 + 场景
│   │   ├── 🤖 llm/              # LLM 适配层
│   │   ├── 🧠 memory/           # 三层记忆系统
│   │   ├── 🎭 models/           # 数据模型
│   │   ├── 📝 prompts/          # Jinja2 提示词模板
│   │   └── 💾 storage/          # 数据库 + YAML 配置存储
│   ├── 📋 configs/              # 配置文件
│   │   ├── 🔌 providers/        # LLM 供应商配置
│   │   ├── 👥 personas/         # 人格模板
│   │   ├── 📝 surveys/          # 问卷模板
│   │   └── 🎨 behavior_prompts/ # 行为提示词
│   ├── 🐳 Dockerfile
│   └── ⚙️ pyproject.toml
│
├── 🎨 frontend/                 # 前端应用
│   ├── 📂 src/
│   │   ├── 🔧 api/              # API 客户端
│   │   ├── 🧩 components/       # React 组件
│   │   ├── 📄 pages/            # 页面
│   │   ├── 🏪 stores/           # Zustand 状态
│   │   └── 🎣 hooks/            # 自定义 Hooks
│   ├── 🐳 Dockerfile
│   └── 📦 package.json
│
├── 🐳 docker-compose.yml
├── 🚀 scripts/start.sh
├── 📋 CHANGELOG.md
├── 📖 README.md                 # 中文文档
├── 📖 README_EN.md              # English docs
└── 📜 LICENSE
```

---

## ⚙️ 配置说明

### 🔌 LLM 供应商配置

在 `backend/configs/providers/` 目录下创建 YAML 配置文件：

```yaml
name: "OpenAI"
base_url: "https://api.openai.com/v1"
api_key: "${OPENAI_API_KEY}"      # 👈 支持环境变量！
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
```

### 🌍 环境变量

创建 `backend/.env` 文件：

```env
# OpenAI API Key（必填）
OPENAI_API_KEY=your_openai_api_key_here

# 其他供应商（可选）
DEEPSEEK_API_KEY=your_deepseek_api_key_here
MIMO_API_KEY=your_mimo_api_key_here
VOLCENGINE_API_KEY=your_volcengine_api_key_here

# 数据库
DATABASE_URL=sqlite:///./data/surveysim.db

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

> ⚠️ **安全提示**：`.env` 文件已默认加入 `.gitignore`，**切勿**将其提交到 Git！

---

## 🗺️ 路线图

### ✅ 已实现

- [x] 🎭 三层人格架构
- [x] 🧠 三层记忆系统
- [x] 🎤 四种调研场景
- [x] 🤖 AI / 人类主持人无缝切换
- [x] 🧩 思考模式（多供应商适配）
- [x] 👥 人格分组管理
- [x] ⭐ 题目评分系统
- [x] 📊 结果可视化 & 导出
- [x] 🎤 人工主持人全程控制

### 📋 计划中

- [ ] 🌍 多语言支持
- [ ] 🔐 用户认证与权限
- [ ] 📈 高级数据分析（偏见检测、情感分析）
- [ ] 🧪 A/B 测试框架
- [ ] 📱 移动端适配
- [ ] 🔗 更多 LLM 供应商接入

---

## 📋 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

---

## 🤝 贡献指南

欢迎 Issue 和 PR！🎉

1. 🍴 Fork 本仓库
2. 🌿 创建你的 Feature 分支 (`git checkout -b feature/amazing-feature`)
3. 💾 提交改动 (`git commit -m 'Add some amazing feature'`)
4. 📤 Push 到分支 (`git push origin feature/amazing-feature`)
5. 🔀 提交 Pull Request

---

## 📜 许可证

[MIT License](LICENSE) © SurveySim Team

---

<div align="center">

### 💖 如果 SurveySim 对你有帮助，请给个 Star 支持一下！

[![Stars](https://img.shields.io/github/stars/Gary23333/Surveysim?style=social)](https://github.com/Gary23333/Surveysim)

**🌟 Star → 🍴 Fork → 🚀 Build → 🎉 Enjoy!**

</div>
