#!/usr/bin/env bash
set -e

# ==========
# MScript 依赖安装脚本
# ==========

echo "🔧 开始安装 MScript 所需依赖..."
echo ""

# 基础依赖包列表
BASE_PKGS=(curl openssl wget gzip socat git unzip)
PYTHON_PKG=""
PIP_PKG=""
UUID_PKG=""
VENV_PKG=""
EXTRA_PKGS=()

# 检测包管理器并安装依赖
if command -v apt &>/dev/null; then
    echo "📦 检测到 APT 包管理器 (Debian/Ubuntu)"
    PYTHON_PKG="python3"
    PIP_PKG="python3-pip"
    UUID_PKG="uuid-runtime"
    # venv 包名将在检测 Python 版本后设置

    echo "🔄 正在更新系统..."
    apt update -y
    apt upgrade -y

    echo "📥 正在安装基础依赖包..."
    apt install -y "${BASE_PKGS[@]}" "$PYTHON_PKG" "$PIP_PKG" "$UUID_PKG"

elif command -v yum &>/dev/null; then
    echo "📦 检测到 YUM 包管理器 (CentOS/RHEL)"
    PYTHON_PKG="python3"
    PIP_PKG="python3-pip"
    UUID_PKG="util-linux"
    EXTRA_PKGS=(tar)

    echo "🔄 正在更新系统..."
    yum update -y

    echo "📥 正在安装基础依赖包..."
    yum install -y "${BASE_PKGS[@]}" "$PYTHON_PKG" "$PIP_PKG" "$UUID_PKG" "${EXTRA_PKGS[@]}" || true

elif command -v dnf &>/dev/null; then
    echo "📦 检测到 DNF 包管理器 (Fedora/RHEL 8+)"
    PYTHON_PKG="python3"
    PIP_PKG="python3-pip"
    UUID_PKG="util-linux"

    echo "🔄 正在更新系统..."
    dnf upgrade -y

    echo "📥 正在安装基础依赖包..."
    dnf install -y "${BASE_PKGS[@]}" "$PYTHON_PKG" "$PIP_PKG" "$UUID_PKG"

elif command -v pacman &>/dev/null; then
    echo "📦 检测到 Pacman 包管理器 (Arch Linux)"
    PYTHON_PKG="python"
    PIP_PKG="python-pip"
    UUID_PKG="util-linux"

    echo "🔄 正在同步系统并更新..."
    pacman -Syu --noconfirm

    echo "📥 正在安装基础依赖包..."
    pacman -S --noconfirm "${BASE_PKGS[@]}" "$PYTHON_PKG" "$PIP_PKG" "$UUID_PKG"

elif command -v apk &>/dev/null; then
    echo "📦 检测到 APK 包管理器 (Alpine Linux)"
    PYTHON_PKG="python3"
    PIP_PKG="py3-pip"
    UUID_PKG="util-linux"

    echo "🔄 正在更新 APK 软件库..."
    apk update

    echo "📥 正在安装基础依赖包..."
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
    echo "  - python3-venv (或对应的虚拟环境包)"
    echo "  - uuidgen (包名: uuid-runtime 或 util-linux)"
    exit 1
fi

echo ""
echo "🔍 验证系统依赖安装..."

# 验证所有必要命令是否可用
MISSING_CMDS=()
for cmd in curl wget gzip openssl uuidgen socat git python3; do
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
echo "🐍 安装 Python 虚拟环境管理..."

# 根据不同的包管理器和 Python 版本安装 venv
if command -v apt &>/dev/null; then
    # Debian/Ubuntu: python3.x-venv
    VENV_PKG="python${PYTHON_VERSION}-venv"
    echo "📦 安装 $VENV_PKG"
    apt install -y "$VENV_PKG" || {
        echo "⚠️  安装 $VENV_PKG 失败,尝试通用包名..."
        apt install -y python3-venv || {
            echo "❌ 无法安装 Python 虚拟环境包"
            exit 1
        }
    }
elif command -v yum &>/dev/null; then
    # CentOS/RHEL: 通常包含在 python3 中,或需要 python3-virtualenv
    echo "📦 检查 Python 虚拟环境支持..."
    if ! python3 -m venv --help &>/dev/null; then
        echo "正在安装 python3-virtualenv..."
        yum install -y python3-virtualenv || echo "⚠️  可能需要手动配置虚拟环境"
    fi
elif command -v dnf &>/dev/null; then
    # Fedora/RHEL 8+
    echo "📦 检查 Python 虚拟环境支持..."
    if ! python3 -m venv --help &>/dev/null; then
        echo "正在安装 python3-virtualenv..."
        dnf install -y python3-virtualenv || echo "⚠️  可能需要手动配置虚拟环境"
    fi
elif command -v pacman &>/dev/null; then
    # Arch Linux: 通常包含在 python 包中
    echo "✓ Arch Linux 的 Python 已包含 venv 模块"
elif command -v apk &>/dev/null; then
    # Alpine Linux: 通常包含在 python3 中
    echo "✓ Alpine Linux 的 Python 已包含 venv 模块"
