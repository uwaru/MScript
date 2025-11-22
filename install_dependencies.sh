#!/usr/bin/env bash
set -e

# ==========
# MScript 依赖安装脚本（已添加 unzip）
# ==========

echo "🔧 开始安装 MScript 所需依赖..."
echo ""

# 基础依赖包列表（已加入 unzip）
BASE_PKGS=(curl openssl wget gzip socat git unzip)
PYTHON_PKG=""
PIP_PKG=""
UUID_PKG=""
EXTRA_PKGS=()

# 检测包管理器并安装依赖
if command -v apt &>/dev/null; then
    echo "📦 检测到 APT 包管理器 (Debian/Ubuntu)"
    PYTHON_PKG="python3"
    PIP_PKG="python3-pip"
    UUID_PKG="uuid-runtime"

    echo "🔄 正在更新系统..."
    apt update -y
    apt upgrade -y

    echo "📥 正在安装依赖包..."
    apt install -y "${BASE_PKGS[@]}" "$PYTHON_PKG" "$PIP_PKG" "$UUID_PKG"

elif command -v yum &>/dev/null; then
    echo "📦 检测到 YUM 包管理器 (CentOS/RHEL)"
    PYTHON_PKG="python3"
    PIP_PKG="python3-pip"
    UUID_PKG="util-linux"
    EXTRA_PKGS=(tar)

    echo "🔄 正在更新系统..."
    yum update -y

    echo "📥 正在安装依赖包..."
    yum install -y "${BASE_PKGS[@]}" "$PYTHON_PKG" "$PIP_PKG" "$UUID_PKG" "${EXTRA_PKGS[@]}" || true

elif command -v dnf &>/dev/null; then
    echo "📦 检测到 DNF 包管理器 (Fedora/RHEL 8+)"
    PYTHON_PKG="python3"
    PIP_PKG="python3-pip"
    UUID_PKG="util-linux"

    echo "🔄 正在更新系统..."
    dnf upgrade -y

    echo "📥 正在安装依赖包..."
    dnf install -y "${BASE_PKGS[@]}" "$PYTHON_PKG" "$PIP_PKG" "$UUID_PKG"

elif command -v pacman &>/dev/null; then
    echo "📦 检测到 Pacman 包管理器 (Arch Linux)"
    PYTHON_PKG="python"
    PIP_PKG="python-pip"
    UUID_PKG="util-linux"

    echo "🔄 正在同步系统并更新..."
    pacman -Syu --noconfirm

    echo "📥 正在安装依赖包..."
    pacman -S --noconfirm "${BASE_PKGS[@]}" "$PYTHON_PKG" "$PIP_PKG" "$UUID_PKG"

elif command -v apk &>/dev/null; then
    echo "📦 检测到 APK 包管理器 (Alpine Linux)"
    PYTHON_PKG="python3"
    PIP_PKG="py3-pip"
    UUID_PKG="util-linux"

    echo "🔄 正在更新 APK 软件库..."
    apk update

    echo "📥 正在安装依赖包..."
    apk add --no-cache "${BASE_PKGS[@]}" "$PYTHON_PKG" "$PIP_PKG" "$UUID_PKG"

else
    echo "❌ 无法识别包管理器"
    echo "支持的系统: Debian/Ubuntu, CentOS/RHEL, Fedora, Arch Linux, Alpine Linux"
    echo "请手动安装以下依赖:"
    echo "  - curl"
    echo "  - openssl"
    echo "  - wget"
    echo "  - gzip"
    echo "  - socat"
    echo "  - git"
    echo "  - unzip"
    echo "  - python3"
    echo "  - pip3"
    echo "  - uuidgen (包名: uuid-runtime 或 util-linux)"
    exit 1
fi

echo ""
echo "🔍 验证系统依赖安装..."

# 验证所有必要命令是否可用
MISSING_CMDS=()
for cmd in curl wget gzip openssl uuidgen socat git python3 unzip; do
    if ! command -v "$cmd" &>/dev/null; then
        MISSING_CMDS+=("$cmd")
    fi
done

if [ ${#MISSING_CMDS[@]} -gt 0 ]; then
    echo "❌ 以下命令未找到:"
    for cmd in "${MISSING_CMDS[@]}"; do
        echo "   - $cmd"
    done
    echo ""
    echo "请手动安装缺失的依赖"
    exit 1
fi

# 验证 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

echo "✓ Python 版本: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 6 ]); then
    echo "❌ Python 版本过低,需要 Python 3.6 或更高版本"
    exit 1
fi

# 验证 Git 版本
GIT_VERSION=$(git --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1)
echo "✓ Git 版本: $GIT_VERSION"

echo ""
echo "🐍 安装 Python 软件包..."

# 确保 pip 可用
if ! command -v pip3 &>/dev/null; then
    echo "❌ pip3 未找到,尝试使用 python3 -m pip"
    PIP_CMD="python3 -m pip"
else
    PIP_CMD="pip3"
fi

# 升级 pip
echo "正在升级 pip..."
$PIP_CMD install --upgrade pip 2>/dev/null || python3 -m pip install --upgrade pip

# 安装 sh 库
echo "正在安装 sh 库..."
$PIP_CMD install sh || python3 -m pip install sh

# 验证 sh 库是否安装成功
if python3 -c "import sh" 2>/dev/null; then
    echo "✓ sh 库安装成功"
else
    echo "❌ sh 库安装失败"
    echo "请手动安装: pip3 install sh"
    exit 1
fi

echo ""
echo "✅ 所有依赖安装完成！"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "已安装的系统工具:"
echo "  ✓ curl      - 网络请求"
echo "  ✓ wget      - 文件下载"
echo "  ✓ gzip      - 文件压缩/解压"
echo "  ✓ openssl   - SSL/TLS 工具"
echo "  ✓ socat     - 网络工具 (acme.sh 需要)"
echo "  ✓ git       - 版本控制工具"
echo "  ✓ unzip     - 文件解压"
echo "  ✓ uuidgen   - UUID 生成器"
echo ""
echo "已安装的 Python 环境:"
echo "  ✓ python3   - Python 解释器 (版本 $PYTHON_VERSION)"
echo "  ✓ pip3      - Python 包管理器"
echo "  ✓ sh        - Python Shell 命令库"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
