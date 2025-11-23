#!/usr/bin/env python3
"""
BaseClass.py - Mihomo 协议部署基础类
包含所有协议部署的通用功能
"""

import sh
import re
import sys
import time
import random
import json
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod


class MihomoBase(ABC):
    """Mihomo 部署基础类"""

    # ============================= 初始化 =============================
    def __init__(self):
        self.home = Path.home()
        self.cert_dir = Path("/root/.config/mihomo")  # Mihomo位置
        self.acme_sh = self.home / ".acme.sh" / "acme.sh"  # Acme.sh位置
        self.protocol_name = "Unknown"  # 子类需要覆盖

    # ============================= 通用方法 =============================
    # random_free_port(self): 生成随机可用端口
    # check_command(self, cmd)：检查命令是否存在
    # check_dependencies(self): 检查必要的依赖是否已安装
    # detect_architecture(self): 检测系统架构
    # get_public_ip(self): 获取公网IP

    def random_free_port(self):
        """生成随机可用端口"""
        while True:
            port = random.randint(20000, 60000)
            try:
                with open('/proc/net/tcp', 'r') as f:
                    tcp_content = f.read()
                with open('/proc/net/udp', 'r') as f:
                    udp_content = f.read()

                hex_port = f"{port:04X}"
                if hex_port not in tcp_content and hex_port not in udp_content:
                    return port
            except Exception:
                continue

    def check_command(self, cmd):
        """检查命令是否存在"""
        try:
            sh.which(cmd)
            return True
        except sh.ErrorReturnCode:
            return False

    def check_dependencies(self):
        """检查必要的依赖是否已安装"""
        required_cmds = ["curl", "wget", "gzip", "openssl", "uuidgen", "socat"]
        missing_cmds = [cmd for cmd in required_cmds if not self.check_command(cmd)]

        if missing_cmds:
            print("❌ 缺少必要的依赖命令:")
            for cmd in missing_cmds:
                print(f"   - {cmd}")
            print("\n请先运行依赖安装脚本:")
            print("   bash install_dependencies.sh")
            sys.exit(1)

    def detect_architecture(self):
        """检测系统架构"""
        arch = sh.uname("-m").strip()

        arch_map = {
            "x86_64": ("amd64", True),
            "aarch64": ("arm64", False),
            "armv7l": ("armv7", False),
            "armv6l": ("armv6", False),
        }

        if arch not in arch_map:
            print(f"❌ 不支持的架构: {arch}")
            sys.exit(1)

        bin_arch, support_level = arch_map[arch]

        # 检测 CPU 指令集
        level = "v1"
        if support_level:
            try:
                cpu_flags = sh.grep("flags", "/proc/cpuinfo", _piped=True)
                flags_line = sh.head("-n1", _in=cpu_flags).strip()
                if "avx2" in flags_line:
                    level = "v3"
                elif "avx" in flags_line:
                    level = "v2"
            except:
                level = "v1"

        print(f"🧠 检测到 CPU 架构: {arch}, 指令集等级: {level}")
        return bin_arch, level

    def get_public_ip(self):
        """获取公网 IP"""
        try:
            return sh.curl("-s", "ifconfig.me").strip()
        except:
            try:
                return sh.curl("-s", "icanhazip.com").strip()
            except:
                return "获取失败"

    # ============================= 通用配置获取方法 =============================
    # get_domain_input(self, prompt): 获取并验证域名输入
    # get_email_input(self, prompt): 获取并验证邮箱输入
    # get_port_input(self, prompt): 获取端口配置
    # get_password_or_uuid_input(self, use_uuid, prompt_type): 获取密码或UUID配置
    # get_cert_type_choice(self): 选择证书类型
    # confirm_config(self, config_dict): 确认配置信息

    def get_domain_input(self, prompt="请输入您的域名(例如: proxy.example.com): "):
        """获取并验证域名输入"""
        while True:
            domain = input(prompt).strip()
            if not domain:
                print("❌ 域名不能为空")
                continue

            if not self.validate_domain(domain):
                print("❌ 域名格式不正确")
                continue
            return domain

    def get_email_input(self, prompt="请输入您的邮箱(用于接收证书通知): "):
        """获取并验证邮箱输入"""
        while True:
            email = input(prompt).strip()
            if not email:
                print("❌ 邮箱不能为空")
                continue

            if not self.validate_email(email):
                print("❌ 邮箱格式不正确")
                continue
            return email

    def get_port_input(self, prompt="请输入端口号(留空则随机生成 20000-60000): "):
        """获取端口配置"""
        port_input = input(prompt).strip()

        if port_input:
            try:
                port = int(port_input)
                if port < 1 or port > 65535:
                    print("❌ 端口号必须在 1-65535 之间,使用随机端口")
                    port = self.random_free_port()
                elif port < 1024:
                    print("⚠️ 警告: 使用小于 1024 的端口需要 root 权限")
            except ValueError:
                print("❌ 无效的端口号,使用随机端口")
                port = self.random_free_port()
        else:
            port = self.random_free_port()

        print(f"✅ 使用端口: {port}")
        return port

    def get_password_or_uuid_input(self, use_uuid=False, prompt_type="密码"):
        """获取密码或UUID配置

        Args:
            use_uuid: True表示生成UUID, False表示生成密码
            prompt_type: 提示文本类型
        """
        if use_uuid:
            prompt = f"请输入 UUID(留空则随机生成): "
        else:
            prompt = f"请输入节点{prompt_type}(留空则随机生成 UUID): "

        value = input(prompt).strip()

        if not value:
            value = sh.uuidgen().strip()
            if use_uuid:
                print(f"✅ 生成随机 UUID: {value}")
            else:
                print(f"✅ 生成随机密码: {value}")
        else:
            if use_uuid:
                print(f"✅ 使用自定义 UUID")
            else:
                print(f"✅ 使用自定义{prompt_type}")

        return value

    def get_cert_type_choice(self):
        """选择证书类型

        Returns:
            bool: True表示使用自签证书, False表示使用正式证书
        """
        print("\n📜 证书类型:")
        print("  1. 使用 acme.sh 申请正式证书 (推荐)")
        print("  2. 使用自签证书 (需要客户端跳过证书验证)")

        while True:
            cert_choice = input("\n请选择证书类型 (1/2): ").strip()
            if cert_choice in ['1', '2']:
                break
            print("❌ 无效选项,请重新输入")

        use_self_signed = (cert_choice == '2')

        if use_self_signed:
            print("\n⚠️ 警告: 使用自签证书需要:")
            print("   - 客户端开启跳过证书验证 'skip-cert-verify: true'")
            print("   - 或允许使用不安全的证书(AllowInsecure)")

        return use_self_signed

    def confirm_config(self, config_dict):
        """确认配置信息

        Args:
            config_dict: 配置信息字典

        Returns:
            bool: True表示确认, False表示取消
        """
        print(f"\n📋 配置信息确认:")
        for key, value in config_dict.items():
            print(f"  {key}: {value}")
        print()

        confirm = input("确认无误?(y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ 已取消")
            return False
        return True

    # ============================= 证书相关 =============================
    # validate_domain(self, domain): 验证域名格式
    # install_acme_sh(self, email): 验证邮箱格式
    # install_acme_sh(self, email): 安装 acme.sh
    # generate_self_signed_cert(self, domain): 生成自签证书
    # request_certificate(self, domain, email): 申请 SSL 证书

    def validate_domain(self, domain):
        """验证域名格式"""
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return re.match(domain_pattern, domain) is not None

    def validate_email(self, email):
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            return False

        # 检查是否使用了 Let's Encrypt 禁止的测试域名
        forbidden_domains = [
            'example.com', 'example.org', 'example.net',
            'test.com', 'test.org', 'test.net',
            'localhost.com', 'invalid.com',
            'invalid', 'local', 'localhost'
        ]

        email_domain = email.split('@')[1].lower()
        if email_domain in forbidden_domains:
            print(f"❌ 不能使用测试域名 '{email_domain}' 作为邮箱")
            print("   请使用真实的邮箱地址(如 Gmail, Outlook 等)")
            return False

        return True

    def install_acme_sh(self, email):
        """安装 acme.sh"""
        if self.acme_sh.exists():
            print("✅ 已检测到 acme.sh")
            return

        print("📥 安装 acme.sh...")
        try:
            # 修正: 使用正确的参数格式
            result = subprocess.run(
                f"curl -s https://get.acme.sh | sh -s email={email}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                print(f"警告: acme.sh 安装返回代码 {result.returncode}")
                if not self.acme_sh.exists():
                    print(f"错误输出: {result.stderr}")
                    raise Exception("acme.sh 安装失败")

            print("✅ acme.sh 安装完成")
        except subprocess.TimeoutExpired:
            print("❌ acme.sh 安装超时")
            sys.exit(1)
        except Exception as e:
            print(f"❌ acme.sh 安装失败: {e}")
            sys.exit(1)

        if not self.acme_sh.exists():
            print("❌ acme.sh 未找到")
            sys.exit(1)

    def generate_self_signed_cert(self, domain):
        """生成自签证书"""
        print("\n🔐 生成自签证书...")

        self.cert_dir.mkdir(parents=True, exist_ok=True)

        cert_file = self.cert_dir / "server.crt"
        key_file = self.cert_dir / "server.key"

        try:
            subprocess.run(
                f'openssl req -x509 -nodes -days 365 -newkey rsa:2048 '
                f'-keyout {key_file} -out {cert_file} '
                f'-subj "/C=US/ST=State/L=City/O=Organization/CN={domain}"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                check=True
            )

            print("✅ 自签证书生成成功")
            print(f"   证书: {cert_file}")
            print(f"   私钥: {key_file}")

        except subprocess.TimeoutExpired:
            print("❌ 证书生成超时")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 证书生成失败: {e}")
            sys.exit(1)

    def request_certificate(self, domain, email):
        """申请 SSL 证书"""
        print("\n🔒 开始申请 SSL 证书...")
        print("⚠️ 请确保:")
        print(f"  1. 域名 {domain} 已解析到本机 IP")
        print("  2. 防火墙已开放 80 端口(用于证书验证)\n")
        input("按回车继续...")

        print("📝 注册 Let's Encrypt ACME 账户...")
        try:
            # 修正: 使用 --accountemail 参数
            subprocess.run(
                f"{self.acme_sh} "
                f"--server letsencrypt "
                f"--register-account "
                f"--accountemail {email} "
                f"--force",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )
        except Exception as e:
            print(f"⚠️ 账户已存在或注册失败: {e}")

        # 停止占用 80 端口的服务
        try:
            status = sh.systemctl("is-active", "mihomo", _ok_code=[0, 3])
            if "active" in str(status):
                print("🛑 临时停止 mihomo 服务...")
                sh.systemctl("stop", "mihomo")
        except:
            pass

        # 切换到 Let's Encrypt
        print("🔄 切换到 Let's Encrypt ...")
        subprocess.run(
            f"{self.acme_sh} --set-default-ca --server letsencrypt",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        # 申请证书
        print("📜 申请证书中(HTTP-01 验证)...")
        try:
            result = subprocess.run(
                f"{self.acme_sh} --issue "
                f"--server letsencrypt "
                f"--accountemail {email} "
                f"-d {domain} "
                f"--standalone "
                f"--keylength ec-256 "
                f"--force",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=180
            )

            if "Cert success" not in result.stdout:
                print(f"命令输出:\n{result.stdout}")
                raise Exception("证书申请失败")

        except subprocess.TimeoutExpired:
            print("❌ 证书申请超时")
            sys.exit(1)
        except Exception as e:
            print("❌ 证书申请失败,请检查:")
            print("  1. 域名解析是否正确")
            print("  2. 80 端口是否可访问")
            print("  3. 防火墙设置")
            sys.exit(1)

        # 创建证书目录
        self.cert_dir.mkdir(parents=True, exist_ok=True)

        # 安装证书
        print("📦 安装证书...")
        try:
            result = subprocess.run(
                f"{self.acme_sh} --install-cert "
                f"-d {domain} --ecc "
                f"--key-file {self.cert_dir}/server.key "
                f"--fullchain-file {self.cert_dir}/server.crt "
                f"--reloadcmd 'systemctl reload mihomo 2>/dev/null || true'",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"⚠️ 证书安装返回代码 {result.returncode}")
                if not (self.cert_dir / "server.crt").exists():
                    print(f"命令输出:\n{result.stdout}")
                    raise Exception("证书文件未生成")

        except subprocess.TimeoutExpired:
            print("❌ 证书安装超时")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 证书安装失败: {e}")
            sys.exit(1)

        print("🎉 证书获取并安装成功!")

    # ============================= Mihomo---Systemd与Docker部署 =============================
    # install_mihomo(self, bin_arch, level): 下载并安装 Mihomo
    # create_systemd_service(self): 创建 systemd 服务
    # check_docker(self): 检查 Docker 和 Docker Compose 是否已安装
    # _check_docker_compose_plugin(self): 检查 docker compose (作为插件) 是否可用
    # get_deployment_method(self): 让用户选择部署方式
    # install_docker(self): 安装 Docker 和 Docker Compose
    # create_docker_compose_file(self, config_dir, protocol_name, port=None): 创建 Docker Compose 配置文件
    # start_docker_service(self, config_dir): 启动 Docker 服务

    def install_mihomo(self, bin_arch, level):
        """下载并安装 Mihomo"""
        if self.check_command("mihomo"):
            print("✅ 已检测到 mihomo,跳过安装步骤")
            return

        print("⬇️ 正在安装 mihomo ...")

        try:
            # 获取最新版本
            response = sh.curl("-s", "https://api.github.com/repos/MetaCubeX/mihomo/releases/latest")
            data = json.loads(str(response))
            latest_version = data["tag_name"]

            if not latest_version:
                print("❌ 获取版本号失败")
                sys.exit(1)

            # 构建下载 URL
            if bin_arch == "amd64":
                file_name = f"mihomo-linux-{bin_arch}-{level}-{latest_version}.gz"
            else:
                file_name = f"mihomo-linux-{bin_arch}-{latest_version}.gz"

            download_url = f"https://github.com/MetaCubeX/mihomo/releases/download/{latest_version}/{file_name}"

            print(f"📦 下载 {file_name} ...")
            try:
                sh.wget("-O", "/tmp/mihomo.gz", download_url, _fg=True)
            except:
                print(f"⚠️ 下载 {level} 版本失败,尝试兼容版本...")
                file_name = f"mihomo-linux-{bin_arch}-compatible-{latest_version}.gz"
                download_url = f"https://github.com/MetaCubeX/mihomo/releases/download/{latest_version}/{file_name}"
                sh.wget("-O", "/tmp/mihomo.gz", download_url, _fg=True)

            # 解压并安装
            sh.gzip("-d", "/tmp/mihomo.gz")
            sh.chmod("+x", "/tmp/mihomo")
            sh.mv("/tmp/mihomo", "/usr/local/bin/mihomo")

            print("✅ mihomo 安装完成")
        except Exception as e:
            print(f"❌ mihomo 安装失败: {e}")
            sys.exit(1)

    def create_systemd_service(self):
        """创建 systemd 服务"""
        service_content = f"""[Unit]
Description=Mihomo Service
After=network.target

[Service]
Type=simple
WorkingDirectory={self.cert_dir}
ExecStart=/usr/local/bin/mihomo -d {self.cert_dir}
Restart=on-failure
RestartSec=3
User=root
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
"""

        service_file = Path("/etc/systemd/system/mihomo.service")
        service_file.write_text(service_content)

        sh.systemctl("daemon-reload")
        sh.systemctl("enable", "--now", "mihomo.service", _fg=True)

        time.sleep(2)

    def check_docker(self):
        """检查 Docker 和 Docker Compose 是否已安装"""
        has_docker = self.check_command("docker")
        has_compose = self.check_command("docker-compose") or self.check_command(
            "docker") and self._check_docker_compose_plugin()

        return has_docker and has_compose

    def _check_docker_compose_plugin(self):
        """检查 docker compose (作为插件) 是否可用"""
        try:
            subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                timeout=5
            )
            return True
        except:
            return False

    def get_deployment_method(self):
        """让用户选择部署方式"""
        print("\n" + "=" * 42)
        print("📦 选择部署方式")
        print("=" * 42 + "\n")

        print("  1. 直接部署 (systemd 服务)")
        print("  2. Docker 部署 (容器化)")

        # 检查 Docker 是否可用
        has_docker = self.check_docker()
        if not has_docker:
            print("\n⚠️ 注意: 未检测到 Docker 或 Docker Compose")
            print("   如需使用 Docker 部署,请先安装:")
            print("   - Docker: curl -fsSL https://get.docker.com | sh")
            print("   - 或参考: https://docs.docker.com/engine/install/")

        while True:
            choice = input("\n请选择部署方式 (1/2): ").strip()
            if choice == '1':
                return 'systemd'
            elif choice == '2':
                if not has_docker:
                    print("❌ Docker 未安装,无法使用此选项")
                    install_choice = input("是否现在安装 Docker? (y/n): ").strip().lower()
                    if install_choice in ['y', 'yes']:
                        self.install_docker()
                        return 'docker'
                    else:
                        continue
                return 'docker'
            else:
                print("❌ 无效选项,请重新输入")

    def install_docker(self):
        """安装 Docker 和 Docker Compose"""
        print("\n🐳 开始安装 Docker...")

        try:
            # 使用官方安装脚本
            print("📥 下载 Docker 安装脚本...")
            subprocess.run(
                "curl -fsSL https://get.docker.com -o /tmp/get-docker.sh",
                shell=True,
                check=True,
                timeout=60
            )

            print("🔧 执行安装...")
            subprocess.run(
                "sh /tmp/get-docker.sh",
                shell=True,
                check=True,
                timeout=300
            )

            # 启动 Docker 服务
            sh.systemctl("start", "docker")
            sh.systemctl("enable", "docker")

            print("✅ Docker 安装完成")

        except Exception as e:
            print(f"❌ Docker 安装失败: {e}")
            print("\n请手动安装 Docker:")
            print("  https://docs.docker.com/engine/install/")
            sys.exit(1)

    from pathlib import Path

    def create_docker_compose_file(self, config_dir, protocol_name, port=None):
        """创建 Docker Compose 配置文件"""

        config_dir_abs = Path(config_dir).resolve()

        cert_file = config_dir_abs / "server.crt"
        key_file = config_dir_abs / "server.key"

        # 逐行构造docker配置
        lines = [
            "services:",
            "  mihomo:",
            "    container_name: mihomo",
            "    image: metacubex/mihomo:latest",
            "    restart: unless-stopped",
            "    environment:",
            "      - TZ=Asia/Shanghai",
            "    volumes:",
            f"      - {config_dir_abs}/config.yaml:/root/.config/mihomo/config.yaml:ro"
        ]

        # 插入证书
        if cert_file.exists() and key_file.exists():
            lines += [
                f"      - {config_dir_abs}/server.crt:/root/.config/mihomo/server.crt:ro",
                f"      - {config_dir_abs}/server.key:/root/.config/mihomo/server.key:ro",
            ]

        lines.append("    network_mode: host")

        compose_content = "\n".join(lines)

        compose_file = config_dir_abs / "docker-compose.yml"
        compose_file.write_text(compose_content, encoding="utf-8")

        print(f"✅ Docker Compose 配置已生成: {compose_file}")
        print("\n生成的配置内容:")
        print(compose_content)
        return compose_file

    def start_docker_service(self, config_dir):
        """启动 Docker 服务"""
        print("\n🐳 启动 Docker 容器...")

        try:
            # 切换到配置目录
            import os
            original_dir = os.getcwd()
            os.chdir(config_dir)

            # 优先使用 docker compose (新版本)
            try:
                result = subprocess.run(
                    ["docker", "compose", "up", "-d"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode != 0:
                    print(f"错误输出:\n{result.stderr}")
                    raise Exception(f"Docker compose 启动失败: {result.stderr}")
            except FileNotFoundError:
                # 回退到 docker-compose (旧版本)
                result = subprocess.run(
                    ["docker-compose", "up", "-d"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode != 0:
                    print(f"错误输出:\n{result.stderr}")
                    raise Exception(f"Docker compose 启动失败: {result.stderr}")

            os.chdir(original_dir)

            print("✅ Docker 容器已启动")

            # 等待容器启动
            import time
            time.sleep(3)

            # 显示容器状态
            print("\n📊 容器状态:")
            try:
                subprocess.run(["docker", "ps", "-a", "--filter", "name=mihomo"], check=False)
            except:
                pass

        except Exception as e:
            print(f"❌ 启动容器失败: {e}")
            # 显示生成的配置文件内容用于调试
            try:
                compose_file = config_dir / "docker-compose.yml"
                if compose_file.exists():
                    print(f"\n生成的 docker-compose.yml 内容:")
                    print(compose_file.read_text())
            except:
                pass
            sys.exit(1)

    # ============================= 抽象方法 - 每个协议部署类必须实现 =============================
    # get_deployment_config(self): 获取部署配置 - 子类实现
    # generate_config(self, **kwargs): 生成协议配置 - 子类实现
    # print_final_info(self, **kwargs): 输出最终配置信息 - 子类实现
    # install(self): 安装协议

    @abstractmethod
    def get_deployment_config(self):
        """获取部署配置 - 子类实现"""
        pass

    @abstractmethod
    def generate_config(self, **kwargs):
        """生成协议配置 - 子类实现"""
        pass

    @abstractmethod
    def print_final_info(self, **kwargs):
        """输出最终配置信息 - 子类实现"""
        pass

    @abstractmethod
    def install(self):
        """安装协议 - 子类实现完整流程"""
        pass

    # ============================= 卸载 =============================
    def uninstall(self):
        """卸载 Mihomo 及相关文件"""
        print("\n" + "=" * 46)
        print("🗑️ 开始卸载 Mihomo")
        print("=" * 46 + "\n")

        # 检测部署方式
        docker_compose_file = self.cert_dir / "docker-compose.yml"
        is_docker_deployment = docker_compose_file.exists()

        if is_docker_deployment:
            print("📦 检测到 Docker 部署\n")
            print("⚠️ 警告: 此操作将删除以下内容:")
            print("  1. Mihomo Docker 容器")
            print("  2. Mihomo 配置文件")
            print("  3. SSL 证书文件")
            print("  4. Docker Compose 配置文件")
            print("  5. Mihomo Docker 镜像(可选)")
            print("  6. acme.sh 中的证书配置\n")
        else:
            print("⚠️ 警告: 此操作将删除以下内容:")
            print("  1. Mihomo 程序文件")
            print("  2. Mihomo 配置文件")
            print("  3. SSL 证书文件")
            print("  4. systemd 服务文件")
            print("  5. acme.sh 中的证书配置\n")

        confirm = input("确认卸载? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ 已取消卸载")
            return

        if is_docker_deployment:
            # Docker 部署的卸载流程
            print("\n🐳 处理 Docker 容器...")

            # 停止并删除容器
            try:
                import os
                original_dir = os.getcwd()
                os.chdir(self.cert_dir)

                print("🛑 停止容器...")
                try:
                    subprocess.run(
                        ["docker", "compose", "down"],
                        timeout=30,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                except:
                    # 回退到旧版本命令
                    subprocess.run(
                        ["docker-compose", "down"],
                        timeout=30,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                os.chdir(original_dir)
                print("✅ 容器已停止并删除")

            except Exception as e:
                print(f"⚠️ 停止容器失败: {e}")

            # 询问是否删除镜像
            print("\n🗑️ 处理 Docker 镜像...")
            remove_image = input("是否删除 Mihomo Docker 镜像? (y/n): ").strip().lower()

            if remove_image in ['y', 'yes']:
                try:
                    # 查找 mihomo 相关镜像
                    result = subprocess.run(
                        ["docker", "images", "-q", "metacubex/mihomo"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if result.stdout.strip():
                        subprocess.run(
                            ["docker", "rmi", "-f"] + result.stdout.strip().split('\n'),
                            timeout=30
                        )
                        print("✅ Mihomo 镜像已删除")
                    else:
                        print("⚠️ 未找到 Mihomo 镜像")

                except Exception as e:
                    print(f"⚠️ 删除镜像失败: {e}")

            # 删除配置目录
            print("\n🗑 删除配置目录...")
            if self.cert_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(self.cert_dir)
                    print(f"✅ 配置目录已删除: {self.cert_dir}")
                except Exception as e:
                    print(f"⚠️ 删除配置目录失败: {e}")
            else:
                print("⚠️ 配置目录不存在")

        else:
            # 原有的 systemd 部署卸载流程
            # 停止并禁用服务
            print("\n🛑 停止 Mihomo 服务...")
            try:
                sh.systemctl("stop", "mihomo", _ok_code=[0, 5])
                sh.systemctl("disable", "mihomo", _ok_code=[0, 1])
                print("✅ 服务已停止")
            except Exception as e:
                print(f"⚠️ 停止服务失败: {e}")

            # 删除 systemd 服务文件
            print("\n🗑 删除 systemd 服务文件...")
            service_file = Path("/etc/systemd/system/mihomo.service")
            if service_file.exists():
                try:
                    service_file.unlink()
                    sh.systemctl("daemon-reload")
                    print("✅ 服务文件已删除")
                except Exception as e:
                    print(f"⚠️ 删除服务文件失败: {e}")
            else:
                print("⚠️ 服务文件不存在")

            # 删除 Mihomo 程序
            print("\n🗑️ 删除 Mihomo 程序...")
            mihomo_bin = Path("/usr/local/bin/mihomo")
            if mihomo_bin.exists():
                try:
                    mihomo_bin.unlink()
                    print("✅ Mihomo 程序已删除")
                except Exception as e:
                    print(f"⚠️ 删除程序失败: {e}")
            else:
                print("⚠️ Mihomo 程序不存在")

            # 删除配置目录
            print("\n🗑 删除配置目录...")
            if self.cert_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(self.cert_dir)
                    print(f"✅ 配置目录已删除: {self.cert_dir}")
                except Exception as e:
                    print(f"⚠️ 删除配置目录失败: {e}")
            else:
                print("⚠️ 配置目录不存在")

        # 处理 acme.sh 证书(两种部署方式都可能有)
        print("\n🗑 处理 SSL 证书...")
        if self.acme_sh.exists():
            try:
                result = subprocess.run(
                    f"{self.acme_sh} --list",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0 and result.stdout:
                    print("  检测到以下证书:")
                    print(result.stdout)
                    remove_certs = input("\n是否删除 acme.sh 中的证书? (y/n): ").strip().lower()

                    if remove_certs in ['y', 'yes']:
                        for line in result.stdout.split('\n'):
                            if line.strip() and not line.startswith('Main'):
                                parts = line.split()
                                if len(parts) > 0:
                                    domain = parts[0]
                                    try:
                                        subprocess.run(
                                            f"{self.acme_sh} --remove -d {domain}",
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            timeout=10
                                        )
                                        print(f"  ✅ 已删除域名证书: {domain}")
                                    except Exception as e:
                                        print(f"  ⚠️ 删除 {domain} 证书失败: {e}")
            except Exception as e:
                print(f"⚠️ 处理证书失败: {e}")
        else:
            print("⚠️ acme.sh 未安装")

        print("\n" + "=" * 46)
        print("✅ 卸载完成!")
        print("=" * 46 + "\n")

        if is_docker_deployment:
            print("ℹ️ 说明:")
            print("  - acme.sh 本身未被删除(可能被其他应用使用)")
            print("  - 如需完全删除 acme.sh, 请运行:")
            print(f"    {self.acme_sh} --uninstall")
            print(f"    rm -rf {self.home}/.acme.sh")
            print("  - 如需清理未使用的 Docker 资源:")
            print("    docker system prune -a\n")
        else:
            print("ℹ️ 说明:")
            print("  - acme.sh 本身未被删除(可能被其他应用使用)")
            print("  - 如需完全删除 acme.sh, 请运行:")
            print(f"    {self.acme_sh} --uninstall")
            print(f"    rm -rf {self.home}/.acme.sh\n")
