# 使用轻量级 Python 镜像
FROM python:3.11-slim

# 安装基础工具
RUN apt-get update && apt-get install -y \
    curl \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# 安装 Typst (下载官方二进制)
# 注意：这里下载的是 aarch64 (ARM) 版本，因为你是在 Mac M1/M2 上运行 Docker 吗？
# 如果是云服务器 (x86)，通常需要 x86_64-unknown-linux-musl
# 我们可以写一个脚本自动检测架构，或者简单起见，假设是 x86 (通常生产环境)
# 鉴于我们在本地 Mac 上开发，我先下载通用脚本安装，或者直接使用 cargo 安装
# 这里的脚本会自动检测架构
RUN curl -fsSL https://github.com/typst/typst/releases/download/v0.12.0/typst-x86_64-unknown-linux-musl.tar.xz | tar -xJ \
    && mv typst-x86_64-unknown-linux-musl/typst /usr/local/bin/ \
    && rm -rf typst-x86_64-unknown-linux-musl

# 设置工作目录
WORKDIR /app

# 安装 Python 依赖
RUN pip install fastapi uvicorn pydantic

# 复制应用代码
COPY . /app

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]