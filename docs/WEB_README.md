# 翻译质量检查工具 - Web版使用说明

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（如果还没有）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动服务器

**方法1: 使用启动脚本（推荐）**
```bash
./start_server.sh
```

**方法2: 手动启动**
```bash
source venv/bin/activate
python app.py
```

### 3. 访问网页

打开浏览器访问: **http://localhost:5001**

---

## 📖 使用说明

### 网页界面

1. **输入原文和译文**
   - 在"原文 (Source Text)"文本框中输入原文
   - 在"译文 (Target Text)"文本框中输入译文

2. **调整参数（可选）**
   - **相似度阈值**: 低于此值视为"相似度低"（默认0.7）
   - **强制拆散阈值**: 低于此值的对齐组将被拆散为缺失+增添（默认0.5）

3. **点击"开始检测"按钮**
   - 等待检测完成（首次运行会加载模型，需要几秒钟）

4. **查看结果**
   - **统计信息**: 显示句子数、对齐组数等
   - **发现的问题**: 显示缺失、增添、相似度低的数量
   - **详细报告**: CSV格式的表格，显示每个句子的对齐情况

5. **导出结果**
   - 点击"💾 下载CSV"按钮下载报告
   - 点击"📋 复制表格"按钮复制到剪贴板

---

## 🔧 API接口

### POST /api/check

检查翻译质量

**请求体**:
```json
{
    "source_text": "原文",
    "target_text": "译文",
    "similarity_threshold": 0.7,
    "force_split_threshold": 0.5
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "csv": "CSV格式的报告",
        "summary": {
            "src_count": 5,
            "tgt_count": 7,
            "alignment_count": 5,
            "similarity_threshold": 0.7
        },
        "issues": {
            "omissions": [...],
            "additions": [...],
            "low_similarity": [...]
        },
        "force_split_count": 2
    }
}
```

### GET /api/health

健康检查

**响应**:
```json
{
    "status": "ok",
    "model_loaded": true
}
```

---

## 📊 检测结果说明

### 异常类型

| 类型 | 说明 | 颜色标记 |
|------|------|---------|
| **缺失 (Omission)** | 原文句子没有对应的译文 | 🔴 红色 |
| **增添 (Addition)** | 译文句子没有对应的原文 | 🔴 红色 |
| **相似度低 (Low Similarity)** | 对齐的句子对语义相似度低于阈值 | 🟡 黄色 |
| **OK** | 正常对齐，相似度高 | 🟢 绿色 |

### CSV报告格式

| 列名 | 说明 |
|------|------|
| 原文 (Source) | 原文句子 |
| 译文 (Target) | 译文句子 |
| 源索引 | 原文句子索引 |
| 目标索引 | 译文句子索引 |
| 相似度 (Similarity) | 语义相似度（0-1） |
| 异常情况 (Exception) | 异常类型或OK |

---

## ⚙️ 配置说明

### 模型路径

模型文件位于项目根目录下的 `labse_onnx/` 文件夹：

```
语义对齐/
├── labse_onnx/          # LaBSE ONNX模型
│   ├── model.onnx
│   ├── config.json
│   ├── tokenizer.json
│   └── ...
├── app.py               # Flask服务器
├── translation_qa_tool.py
├── labse_onnx_encoder.py
└── ...
```

### 参数调优

**相似度阈值 (similarity_threshold)**:
- 默认: 0.7
- 范围: 0.0 - 1.0
- 建议: 0.6 - 0.8

**强制拆散阈值 (force_split_threshold)**:
- 默认: 0.5
- 范围: 0.0 - 1.0
- 建议: 0.4 - 0.6

---

## 🐛 故障排除

### 问题1: 端口被占用

```bash
# 修改 app.py 中的端口号
app.run(host='0.0.0.0', port=5001, debug=True)  # 改为5001
```

### 问题2: 模型加载失败

确保 `labse_onnx/` 文件夹存在且包含以下文件：
- model.onnx
- config.json
- tokenizer.json
- vocab.txt

### 问题3: 依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

---

## 📝 技术栈

- **后端**: Flask 3.0+
- **前端**: 原生HTML/CSS/JavaScript
- **对齐算法**: Bertalign
- **编码模型**: LaBSE (ONNX格式)
- **运行时**: ONNX Runtime

---

## 🎯 性能优化

### 批量处理

服务器会复用QA工具实例，避免重复加载模型。首次请求会较慢（加载模型），后续请求会快很多。

### 内存占用

- 模型加载后约占用 **500MB** 内存
- 建议服务器至少有 **2GB** 可用内存

---

## 📄 许可证

本项目仅供学习和研究使用。

