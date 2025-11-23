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

        # 可选: 删除 acme.sh 证书
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
        print("ℹ️ 说明:")
        print("  - acme.sh 本身未被删除(可能被其他应用使用)")
        print("  - 如需完全删除 acme.sh, 请运行:")
        print(f"    {self.acme_sh} --uninstall")
        print(f"    rm -rf {self.home}/.acme.sh\n")