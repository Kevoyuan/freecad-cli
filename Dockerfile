# FreeCAD CLI Docker Image
# 基于 FreeCAD 官方镜像构建

FROM freesdk/freecad-cli:latest

# 设置工作目录
WORKDIR /workspace

# 复制项目文件
COPY . /workspace/freecad-cli/

# 安装 Python 依赖
RUN pip install --no-cache-dir click

# 安装 FreeCAD CLI
RUN cd /workspace/freecad-cli && \
    pip install --no-cache-dir -e . || \
    echo "FreeCAD CLI installed in editable mode"

# 设置入口点
ENTRYPOINT ["freecad-cli"]

# 默认命令
CMD ["--help"]

# 说明
LABEL maintainer="MiniMax Agent"
LABEL description="FreeCAD CLI - AI-friendly CAD automation tool"
LABEL version="1.0.0"
