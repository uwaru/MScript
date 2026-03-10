# MScript - 基于 Mihomo 的服务端多协议一键部署脚本

<div align="center">

**一键部署多种代理协议的自动化脚本**

</div>

---

## 📖 简介

MScript 是一个基于 Mihomo 的多协议部署管理工具,提供友好的交互式界面,支持一键部署和管理多种代理协议。无需复杂配置,适合新手和进阶用户。

## ✨ 功能特性

- 🚀 **一键部署** - 自动化安装流程
- ⚒️ **部署方式“双料特工”** - Systemd 和 Docker 双模式
- 🔧 **多协议支持** - 支持 5+ 种主流代理协议
- 🎯 **双模式选择** - TLS 和 Reality 模式任你选择
- 🔒 **证书管理** - 自动申请和续期 SSL 证书
- 📊 **服务管理** - 内置服务状态监控和日志查看
- 🎨 **友好界面** - 清晰的菜单和详细的提示信息
- 📋 **多格式输出** - YAML、Compact、URI 三种配置格式

## 🌐 支持协议

| 协议                 | TLS 模式 | Reality 模式 | 特点                                                  |
| -------------------- | -------- | ------------ | ----------------------------------------------------- |
| **AnyTLS**           | ✅       | ❌           | 安全的 TLS 加密协议                                   |
| **Vless**            | ✅       | ✅           | 支持 xtls-rprx-vision 流控                            |
| **Trojan**           | ✅       | ✅           | 伪装成 HTTPS 流量                                     |
| **Mieru**            | ❌       | ❌           | 简单轻量的代理协议                                    |
| **TUIC V5**          | ✅       | ❌           | 基于 QUIC 的高性能代理                                |
| **Hysteria2**        | ✅       | ❌           | 专为不稳定网络优化                                    |
| **Vless Encryption** | ❌       | ❌           | 后量子安全加密协议                                    |
| **ShadowSocks**      | ❌       | ❌           | 支持 2022 新版和传统加密方法以及 ShadowTLS 和 Kcp-tun |

## 🚀 快速开始

### 系统要求

- **操作系统**: Ubuntu 18.04+, Debian 10+, CentOS 7+
- **权限**: Root 用户权限
- **架构**: x86_64, ARM64, ARMv7, ARMv6
- **网络**: 能够访问 GitHub 和证书颁发机构

### 一键安装

1. 下载仓库并设置工作目录(这一步可能需要先安装 unzip，请使用 sudo apt install unzip 命令安装。)

```bash
wget https://github.com/uwaru/MScript/archive/refs/heads/main.zip&&unzip main.zip&&cd MScript-main
```

2. 安装依赖

```
bash install_dependencies.sh
```

3. 运行主程序

```
bash run.sh
```

**注意：若要选择使用自签证书，请在一开始的输入域名处输入服务器 IP。若有自签任意域名证书需求，请在最后导入客户端配置后自行将服务器地址从你自签的域名改为 IP，并在 SNI 处填写你之前输入的域名。**

## 手动安装依赖

如果一键安装失败，可以手动安装：

### Ubuntu/Debian 系统

```bash
# 更新软件源
apt update

# 安装系统依赖
apt install -y curl wget gzip openssl uuid-runtime socat git unzip python3 python3-pip

# 安装 Python 虚拟环境支持（重要！）
apt install -y python3-venv

# 安装 Python 包
pip3 install sh
```

### CentOS/RHEL 7 系统

```bash
# 更新软件源
yum update -y

# 安装系统依赖
yum install -y curl wget gzip openssl util-linux socat git unzip tar python3 python3-pip

# CentOS/RHEL 的 Python3 通常已包含 venv 模块
# 如果 python3 -m venv 不可用，安装 virtualenv
yum install -y python3-virtualenv

# 安装 Python 包
pip3 install sh
```

### CentOS/RHEL 8+ / Fedora 系统

```bash
# 更新软件源
dnf upgrade -y

# 安装系统依赖
dnf install -y curl wget gzip openssl util-linux socat git unzip python3 python3-pip

# 如果需要，安装 virtualenv
dnf install -y python3-virtualenv

# 安装 Python 包
pip3 install sh
```

### Arch Linux 系统

```bash
# 同步并更新系统
pacman -Syu --noconfirm

# 安装系统依赖
pacman -S --noconfirm curl wget gzip openssl util-linux socat git unzip python python-pip

# Arch 的 Python 已包含 venv 模块
# 安装 Python 包
pip3 install sh
```

### Alpine Linux 系统

