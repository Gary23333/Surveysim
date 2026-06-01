# Changelog

All notable changes to SurveySim will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-06-02

### Added
- **完整的人主持人模式**：支持人类主持人全程控制调研流程
  - 开场白、逐题推进、自由提问、引导语、总结均由人类输入
  - 等待状态指示器，前端实时显示主持人需要输入的类型
  - 创建任务时可预先配置主持人类型（AI / 人工）
- CHANGELOG.md 版本变更记录
- README_EN.md 英文文档
- WebSocket 连接状态指示器
- 自由提问结果记录到最终数据

### Changed
- 统一所有版本号到 1.0.0（pyproject.toml、package.json、main.py）
- 重写 README.md，新增人主持人模式使用指南
- ModeratorManager 支持 AI 和人类模式完整切换
- 场景引擎（问卷/焦点小组/深度访谈）支持人工暂停等待模式

### Fixed
- TypeScript 类型定义中重复的 ModeratorConfig 接口
- ModeratorCommandMessage 缺失的命令类型（next_question 等）
- takeover 命令在 session 和 websocket 双重处理的冲突
- HumanModerator 命令队列未连接 WebSocket 的问题
- ModeratorManager 在无 AI 主持人时的 TypeError

### Removed
- README 中的修复执行记录（迁移到 CHANGELOG.md）

## [0.8.0] - 2026-05-31

### Added
- 人格分组管理（CRUD、多对多关系、Badge 筛选、批量导入）
- 结果可视化（统计卡片、情绪分布图、评分汇总）
- 结果导出（JSON / CSV）
- 问卷反馈收集（5 维度体验评分）
- GitHub Actions CI（前端 type-check + build + lint，后端 compileall + pytest）
- 任务持久化（SQLite 存储、恢复、列表、删除）

### Fixed
- 前端 clean clone 构建阻塞
- WebSocket 实时广播注入
- 主持人 provider 选择错误
- Provider 连通性测试 payload
- LICENSE 文件缺失

## [0.7.0] - 2026-05

### Added
- 题目评分系统（1-10 分独立评分 + 文字回答）
- 每题独立评分开关和范围自定义
- 结果页色条 + 散点图可视化

## [0.6.0] - 2026-05

### Added
- 思考模式多供应商适配（MiMo toggle、DeepSeek effort、豆包 effort_only）
- LLM 供应商连通性测试和模型检测
- 任务级 Agent 独立思考配置

## [0.1.0] - 2026-05

### Added
- 初始版本发布
- 三层人格架构（行为指令 / 人格档案 / 模板生成）
- 三层记忆系统（对话历史 / 态度状态 / 经历锚点）
- 四种调研场景（问卷调查 / 焦点小组 / 深度访谈 / 辩论讨论）
- AI / 人类主持人无缝切换
- WebSocket 实时流式通信
- Docker 一键部署
- 问卷模板库（满意度调查、市场调研、产品反馈）
- 问卷导入导出（JSON / 问卷星 / 腾讯问卷）
- Jinja2 提示词模板系统
