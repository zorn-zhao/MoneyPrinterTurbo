# 第一阶段：构建依赖
FROM python:3.11-slim-bullseye as builder

# 1. 配置基础环境
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends git ffmpeg imagemagick && \
    rm -rf /var/lib/apt/lists/* && \
    sed -i '/<policy domain="path" rights="none" pattern="@\*"/d' /etc/ImageMagick-6/policy.xml

# 2. 创建并激活虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 3. 安装Python依赖
WORKDIR /MoneyPrinterTurbo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

# 4. 明确复制组件到特定目录（关键修复）
RUN mkdir -p /build-output/bin /build-output/lib && \
    cp /usr/bin/git /build-output/bin/ && \
    cp /usr/bin/ffmpeg /build-output/bin/ && \
    cp -r /usr/lib/x86_64-linux-gnu/ImageMagick-6* /build-output/lib/

# 第二阶段：运行时镜像
FROM python:3.11-slim-bullseye

# 1. 预创建目录结构
RUN mkdir -p /MoneyPrinterTurbo /usr/lib/x86_64-linux-gnu && \
    chmod -R 777 /MoneyPrinterTurbo

# 2. 从构建阶段复制组件
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build-output/bin/git /usr/bin/git
COPY --from=builder /build-output/bin/ffmpeg /usr/bin/ffmpeg 
COPY --from=builder /build-output/lib/ /usr/lib/x86_64-linux-gnu/

# 3. 设置环境变量
ENV PATH="/opt/venv/bin:$PATH" \
    IMAGEMAGICK_BINARY="/usr/lib/x86_64-linux-gnu/ImageMagick-6.9.11/bin/convert"

# 4. 复制应用代码
WORKDIR /MoneyPrinterTurbo
COPY . .

# 5. 处理配置文件
RUN [ -f config.example.toml ] && cp config.example.toml config.toml || true && \
    chmod 777 config.toml

# 6. 权限设置
RUN useradd -u 1000 appuser && \
    chown -R appuser /MoneyPrinterTurbo

USER appuser

CMD ["python", "-m", "streamlit", "run", "./webui/Main.py", "--server.port=8501"]