```bash
# 更新软件源
apk update

# 安装系统依赖
apk add --no-cache curl wget gzip openssl util-linux socat git unzip python3 py3-pip

# Alpine 的 Python3 已包含 venv 模块
# 安装 Python 包
pip3 install sh
```

### 验证安装

```bash
# 检查 Python 版本（需要 3.6+）
python3 --version

# 检查 venv 模块是否可用
python3 -m venv --help

# 检查 pip
pip3 --version

# 检查其他工具
curl --version
git --version
uuidgen --version
```

### 创建虚拟环境（在 MScript-main 目录中）

```bash
cd MScript-main

# 创建虚拟环境
python3 -m venv mscript-env

# 激活虚拟环境
source mscript-env/bin/activate

# 在虚拟环境中安装 Python 包
pip install sh
pip install pyyaml

# 退出虚拟环境
deactivate
```

## 📚 详细文档

### 使用流程

1. **启动程序**

   ```bash
   python3 MScript.py
   ```

2. **选择操作**

   - `1` - 安装协议
   - `2` - 卸载 Mihomo
   - `3` - 查看服务状态
   - `4` - 重启服务
   - `5` - 查看日志
   - `0` - 退出程序

3. **选择协议**

   - 根据需求选择要部署的协议

4. **配置参数**

   - **传输模式**: TLS 或 Reality
   - **域名**: (TLS 模式需要)
   - **邮箱**: (申请正式证书需要)
   - **端口**: 留空随机生成
   - **密码/UUID**: 留空自动生成

5. **获取配置**

   - 安装完成后会显示三种格式的客户端配置
   - 复制到客户端即可使用

### TLS 模式 vs Reality 模式

#### TLS 模式

- ✅ 使用真实域名和 SSL 证书
- ✅ 兼容性好,所有客户端支持
- ⚠️ 需要域名并解析到服务器
- ⚠️ 需要开放 80 端口(证书验证)

#### Reality 模式

- ✅ 无需域名和证书
- ✅ 更加隐蔽,难以检测
- ✅ 伪装成其他网站的流量
- ⚠️ 需要客户端支持 Reality

### 证书选择

#### 正式证书 (推荐)

- 使用 acme.sh 自动申请 Let's Encrypt 证书
- 自动续期,无需手动维护
- 客户端无需额外配置

#### 自签证书

- 快速生成,无需域名
- 需要客户端设置 `skip-cert-verify: true`
- 适合测试环境

## 🔧 服务管理

### 常用命令

```bash
# 查看服务状态
systemctl status mihomo

# 启动服务
systemctl start mihomo

# 停止服务
systemctl stop mihomo

# 重启服务
systemctl restart mihomo

# 查看实时日志
journalctl -u mihomo -f

# 查看最近日志
journalctl -u mihomo -n 100
```

### 配置文件位置

- **配置文件**: `/root/.config/mihomo/config.yaml`
- **证书文件**: `/root/.config/mihomo/server.crt`
- **私钥文件**: `/root/.config/mihomo/server.key`
- **服务文件**: `/etc/systemd/system/mihomo.service`

### 防火墙设置

```bash
# Ubuntu/Debian
sudo ufw allow 端口号/tcp
sudo ufw allow 端口号/udp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=端口号/tcp
sudo firewall-cmd --permanent --add-port=端口号/udp
sudo firewall-cmd --reload
```

## 🎯 配置示例

### Vless Reality 配置

```yaml
- name: Vless|Reality|www.microsoft.com
  server: 1.2.3.4
  type: vless
  port: 12345
  uuid: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  network: tcp
  udp: true
  tls: true
  flow: xtls-rprx-vision
  servername: www.microsoft.com
  reality-opts:
    public-key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    short-id: xxxxxxxxxxxx
  client-fingerprint: chrome
```

### Trojan TLS 配置

```yaml
- name: Trojan|TLS|proxy.example.com
  server: proxy.example.com
  type: trojan
  port: 443
  password: your-password-here
  udp: true
  sni: proxy.example.com
  skip-cert-verify: false
  client-fingerprint: chrome
```

## ❓ 常见问题

<details> <summary><b>Q: 证书申请失败怎么办?</b></summary>

A: 请检查:

1. 域名是否正确解析到服务器 IP
2. 防火墙是否开放了 80 端口
3. 80 端口是否被其他程序占用
4. 服务器是否能访问 Let's Encrypt 服务器

</details> <details> <summary><b>Q: Reality 模式如何选择伪装域名?</b></summary>

A: 建议选择:

- 大型网站(如 Microsoft, Apple, Google)
- 支持 TLS 1.3 的网站
- 访问量大的网站
- 默认的 www.microsoft.com 是不错的选择

