<div align="center">

# 🎭 SurveySim — Virtual Research Lab

### ✨ Let AI Complete 10,000 Surveys For You ✨

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?style=for-the-badge&logo=react)](https://reactjs.org/)
[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg?style=for-the-badge)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <img src="https://img.shields.io/badge/🧠-LLM_Powered-ff6b6b?style=flat-square" />
  <img src="https://img.shields.io/badge/👥-Multi_Agent-4ecdc4?style=flat-square" />
  <img src="https://img.shields.io/badge/📊-Real-time_Viz-45b7d1?style=flat-square" />
  <img src="https://img.shields.io/badge/🎭-Persona_Sim-f7dc6f?style=flat-square" />
  <img src="https://img.shields.io/badge/🎤-Human_Moderator-9b59b6?style=flat-square" />
</p>

**🚀 LLM-Powered Simulated Survey & Group Research Platform**

> Configure multiple AI Agents with distinct personas to simulate real human survey respondents.
> Use it to **pre-evaluate survey design**, **test question comprehension**, **discover hidden biases**, and **explore group dynamics**.

**中文文档**: [README.md](README.md)

[🎬 Quick Start](#-quick-start) • [📖 Features](#-features) • [🎤 Human Moderator](#-human-moderator-mode) • [🏗️ Architecture](#-core-architecture) • [🛠️ Tech Stack](#-tech-stack)

</div>

---

## 🌟 Why SurveySim?

Pain points of traditional survey research 😫:

| 😤 Hard to Find | 😵 Expensive | 😰 Slow | 😵‍💫 Bias Blind Spots |
|---------|---------|---------|------------|
| Recruiting target respondents takes time | Every survey costs real money | Waiting for responses and analysis | Designer-introduced leading biases |

**SurveySim's Solution 💡:**

> 🎯 **Simulate with AI before deploying to real people!**

- 🧪 Use AI Agents to simulate respondents from diverse backgrounds and discover survey flaws early
- ⚡ Complete hundreds of "virtual responses" in minutes, rapidly iterate survey design
- 🎭 Observe how different personas interact and predict real group dynamics
- 💰 Zero-cost pre-testing — save your budget for real user research

---

## 🎪 Four Research Scenarios

SurveySim is more than a survey tool — it's a complete **Virtual Research Lab** 🔬

| Scenario | Icon | Description | Use Cases |
|------|------|------|----------|
| **📋 Survey** | 📝 | Standardized questions, each Agent answers independently | Customer satisfaction, market research |
| **🗣️ Focus Group** | 💬 | Free-form group discussion, Agents see and influence each other | Product experience, user needs |
| **🎤 In-Depth Interview** | 🕵️ | One-on-one deep dive, moderator asks follow-ups | User research, case studies |
| **⚔️ Debate** | 🥊 | Pro vs. con argument clash, observe attitude evolution | Opinion analysis, decision support |

---

## 🧬 Core Architecture

### 🎭 Three-Layer Persona Architecture — Every Agent is a "Real Person"

```
┌──────────────────────────────────────────────┐
│  🎨 Layer 3: Behavior Instructions            │
│  • Global answer style (honest/detailed/...)  │
│  • Format constraints                         │
│  • Prohibitions (no pleasing, no fabricating) │
├──────────────────────────────────────────────┤
│  👤 Layer 2: Persona Profile                  │
│  • Demographics: age/gender/city/income       │
│  • Psychographics: values/personality         │
│  • Background: education/family/experiences   │
├──────────────────────────────────────────────┤
│  🧬 Layer 1: Template Generation              │
│  • Preset population templates                │
│  • Batch persona synthesis                    │
└──────────────────────────────────────────────┘
```

### 🧠 Three-Layer Memory System — No More Contradictions

| Memory Type | 🧩 Purpose | 💾 Content |
|---------|--------|------------|
| **💬 Conversation History** | Maintain context coherence | Recent N Q&A rounds |
| **🎭 Attitude State** | Track stance evolution | Timeline of position changes on key topics |
| **⚓ Experience Anchors** | Concrete fact references | Specific events, numbers, timestamps mentioned |

### 🎤 Moderator System — Seamless AI / Human Switching

```
🤖 AI Moderator ←——[One-Click Takeover]——→ 🧑‍💼 Human Moderator
```

- 🤖 **AI Moderator**: Auto-generates openings, evaluates response quality, triggers intelligent follow-ups
- 🧑‍💼 **Human Moderator**: Full manual control — opening, questions, follow-ups, guidance, summaries
- 🔄 **Seamless Switching**: Switch between AI auto and human control at any time

---

## ✨ Features

### 🎤 Human Moderator Mode — New in v1.0.0!

Take full control of the research process while AI Agents handle only the responses:

- 🎬 **Opening Statement**: Write your own introduction to the research topic
- 📋 **Question-by-Question Control**: Manually trigger each question, no auto-advance
- 💬 **Ad-hoc Questions**: Ask free-form questions to all or specific Agents anytime
- 🔄 **Follow-up Decisions**: After each response, decide whether to follow up and what to ask
- 📖 **Round Guidance**: Input guidance between focus group rounds
- 📝 **Final Summary**: Write the research conclusion yourself
- ⏸️ **Waiting Indicator**: Real-time display of what input the system is waiting for

### 🧠 Thinking Mode

Supports **4 top LLM providers** with intelligent thinking mode adaptation:

| Provider | 🧩 Thinking Mode | ✨ Feature |
|--------|-----------|--------|
| **🟢 MiMo** | toggle switch | Pure toggle mode, auto-overrides temperature=1.0 |
| **🔵 DeepSeek** | effort intensity | Toggle + intensity control, `high` / `max` levels |
| **🟠 Volcengine (Doubao)** | effort_only | Pure intensity control, four granular levels |
| **⚪ OpenAI** | — | Standard chat mode |

### 👥 Persona Group Management

- 📁 Group CRUD: create/edit/delete persona groups
- 🔗 Many-to-many relationships: one persona can belong to multiple groups
- 🏷️ Badge filtering for quick group-based selection
- 📥 Batch import from groups when creating tasks

### ⭐ Question Rating System

- 📊 1-10 rating scale + text response per question
- ⚙️ Per-question toggle and customizable rating range
- 📈 Visual bar charts and scatter plots in results

### 📊 Results & Export

- 📋 Stats cards: emotion distribution, rating summaries at a glance
- 📉 Emotion timeline visualization
- 📥 Multi-format export: JSON (full data) / CSV (tabular)
- 📝 Survey feedback: 5-dimension experience ratings + Agent commentary

### 🛠️ More Highlights

- 🎯 **Smart Follow-up**: Auto-triggers when answers are short, vague, contradictory, or anomalous
- 👁️ **Visibility Control**: `isolated` (agents can't see each other) / `open` (full visibility)
- 🌊 **WebSocket Streaming**: Real-time dashboard with emotion/status second-by-second updates
- 📦 **Docker One-Click Deploy**: `docker-compose up` and you're running
- 📝 **Survey Templates**: Customer satisfaction, market research, product feedback out of the box
- 🔄 **Survey Import/Export**: JSON / Wenjuanxing / Tencent Survey format compatibility

---

## 🎤 Human Moderator Mode

### Usage Flow

1. **Select "Human Moderator" when creating a task** — Choose in the first step of the creation wizard
2. **Enter the Dashboard** — Auto-redirected after task creation
3. **Click "Take Over Moderator"** — AI auto-flow pauses, you get full control
4. **Write the Opening** — System prompts for an opening statement, then broadcasts to all Agents
5. **Advance Question by Question** — Click "Start This Question" to trigger Agent responses
6. **Decide on Follow-ups** — After each response, decide: continue to next question or ask a follow-up
7. **Ask Ad-hoc Questions** — Type free-form questions to all or specific Agents anytime
8. **Write the Summary** — After all questions, input your research summary
9. **Return to AI** — Hand control back to AI at any time

### Waiting State Indicators

The Dashboard shows real-time indicators for what input is needed:

| Indicator | Meaning |
|--------|---------|
| 🎤 Waiting for Opening | Needs opening statement input |
| 📖 Waiting for Guidance | Needs between-round guidance |
| ➡️ Waiting for Next Question | Needs click to start next question |
| 🤔 Waiting for Decision | Needs follow-up decision |
| 📝 Waiting for Summary | Needs research summary input |

Each waiting state includes a "Skip" button to bypass the current input.

---

## 🚀 Quick Start

### 📦 Requirements

- 🐍 Python 3.10+
- 🟢 Node.js 18+
- 📦 npm or yarn

### 🖥️ Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API Key
uvicorn virtual_survey.main:app --reload --port 8000
```

### 🎨 Frontend

```bash
cd frontend
npm install
npm run dev
```

### 🐳 Docker (Recommended)

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API Key
docker-compose up --build
```

### 🌐 Access

| Service | URL |
|------|------|
| 🎨 Frontend | http://localhost:3000 |
| 🔧 Backend API | http://localhost:8000 |
| 📚 API Docs | http://localhost:8000/docs |

---

## 🛠️ Tech Stack

### Backend

| Technology | Description |
|------|------|
| ⚡ **FastAPI** | High-performance async web framework |
| 🗄️ **SQLModel** | Modern Python ORM |
| 🔌 **WebSocket** | Native FastAPI real-time communication |
| 🤖 **Multi-LLM** | OpenAI / DeepSeek / MiMo / Volcengine |
| 🐍 **Python 3.11** | Async engine driven |

### Frontend

| Technology | Description |
|------|------|
| ⚛️ **React 18** | Declarative UI framework |
| 🔷 **TypeScript** | Type safety |
| ⚡ **Vite** | Lightning-fast build tool |
| 🎨 **shadcn/ui** | Beautiful component library |
| 🌊 **Tailwind CSS** | Utility-first styling |
| 🏪 **Zustand** | Lightweight state management |
| ✨ **Framer Motion** | Smooth animations |

---

## 📁 Project Structure

```
🎭 SurveySim/
├── 🖥️ backend/                  # Backend service
│   ├── 🧠 virtual_survey/       # Core application
│   │   ├── 🔌 api/              # REST API + WebSocket
│   │   ├── ⚙️ core/             # Engine + Scenarios
│   │   ├── 🤖 llm/              # LLM adapters
│   │   ├── 🧠 memory/           # Three-layer memory
│   │   ├── 🎭 models/           # Data models
│   │   ├── 📝 prompts/          # Jinja2 prompt templates
│   │   └── 💾 storage/          # DB + YAML config store
│   ├── 📋 configs/              # Configuration files
│   ├── 🐳 Dockerfile
│   └── ⚙️ pyproject.toml
├── 🎨 frontend/                 # Frontend app
│   ├── 📂 src/
│   ├── 🐳 Dockerfile
│   └── 📦 package.json
├── 🐳 docker-compose.yml
├── 📋 CHANGELOG.md
├── 📖 README.md                 # Chinese docs
├── 📖 README_EN.md              # English docs
└── 📜 LICENSE
```

---

## ⚙️ Configuration

### 🔌 LLM Provider Config

Create YAML files in `backend/configs/providers/`:

```yaml
name: "OpenAI"
base_url: "https://api.openai.com/v1"
api_key: "${OPENAI_API_KEY}"
default_model: "gpt-4o-mini"
models:
  - id: "gpt-4o"
    name: "GPT-4o"
    max_tokens: 4096
```

### 🌍 Environment Variables

Create `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DATABASE_URL=sqlite:///./data/surveysim.db
HOST=0.0.0.0
PORT=8000
```

---

## 🗺️ Roadmap

### ✅ Implemented

- [x] 🎭 Three-layer persona architecture
- [x] 🧠 Three-layer memory system
- [x] 🎤 Four research scenarios
- [x] 🤖 AI / Human moderator seamless switching
- [x] 🧩 Thinking mode (multi-provider)
- [x] 👥 Persona group management
- [x] ⭐ Question rating system
- [x] 📊 Result visualization & export
- [x] 🎤 Human moderator full control

### 📋 Planned

- [ ] 🌍 Multi-language support
- [ ] 🔐 User authentication & permissions
- [ ] 📈 Advanced analytics (bias detection, sentiment analysis)
- [ ] 🧪 A/B testing framework
- [ ] 📱 Mobile responsive
- [ ] 🔗 More LLM provider integrations

---

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md)

---

## 🤝 Contributing

Issues and PRs welcome! 🎉

1. 🍴 Fork this repo
2. 🌿 Create your feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add some amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔀 Open a Pull Request

---

## 📜 License

[MIT License](LICENSE) © SurveySim Team

---

<div align="center">

### 💖 If SurveySim helps you, please give us a Star!

[![Stars](https://img.shields.io/github/stars/Gary23333/Surveysim?style=social)](https://github.com/Gary23333/Surveysim)

**🌟 Star → 🍴 Fork → 🚀 Build → 🎉 Enjoy!**

</div>
