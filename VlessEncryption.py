#!/usr/bin/env python3
"""
VlessEncryption.py - VLESS Encryption 协议部署模块
继承 MihomoBase 基类,实现 VLESS Encryption 协议的具体部署
支持混合密钥交换 (mlkem768x25519plus) 和多种加密方式
"""

import sh
import sys
import yaml
import subprocess
from BaseClass import MihomoBase


class VlessEncryptionInstaller(MihomoBase):
    """VLESS Encryption 协议安装器"""

    def __init__(self):
        super().__init__()
        self.protocol_name = "VlessEncryption"

    def validate_padding_format(self, padding_str):
        """验证 padding 格式是否正确

        格式: probability-min-max
        - probability: 0-100 的整数
        - min: >= 0 的整数
        - max: >= min 的整数
        """
        try:
            parts = padding_str.split('-')
            if len(parts) != 3:
                return False, "格式错误,应为 probability-min-max"

            probability = int(parts[0])
            min_val = int(parts[1])
            max_val = int(parts[2])

            if probability < 0 or probability > 100:
                return False, "概率必须在 0-100 之间"

            if min_val < 0:
                return False, "最小值不能小于 0"

            if max_val < min_val:
                return False, "最大值不能小于最小值"

            return True, ""

        except ValueError:
            return False, "必须为整数"
        except Exception as e:
            return False, f"验证失败: {e}"

    def configure_padding(self):
        """配置 Padding - 支持无限串联"""
        padding_blocks = []

        print("\n🔧 自定义 Padding 配置")
        print("=" * 42)
        print("说明:")
        print("  - 第一个 Padding 必须 100% 概率且最小长度 >= 35")
        print("  - 后续可添加多个 padding/delay 块")
        print("  - 两个 padding 块之间必须有 delay 块")
        print("  - 输入 'done' 完成配置\n")

        # 第一个 Padding (强制要求)
        while True:
            print("📦 第一个 Padding (必填):")
            padding1 = input("  格式 100-min-max (如 100-111-1111): ").strip()

            if not padding1:
                print("❌ 第一个 Padding 不能为空")
                continue

            valid, error = self.validate_padding_format(padding1)
            if not valid:
                print(f"❌ {error}")
                continue

            # 检查是否 100% 概率
            if not padding1.startswith("100-"):
                print("❌ 第一个 Padding 必须是 100% 概率")
                continue

            # 检查最小值是否 >= 35
            parts = padding1.split('-')
            if int(parts[1]) < 35:
                print("❌ 第一个 Padding 的最小长度必须 >= 35 字节")
                continue

            padding_blocks.append(padding1)
            print(f"✅ 已添加: {padding1}\n")
            break

        # 循环添加更多块
        last_block_type = "padding"  # 记录上一个块的类型

        while True:
            print(f"当前配置: {'.'.join(padding_blocks)}\n")

            if last_block_type == "padding":
                print("📊 下一步选择:")
                print("  1. 添加 Delay 块")
                print("  2. 完成配置")
                choice = input("请选择 (1/2): ").strip()

                if choice == '2':
                    break
                elif choice == '1':
                    while True:
                        delay = input("\n⏱️  Delay 格式 probability-min-max (如 75-0-111): ").strip()

                        if not delay:
                            print("❌ Delay 不能为空")
                            continue

                        valid, error = self.validate_padding_format(delay)
                        if not valid:
                            print(f"❌ {error}")
                            continue

                        padding_blocks.append(delay)
                        print(f"✅ 已添加 Delay: {delay}\n")
                        last_block_type = "delay"
                        break
                else:
                    print("❌ 无效选项\n")

            elif last_block_type == "delay":
                print("📊 下一步选择:")
                print("  1. 添加 Padding 块")
                print("  2. 完成配置")
                choice = input("请选择 (1/2): ").strip()

                if choice == '2':
                    break
                elif choice == '1':
                    while True:
                        padding = input("\n📦 Padding 格式 probability-min-max (如 50-0-3333): ").strip()

                        if not padding:
                            print("❌ Padding 不能为空")
                            continue

                        valid, error = self.validate_padding_format(padding)
                        if not valid:
                            print(f"❌ {error}")
                            continue

                        padding_blocks.append(padding)
                        print(f"✅ 已添加 Padding: {padding}\n")
                        last_block_type = "padding"
                        break
                else:
                    print("❌ 无效选项\n")

        return '.'.join(padding_blocks)

    def generate_x25519_key(self):
        """生成 X25519 密钥对"""
        print("\n🔐 生成 X25519 密钥对...")
        try:
            result = subprocess.run(
                ["mihomo", "generate", "vless-x25519"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise Exception("X25519 密钥对生成失败")

            output = result.stdout.strip()
            lines = output.split('\n')

            private_key = None
            password = None

            for line in lines:
                if "PrivateKey:" in line:
                    private_key = line.split(":", 1)[1].strip()
                elif "Password:" in line:
                    password = line.split(":", 1)[1].strip()

            if not private_key or not password:
                raise Exception("无法解析 X25519 密钥对")

            print(f"✅ X25519 PrivateKey: {private_key}")
            print(f"✅ X25519 Password: {password}")

            return private_key, password

        except Exception as e:
            print(f"❌ X25519 密钥对生成失败: {e}")
            sys.exit(1)

    def generate_mlkem768_key(self):
        """生成 ML-KEM-768 密钥对"""
        print("\n🔐 生成 ML-KEM-768 密钥对...")
        try:
            result = subprocess.run(
                ["mihomo", "generate", "vless-mlkem768"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise Exception("ML-KEM-768 密钥对生成失败")

            output = result.stdout.strip()
            lines = output.split('\n')

            seed = None
            client_key = None

            for line in lines:
                if "Seed:" in line:
                    seed = line.split(":", 1)[1].strip()
                elif "Client:" in line:
                    client_key = line.split(":", 1)[1].strip()

            if not seed or not client_key:
                raise Exception("无法解析 ML-KEM-768 密钥对")

            print(f"✅ ML-KEM-768 Seed: {seed}")
            print(f"✅ ML-KEM-768 Client: {client_key}")

            return seed, client_key

        except Exception as e:
            print(f"❌ ML-KEM-768 密钥对生成失败: {e}")
            sys.exit(1)

    def get_deployment_config(self):
        """获取 VLESS Encryption 部署配置"""
        print("\n" + "=" * 42)
        print("⚙️ VLESS Encryption 部署配置")
        print("=" * 42 + "\n")

        # 选择加密方式
        print("🔐 加密方式:")
        print("  1. native  - 原始外观")
        print("  2. xorpub  - 只 XOR 公钥 (默认)")
        print("  3. random  - 全随机数")

        while True:
            enc_choice = input("\n请选择加密方式 (1/2/3, 默认 2): ").strip()
            if not enc_choice:
                enc_choice = '2'
            if enc_choice in ['1', '2', '3']:
                break
            print("❌ 无效选项,请重新输入")

        # 加密模式映射
        mode_map = {'1': 'native', '2': 'xorpub', '3': 'random'}
        encryption_mode = mode_map[enc_choice]

        # 服务端: 选择 ticket_time (票据有效时间)
        print("\n🎫 服务端票据有效时间 (ticket_time):")
        print("  1. 0s   - 禁用 0-RTT")
        print("  2. 300s - 自定义时间 (如 300 秒)")

        while True:
            ticket_choice = input("\n请选择 (1/2, 默认 1): ").strip()
            if not ticket_choice:
                ticket_choice = '1'
            if ticket_choice in ['1', '2']:
                break
            print("❌ 无效选项,请重新输入")

        if ticket_choice == '1':
            ticket_time = '0s'
        else:  # ticket_choice == '2'
            while True:
                custom_time = input("请输入时间 (300-600 秒之间,格式如 300s): ").strip()
                if custom_time.endswith('s'):
                    try:
                        seconds = int(custom_time[:-1])
                        if 300 <= seconds <= 600:
                            ticket_time = custom_time
                            break
                        else:
                            print("❌ 时间必须在 300-600 秒之间")
                    except ValueError:
                        print("❌ 格式错误,请输入如 300s 的格式")
                else:
                    print("❌ 格式错误,请输入如 300s 的格式")

        # 客户端: 选择 rtt_mode
        print("\n🔄 客户端 RTT 模式 (rtt_mode):")
        print("  1. 0rtt - 启用 0-RTT")
        print("  2. 1rtt - 启用 1-RTT")

        while True:
            rtt_choice = input("\n请选择 (1/2, 默认 2): ").strip()
            if not rtt_choice:
                rtt_choice = '2'
            if rtt_choice in ['1', '2']:
                break
            print("❌ 无效选项,请重新输入")

        if rtt_choice == '1':
            rtt_mode = '0rtt'
        elif rtt_choice == '2':
            rtt_mode = '1rtt'

        # Padding 配置 - 支持无限串联
        print("\n🔐 Padding 配置 (用于混淆长度特征):")
        print("  提示: 格式为 probability-min-max")
        print("  Padding 格式: 如 100-111-1111 (100%概率发送111-1111字节)")
        print("  Delay 格式: 如 75-0-111 (75%概率等待0-111毫秒)")
        print("  默认值: 100-111-1111.75-0-111.50-0-3333")

        use_default_padding = input("\n使用默认 Padding 配置? (y/n, 默认 y): ").strip().lower()

        if use_default_padding in ['n', 'no']:
            padding_config = self.configure_padding()
        else:
            padding_config = "100-111-1111.75-0-111.50-0-3333"

        print(f"✅ 使用 Padding: {padding_config}")

        # 生成密钥对
        x25519_private, x25519_password = self.generate_x25519_key()
        mlkem768_seed, mlkem768_client = self.generate_mlkem768_key()

        # 获取端口
        print("\n📌 端口配置:")
        port = self.get_port_input()

        # 获取 UUID
        print("\n🔑 UUID 配置:")
        uuid = self.get_password_or_uuid_input(use_uuid=True)

        # 构建完整的 decryption 字符串(服务端)
        # 格式: mlkem768x25519plus.{encryption_mode}.{ticket_time}.{padding}.{X25519_PrivateKey}.{ML-KEM-768_Seed}
        decryption_parts = [
            "mlkem768x25519plus",
            encryption_mode,
            ticket_time,
            padding_config,
            x25519_private,
            mlkem768_seed
        ]

        # 过滤掉空字符串,只保留有效部分
        decryption_str = '.'.join(filter(None, decryption_parts))

        # 构建完整的 encryption 字符串(客户端)
        # 格式: mlkem768x25519plus.{encryption_mode}.{rtt_mode}.{padding}.{X25519_Password}.{ML-KEM-768_Client}
        encryption_parts = [
            "mlkem768x25519plus",
            encryption_mode,
            rtt_mode,
            padding_config,
            x25519_password,
            mlkem768_client
        ]

        # 过滤掉空字符串,只保留有效部分
        encryption_str = '.'.join(filter(None, encryption_parts))

        # 确认配置
        print(f"\n📋 配置信息确认:")
        print(f"  加密方式: {encryption_mode}")
        print(f"  服务端票据时间: {ticket_time or '(未设置)'}")
        print(f"  客户端 RTT 模式: {rtt_mode or '(未设置)'}")
        print(f"  Padding: {padding_config}")
        print(f"  X25519 PrivateKey: {x25519_private}")
        print(f"  X25519 Password: {x25519_password}")
        print(f"  ML-KEM-768 Seed: {mlkem768_seed}")
        print(f"  ML-KEM-768 Client: {mlkem768_client}")
        print(f"  端口: {port}")
        print(f"  UUID: {uuid}\n")

        confirm = input("确认无误?(y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ 已取消")
            sys.exit(1)

        return {
            'encryption_mode': encryption_mode,
            'rtt_mode': rtt_mode,
            'ticket_time': ticket_time,
            'padding_config': padding_config,
            'x25519_private': x25519_private,
            'x25519_password': x25519_password,
            'mlkem768_seed': mlkem768_seed,
            'mlkem768_client': mlkem768_client,
            'decryption_str': decryption_str,
            'encryption_str': encryption_str,
            'port': port,
            'uuid': uuid
        }

    def generate_config(self, config):
        """生成 VLESS Encryption 配置"""
        print("⚙️ 生成 VLESS Encryption 配置...")

        self.cert_dir.mkdir(parents=True, exist_ok=True)

        # 使用 PyYAML 构建配置
        config_dict = {
            'listeners': [
                {
                    'name': 'vless-encryption-in-1',
                    'type': 'vless',
                    'port': config['port'],
                    'listen': '0.0.0.0',
                    'users': [
                        {
                            'username': 'user1',
                            'uuid': config['uuid']
                        }
                    ],
                    'decryption': config['decryption_str'],
                }
            ]
        }

        config_file = self.cert_dir / "config.yaml"

        # 使用 PyYAML 写入配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f,
                      default_flow_style=False,
                      allow_unicode=True,
                      sort_keys=False)

        print("✅ 配置文件生成完成")

    def print_final_info(self, config):
        """输出 VLESS Encryption 最终配置信息"""
        public_ip = self.get_public_ip()

        print("\n" + "=" * 46)
        print("✅ VLESS Encryption 部署完成!")
        print("=" * 46 + "\n")

        print(f"📋 VLESS Encryption 客户端配置:\n")

        # 构建客户端配置字典
        client_config = {
            'name': f'VlessEnc|{config["encryption_mode"]}|{config["rtt_mode"]}',
            'server': public_ip,
            'type': 'vless',
            'port': config['port'],
            'uuid': config['uuid'],
            'network': 'tcp',
            'udp': True,
            'encryption': config['encryption_str'],
            'tls': False,
        }

        # YAML 格式 - 使用 PyYAML 输出
        print("---[ YAML 格式 ]---")
        yaml_output = yaml.dump([client_config],
                                default_flow_style=False,
                                allow_unicode=True,
                                sort_keys=False)
        print(yaml_output)

        # Compact YAML 格式 - 单行格式
        print("---[ Compact 格式 ]---")
        compact_parts = [
            f'name: "{client_config["name"]}"',
            f'type: {client_config["type"]}',
            f'server: {client_config["server"]}',
            f'port: {client_config["port"]}',
            f'uuid: {client_config["uuid"]}',
            f'network: {client_config["network"]}',
            f'udp: {str(client_config["udp"]).lower()}',
            f'encryption: "{client_config["encryption"]}"',
            f'tls: {str(client_config["tls"]).lower()}'
        ]
        compact = f'- {{{", ".join(compact_parts)}}}'
        print(f"{compact}\n")

        print("=" * 46)
        print("📌 重要信息:")
        print(f"  服务器 IP: {public_ip}")
        print(f"  加密方式: {config['encryption_mode']}")
        print(f"  RTT 模式: {config['rtt_mode']}")
        print(f"  票据时间: {config['ticket_time']}")
        print(f"  端口: {config['port']}")
        print(f"  UUID: {config['uuid']}\n")

        print("🔐 服务端密钥配置:")
        print(f"  X25519 PrivateKey: {config['x25519_private']}")
        print(f"  ML-KEM-768 Seed: {config['mlkem768_seed']}\n")

        print("🔐 客户端密钥配置:")
        print(f"  X25519 Password: {config['x25519_password']}")
        print(f"  ML-KEM-768 Client: {config['mlkem768_client']}\n")

        print("🔐 Padding 配置:")
        print(f"  {config['padding_config']}\n")

        print("🔐 完整 Decryption 字符串(服务端):")
        print(f"  {config['decryption_str']}\n")

        print("🔐 完整 Encryption 字符串(客户端):")
        print(f"  {config['encryption_str']}\n")

        print("🎯 防火墙设置:")
        print(f"  请确保开放端口: {config['port']}\n")
        print("  Ubuntu/Debian:")
        print(f"    sudo ufw allow {config['port']}/tcp")
        print(f"    sudo ufw allow {config['port']}/udp\n")
        print("  CentOS/RHEL:")
        print(f"    sudo firewall-cmd --permanent --add-port={config['port']}/tcp")
        print(f"    sudo firewall-cmd --permanent --add-port={config['port']}/udp")
        print(f"    sudo firewall-cmd --reload\n")

        print("=" * 46 + "\n")

        print("🔧 服务管理命令:")
        print("  查看状态: systemctl status mihomo")
        print("  重启服务: systemctl restart mihomo")
        print("  查看日志: journalctl -u mihomo -f")
        print("  停止服务: systemctl stop mihomo\n")

        print("=" * 46 + "\n")

        print("📊 当前服务状态:")
        try:
            sh.systemctl("status", "mihomo", "--no-pager", "-l", _fg=True)
        except:
            pass

        print("\n✅ 安装完成!请将上面的配置信息添加到您的客户端中。")
        print("\n💡 提示: VLESS Encryption 使用混合量子密钥交换,提供更高的安全性!")
        print("💡 注意: 该协议不支持 TLS,加密完全依赖 VLESS Encryption 本身的加密机制。")

    def install(self):
        """VLESS Encryption 完整安装流程"""
        try:
            print("\n" + "=" * 46)
            print("🚀 开始安装 VLESS Encryption")
            print("=" * 46)

            # 检查必要依赖
            self.check_dependencies()

            # 检测架构
            bin_arch, level = self.detect_architecture()

            # 安装 Mihomo
            self.install_mihomo(bin_arch, level)

            # 获取部署配置
            config = self.get_deployment_config()

            # 生成配置 (VLESS Encryption 不需要证书)
            self.generate_config(config)

            # 创建服务
            self.create_systemd_service()

            # 输出最终信息
            self.print_final_info(config)

        except KeyboardInterrupt:
            print("\n\n❌ 用户取消操作")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ 安装过程出错: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    # 检查是否为 root 用户
    if sh.whoami().strip() != "root":
        print("❌ 请使用 root 用户运行此脚本")
        sys.exit(1)

    installer = VlessEncryptionInstaller()
    installer.install()