fi

# 验证 venv 模块是否可用
echo "🔍 验证 Python venv 模块..."
if python3 -m venv --help &>/dev/null; then
    echo "✓ Python venv 模块可用"
else
    echo "❌ Python venv 模块不可用"
    echo "请手动安装:"
    echo "  - Debian/Ubuntu: apt install python${PYTHON_VERSION}-venv"
    echo "  - CentOS/RHEL:   yum install python3-virtualenv"
    echo "  - Fedora:        dnf install python3-virtualenv"
    exit 1
fi

# 创建虚拟环境
echo "🐍 创建虚拟环境 mscript-env..."
if [ -d "mscript-env" ]; then
    echo "⚠️  虚拟环境目录已存在"
    # 检查虚拟环境是否完整
    if [ ! -f "mscript-env/bin/activate" ]; then
        echo "⚠️  虚拟环境不完整,删除并重新创建..."
        rm -rf mscript-env
        python3 -m venv mscript-env || {
            echo "❌ 创建虚拟环境失败"
            echo ""
            echo "可能的原因："
            echo "1. Python venv 模块未正确安装"
            echo "2. 磁盘空间不足"
            echo "3. 权限不足"
            echo ""
            echo "请尝试手动创建："
            echo "  python3 -m venv mscript-env"
            exit 1
        }
    else
        echo "✓ 虚拟环境完整,跳过创建"
    fi
else
    python3 -m venv mscript-env 2>&1 | tee /tmp/venv_error.log || {
        echo "❌ 创建虚拟环境失败"
        echo ""
        echo "错误信息："
        cat /tmp/venv_error.log
        echo ""
        echo "可能的原因："
        echo "1. Python venv 模块未正确安装"
        echo "2. 磁盘空间不足"
        echo "3. 权限不足"
        echo ""
        echo "请尝试："
        echo "  - 检查 Python venv: python3 -m venv --help"
        echo "  - 检查磁盘空间: df -h"
        echo "  - 手动创建测试: python3 -m venv test_env"
        exit 1
    }
    echo "✓ 虚拟环境创建成功"
fi

# 验证虚拟环境文件
if [ ! -f "mscript-env/bin/activate" ]; then
    echo "❌ 虚拟环境创建异常: activate 脚本不存在"
    echo "虚拟环境目录内容:"
    ls -la mscript-env/ || echo "无法列出目录内容"
    exit 1
fi

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source mscript-env/bin/activate || {
    echo "❌ 激活虚拟环境失败"
    echo "虚拟环境路径: $(pwd)/mscript-env"
    exit 1
}
echo "✅ 虚拟环境已激活"

# 确保 pip 可用
if ! command -v pip &>/dev/null && ! command -v pip3 &>/dev/null; then
    echo "❌ pip 未找到,尝试使用 python -m pip"
    PIP_CMD="python -m pip"
else
    PIP_CMD="pip"
fi

# 升级 pip
echo "⬆️  正在升级 pip..."
$PIP_CMD install --upgrade pip || {
    echo "⚠️  升级 pip 失败,继续使用当前版本"
}

# 显示 pip 版本
PIP_VERSION=$($PIP_CMD --version | grep -oP '\d+\.\d+\.\d+' | head -1)
echo "✓ pip 版本: $PIP_VERSION"

# 安装 sh 库
echo "📦 正在安装 sh 库..."
$PIP_CMD install sh || {
    echo "❌ sh 库安装失败"
    deactivate
    exit 1
}

# 验证 sh 库是否安装成功
if python -c "import sh" 2>/dev/null; then
    echo "✓ sh 库安装成功"
else
    echo "❌ sh 库安装失败"
    echo "请手动安装: pip install sh"
    deactivate
    exit 1
fi

# 安装 pyyaml 库
echo "📦 正在安装 pyyaml 库..."
$PIP_CMD install pyyaml || {
    echo "❌ pyyaml 库安装失败"
    deactivate
    exit 1
}

# 验证 pyyaml 库是否安装成功
if python -c "import yaml" 2>/dev/null; then
    echo "✓ pyyaml 库安装成功"
else
    echo "❌ pyyaml 库安装失败"
    echo "请手动安装: pip install pyyaml"
    deactivate
    exit 1
fi

# 退出虚拟环境
deactivate
echo "🚪 已退出虚拟环境"

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
echo "  ✓ unzip     - 解压工具"
echo "  ✓ uuidgen   - UUID 生成器"
echo ""
echo "已安装的 Python 环境:"
echo "  ✓ python3   - Python 解释器 (版本 $PYTHON_VERSION)"
echo "  ✓ pip       - Python 包管理器 (版本 $PIP_VERSION)"
echo "  ✓ venv      - Python 虚拟环境"
echo "  ✓ sh        - Python Shell 命令库"
echo "  ✓ pyyaml    - Python yaml  命令库"
echo ""
echo "虚拟环境位置:"
echo "  📁 $(pwd)/mscript-env"
echo ""
echo "使用虚拟环境:"
echo "  激活: source mscript-env/bin/activate"
echo "  退出: deactivate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
