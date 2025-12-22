#!/bin/bash

# 获取脚本所在目录并切换到该目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 定义端口号
PORT=5001

echo "=================================="
echo "翻译质量检查工具 - 启动服务器"
echo "=================================="
echo ""
echo "工作目录: $SCRIPT_DIR"
echo ""

# 检查并清理端口占用
echo "检查端口 $PORT 占用情况..."
PID=$(lsof -ti:$PORT)
if [ ! -z "$PID" ]; then
    echo "⚠️  端口 $PORT 已被进程 $PID 占用"
    echo "正在终止进程..."
    kill -9 $PID 2>/dev/null
    sleep 1
    echo "✓ 端口已清理"
else
    echo "✓ 端口 $PORT 可用"
fi
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 未找到虚拟环境，正在创建..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败"
        echo ""
        echo "按任意键退出..."
        read -n 1
        exit 1
    fi
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 跳过依赖检查（如需安装依赖，请手动运行）
# 如果需要安装依赖，取消下面这行的注释：
# pip install -q -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

# 启动服务器
echo ""
echo "=================================="
echo "启动Flask服务器..."
echo "=================================="
echo ""
echo "访问地址: http://localhost:$PORT"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 在后台启动服务器
python app.py &
SERVER_PID=$!

# 等待服务器启动
echo "等待服务器启动..."
sleep 2

# 检查服务器是否成功启动
if ps -p $SERVER_PID > /dev/null; then
    echo "✓ 服务器进程已启动 (PID: $SERVER_PID)"
    echo ""

    # 等待服务器完全就绪（检查端口是否可访问）
    echo "等待服务器就绪..."
    MAX_WAIT=15
    WAITED=0
    while [ $WAITED -lt $MAX_WAIT ]; do
        if curl -s http://localhost:$PORT/ > /dev/null 2>&1; then
            echo "✓ 服务器已就绪"
            break
        fi
        sleep 1
        WAITED=$((WAITED + 1))
        echo -n "."
    done
    echo ""

    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "⚠️  服务器启动超时，但进程仍在运行"
        echo "   请手动访问: http://localhost:$PORT"
    else
        # 自动打开浏览器
        echo "正在打开浏览器..."
        open http://localhost:$PORT
    fi
    echo ""
    echo "=================================="
    echo "服务器正在运行中..."
    echo "=================================="
    echo ""
    echo "提示："
    echo "  - 关闭此窗口将停止服务器"
    echo "  - 或按 Ctrl+C 停止服务器"
    echo ""

    # 等待服务器进程
    wait $SERVER_PID
else
    echo "❌ 服务器启动失败"
    echo ""
    echo "按任意键退出..."
    read -n 1
    exit 1
fi

