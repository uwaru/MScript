# MScript - 基于Mihomo的服务端多协议一键部署脚本

<div align="center">


**一键部署多种代理协议的自动化脚本**

</div>

------

## 📖 简介

MScript 是一个基于 Mihomo 的多协议部署管理工具,提供友好的交互式界面,支持一键部署和管理多种代理协议。无需复杂配置,适合新手和进阶用户。

## ✨ 功能特性

- 🚀 **一键部署** - 自动化安装流程,无需手动配置
- 🔧 **多协议支持** - 支持 5+ 种主流代理协议
- 🎯 **双模式选择** - TLS 和 Reality 模式任你选择
- 🔒 **证书管理** - 自动申请和续期 SSL 证书
- 📊 **服务管理** - 内置服务状态监控和日志查看
- 🎨 **友好界面** - 清晰的菜单和详细的提示信息
- 📋 **多格式输出** - YAML、Compact、URI 三种配置格式

## 🌐 支持协议

| 协议          | TLS 模式 | Reality 模式 | 特点                       |
| ------------- | -------- | ------------ | -------------------------- |
| **AnyTLS**    | ✅        | ❌            | 安全的 TLS 加密协议        |
| **Vless**     | ✅        | ✅            | 支持 xtls-rprx-vision 流控 |
| **Trojan**    | ✅        | ✅            | 伪装成 HTTPS 流量          |
| **Mieru**     | ✅        | ❌            | 简单轻量的代理协议         |
| **TUIC V5**   | ✅        | ❌            | 基于 QUIC 的高性能代理     |
| **Hysteria2** | ✅        | ❌            | 专为不稳定网络优化         |

## 🚀 快速开始

### 系统要求

- **操作系统**: Ubuntu 18.04+, Debian 10+, CentOS 7+
- **权限**: Root 用户权限
- **架构**: x86_64, ARM64, ARMv7, ARMv6
- **网络**: 能够访问 GitHub 和证书颁发机构

### 一键安装

1. 下载仓库并设置工作目录

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

### 手动安装依赖

如果一键安装失败,可以手动安装:

```bash
# Ubuntu/Debian
apt update
apt install -y curl wget gzip openssl uuid-runtime socat python3 python3-pip
pip3 install sh

# CentOS/RHEL
yum install -y curl wget gzip openssl util-linux socat python3 python3-pip
pip3 install sh
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

</details>

## 🔒 安全建议

1. **定期更新** - 保持系统和脚本最新版本
2. **强密码** - 使用复杂的密码/UUID
3. **防火墙** - 只开放必要端口
4. **监控日志** - 定期检查异常访问
5. **备份配置** - 定期备份配置文件

## 📝 更新日志

### v1.0.0 (2025-11-22)

- ✨ 首次发布
- ✅ 支持 6 种协议
- ✅ TLS 和 Reality 双模式
- ✅ 自动证书管理
- ✅ 完整的服务管理功能

## 📄 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](https://claude.ai/chat/LICENSE) 文件

## 🙏 致谢

- [MetaCubeX/mihomo](https://github.com/MetaCubeX/mihomo) - 核心代理程序
- [acmesh-official/acme.sh](https://github.com/acmesh-official/acme.sh) - SSL 证书管理
- [Let's Encrypt](https://letsencrypt.org/) - 免费 SSL 证书
- [Mihomo Scripts](https://github.com/iahfdoa/mihomo-scripts) - 本项目部分代码引用自该项目
- [Claude ](https://claude.ai/)- 特别鸣谢！天下才共一石，Claude独得9.5斗，我得0.5斗

## ⚠️ 免责声明

本工具仅供学习交流使用,请遵守当地法律法规。使用本工具产生的任何后果由使用者自行承担。

代码基本为AI生成，文档也为AI生成。本人代码能力较弱，BUG反馈后处理较慢请见谅。我可以保证截止代码完成时代码中每一个模块均实际测试过（在Ubuntu22.04.5 LTS环境下）。我主要是做一个抛砖引玉的工作，希望有大佬能帮助完善该脚本。

## 📧 联系方式

- Issue: [GitHub Issues](https://github.com/uwaru/MScript/issues)

------

<div align="center">




**如果这个项目对你有帮助,请给个 ⭐ Star 支持一下!**

Made with ❤️ by [uwaru]

</div>
