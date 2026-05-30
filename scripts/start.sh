#!/bin/bash

# Virtual Survey 启动脚本

set -e

echo "🚀 启动 Virtual Survey..."

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  警告: 未设置 OPENAI_API_KEY 环境变量"
    echo "   请在 backend/.env 文件中配置"
fi

# 启动后端
echo "📦 启动后端服务..."
cd backend

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "   创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "   安装依赖..."
pip install -r requirements.txt -q

# 创建数据目录
mkdir -p data

# 启动后端
echo "   启动 FastAPI 服务..."
uvicorn virtual_survey.main:app --reload --port 8000 &
BACKEND_PID=$!

cd ..

# 启动前端
echo "📦 启动前端服务..."
cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "   安装依赖..."
    npm install -q
fi

# 启动前端
echo "   启动 Vite 开发服务器..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ Virtual Survey 已启动！"
echo ""
echo "🌐 前端地址: http://localhost:3000"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待退出信号
trap "echo ''; echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

# 保持运行
wait