</details> <details> <summary><b>Q: 如何更换端口?</b></summary>

A:

1. 编辑配置文件: `nano /root/.config/mihomo/config.yaml`
2. 修改 `port` 字段
3. 重启服务: `systemctl restart mihomo`
4. 更新防火墙规则

</details> <details> <summary><b>Q: 服务无法启动怎么办?</b></summary>

A: 查看日志排查:

```bash
journalctl -u mihomo -n 50
```

常见原因:

- 端口被占用
- 配置文件格式错误
- 证书文件不存在
- 权限问题

</details> <details> <summary><b>Q: 如何完全卸载?</b></summary>

A:

1. 使用脚本卸载功能(推荐)
2. 或手动执行:

```bash
systemctl stop mihomo
systemctl disable mihomo
rm -rf /root/.config/mihomo
rm /usr/local/bin/mihomo
rm /etc/systemd/system/mihomo.service
systemctl daemon-reload
```

3.如需完全删除脚本文件请在用户目录下运行如下命令

```bash
rm MScript-main -r
```

</details>

## 🔒 安全建议

1. **定期更新** - 保持系统和脚本最新版本
2. **强密码** - 使用复杂的密码/UUID
3. **防火墙** - 只开放必要端口
4. **监控日志** - 定期检查异常访问
5. **备份配置** - 定期备份配置文件

## 📝 更新日志

### v2.0.0 (2025-11-25)

- 正式添加对 Docker 部署的支持
- 所有的配置生成方式都改为使用 Pyyaml

### v1.5.0 (2025-11-24)

- 将部分子类共有的方法提升到基类里
- 代码易读性优化
- 新增对 Vless Encryption 协议的支持

### v1.0.0 (2025-11-22)

- ✨ 首次发布
- ✅ 支持 6 种协议
- ✅ TLS 和 Reality 双模式
- ✅ 自动证书管理
- ✅ 完整的服务管理功能

## ⚠️ 目前已知的存在的问题
1.在使用acme.sh自动更新管理证书时，更新后的证书不会自动替换掉mihomo工作目录下的过期证书，当前脚本版本可以运行以下命令解决该问题：
#使用普通方式进行安装的（请将example.com替换为你正在使用的域名）
```
~/.acme.sh/acme.sh --install-cert -d example.com \
--key-file       /root/.config/mihomo/server.key \
--fullchain-file /root/.config/mihomo/server.crt \
--reloadcmd      "systemctl restart mihomo"
```

#使用docker方式进行安装的（请将example替换为你正在使用的域名）
```
~/.acme.sh/acme.sh --install-cert -d example.com \
--key-file       /root/.config/mihomo/server.key \
--fullchain-file /root/.config/mihomo/server.crt \
--reloadcmd      "docker restart mihomo"
```

## 📄 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](https://claude.ai/chat/LICENSE) 文件

## 🙏 致谢

- [MetaCubeX/mihomo](https://github.com/MetaCubeX/mihomo) - 核心代理程序
- [acmesh-official/acme.sh](https://github.com/acmesh-official/acme.sh) - SSL 证书管理
- [Let's Encrypt](https://letsencrypt.org/) - 免费 SSL 证书
- [Mihomo Scripts](https://github.com/iahfdoa/mihomo-scripts) - 本项目部分代码引用自该项目
- [Claude ](https://claude.ai/)- 特别鸣谢！天下才共一石，Claude 独得 9.5 斗，我得 0.5 斗

## ⚠️ 免责声明

本工具仅供学习交流使用,请遵守当地法律法规。使用本工具产生的任何后果由使用者自行承担。

代码基本为 AI 生成，文档也为 AI 生成。本人代码能力较弱，BUG 反馈后处理较慢请见谅。我可以保证截止代码完成时代码中每一个模块均实际测试过（在 Ubuntu22.04.5 LTS 环境下）。我主要是做一个抛砖引玉的工作，希望有大佬能帮助完善该脚本。

## 📄 下一步计划

1. 听取反馈，及时解决存在的 BUG。
2. 进一步组织代码，将协议部署模块类目前共有的一些方法提升到基类里。
3. 通过转为使用 pyyaml 生成配置文件等操作使代码更易读且更便于维护。
4. 添加 shadowsocks 等协议的支持。
5. 添加对 Docker 部署的支持。
6. ......

## 📧 联系方式

- Issue: [GitHub Issues](https://github.com/uwaru/MScript/issues)

---

<div align="center">

**如果这个项目对你有帮助,请给个 ⭐ Star 支持一下!**

Made with ❤️ by [uwaru]

</div>
