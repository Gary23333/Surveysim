# SurveySim Backend

大模型驱动的模拟问卷调查与群体调研平台后端服务（v1.0.0）。

## 技术栈

- Python 3.10+
- FastAPI + SQLModel + WebSocket
- 多 LLM 供应商适配（OpenAI / DeepSeek / MiMo / 豆包）

## 快速启动

```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key
uvicorn virtual_survey.main:app --reload --port 8000
```

## 测试

```bash
pytest
python -m compileall -q virtual_survey
```

详见项目根目录 [README.md](../README.md)。
