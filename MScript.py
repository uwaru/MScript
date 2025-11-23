#!/usr/bin/env python3
"""
MScript.py - Mihomo 协议部署管理主程序
支持多种协议的安装、卸载和管理
"""

import sys
import sh
from Anytls import AnyTLSInstaller
from Vless import VlessInstaller
from Mieru import MieruInstaller
from Tuic import TuicInstaller
from Hysteria import HysteriaInstaller
from Trojan import TrojanInstaller


class MihomoManager:
    """Mihomo 管理器主类"""

    def __init__(self):
        # 协议映射表 - 便于扩展新协议
        self.protocols = {
            '1': {
                'name': 'AnyTLS',
                'description': 'AnyTLS 协议 - 安全的 TLS 加密协议',
                'installer': AnyTLSInstaller
            },
            '2': {
                'name': 'Vless',
                'description': 'Vless 协议 - 支持 TLS 和 Reality 模式',
                'installer': VlessInstaller
            },
            '3': {
                'name': 'Mieru',
                'description': 'Mieru 协议 - 简单轻量的代理协议',
                'installer': MieruInstaller
            },
            '4': {
                'name': 'TUIC V5',
                'description': 'TUIC V5 协议 - 基于 QUIC 的高性能代理',
                'installer': TuicInstaller
            },
            '5': {
                'name': 'Hysteria2',
                'description': 'Hysteria2 协议 - 专为不稳定网络优化',
                'installer': HysteriaInstaller
            },
            '6': {
                'name': 'Trojan',
                'description': 'Trojan 协议 - 支持 TLS 和 Reality 模式',
                'installer': TrojanInstaller
            }
        }

        def print_banner(self):
            """打印程序横幅"""
        banner = r"""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║     ███╗   ███╗    ███████╗    ██████╗    ██████╗     ██╗   ██████╗  ║
    ║     ████╗ ████║    ██╔════╝   ██╔════╝    ██╔══██╗    ██║   ██╔══██╗ ║
    ║     ██╔████╔██║    ███████╗   ██║         ██████╔╝    ██║   ██████╔╝ ║
    ║     ██║╚██╔╝██║    ╚════██║   ██║         ██╔══██╗    ██║   ██╔═══╝  ║
    ║     ██║ ╚═╝ ██║    ███████║   ╚██████╗    ██║  ██║    ██║   ██║      ║
    ║     ╚═╝     ╚═╝    ╚══════╝    ╚═════╝    ╚═╝  ╚═╝    ╚═╝   ╚═╝      ║
    ║                                                                      ║
    ║  ═══════════════════════════════════════════════════════════════════ ║
    ║                                                                      ║
    ║         ⚡ Multi-Protocol Deployment & Orchestration Suite ⚡          ║
    ║                                                                      ║
    ║                            Version 1.0                               ║
    ║                                                                      ║
    ║  ═══════════════════════════════════════════════════════════════════ ║
    ║                                                                      ║
    ║     ▶ High Performance    ▶ Multi-Protocol    ▶ Auto Deployment      ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
        print(banner)

    def print_main_menu(self):
        """打印主菜单"""
        print("\n" + "─" * 63)
        print("                       M S C r i p t 主菜单")
        print("─" * 63 + "\n")

        print("  1. 安装协议")
        print("  2. 卸载Mihomo及删除相关配置文件")
        print("  3. 查看服务状态")
        print("  4. 重启服务")
        print("  5. 查看日志")
        print("  0. 退出程序")

        print("\n" + "─" * 63)

    def print_protocol_menu(self):
        """打印协议选择菜单"""
        print("\n" + "─" * 63)
        print("                       选择协议类型")
        print("─" * 63 + "\n")

        for key, protocol in self.protocols.items():
            print(f"  {key}. {protocol['name']}")
            print(f"       → {protocol['description']}\n")

        print("  0. 返回主菜单")
        print("\n" + "─" * 63)

    def install_protocol(self):
        """安装协议"""
        while True:
            self.print_protocol_menu()

            choice = input("\n请选择协议 (输入编号): ").strip()

            if choice == '0':
                return

            if choice in self.protocols:
                protocol_info = self.protocols[choice]
                print(f"\n✨ 准备安装 {protocol_info['name']} 协议...")

                # 确认安装
                confirm = input(f"\n确认安装 {protocol_info['name']}? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    print("❌ 已取消安装")
                    continue

                try:
                    # 实例化对应的安装器并执行安装
                    installer = protocol_info['installer']()
                    installer.install()

                    input("\n按回车键返回主菜单...")
                    return

                except Exception as e:
                    print(f"\n❌ 安装失败: {e}")
                    import traceback
                    traceback.print_exc()
                    input("\n按回车键继续...")
            else:
                print("❌ 无效的选项,请重新选择")

    def uninstall_mihomo(self):
        """卸载 Mihomo"""
        print("\n" + "═" * 63)
        print("                    🗑️  卸载 Mihomo 🗑️                       ")
        print("═" * 63)

        # 使用任意一个安装器的卸载方法即可(卸载逻辑在基类中)
        installer = AnyTLSInstaller()
        installer.uninstall()

        input("\n按回车键返回主菜单...")

    def check_service_status(self):
        """查看服务状态"""
        print("\n" + "═" * 63)
        print("                   📊 服务状态查询 📊                        ")
        print("═" * 63 + "\n")

        try:
            sh.systemctl("status", "mihomo", "--no-pager", "-l", _fg=True)
        except sh.ErrorReturnCode:
            print("\n⚠️  Mihomo 服务未运行或未安装")
        except Exception as e:
            print(f"\n❌ 查询失败: {e}")

        input("\n按回车键返回主菜单...")

    def restart_service(self):
        """重启服务"""
        print("\n" + "═" * 63)
        print("                    🔄 重启服务 🔄                          ")
        print("═" * 63 + "\n")

        confirm = input("确认重启 Mihomo 服务? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ 已取消重启")
            input("\n按回车键返回主菜单...")
            return

        try:
            print("\n🔄 正在重启服务...")
            sh.systemctl("restart", "mihomo")
            print("✅ 服务重启成功!")

            # 显示新的状态
            print("\n📊 当前状态:")
            sh.systemctl("status", "mihomo", "--no-pager", "-l", _fg=True)

        except sh.ErrorReturnCode:
            print("\n❌ 服务重启失败,请检查服务是否已安装")
        except Exception as e:
            print(f"\n❌ 重启失败: {e}")

        input("\n按回车键返回主菜单...")

    def view_logs(self):
        """查看日志"""
        print("\n" + "═" * 63)
        print("                   📖 服务日志查看 📖                       ")
        print("═" * 63 + "\n")

        print("提示: 按 Ctrl+C 退出日志查看\n")

        try:
            sh.journalctl("-u", "mihomo", "-f", "--no-pager", _fg=True)
        except KeyboardInterrupt:
            print("\n\n退出日志查看")
        except sh.ErrorReturnCode:
            print("\n⚠️  无法查看日志,请检查服务是否已安装")
        except Exception as e:
            print(f"\n❌ 查看失败: {e}")

        input("\n按回车键返回主菜单...")

    def run(self):
        """运行主程序"""
        # 检查是否为 root 用户
        if sh.whoami().strip() != "root":
            print("❌ 请使用 root 用户运行此脚本")
            sys.exit(1)

        # 打印横幅
        self.print_banner()

        # 主循环
        while True:
            try:
                self.print_main_menu()

                choice = input("\n请选择操作 (输入编号): ").strip()

                if choice == '0':
                    print("\n" + "═" * 63)
                    print("                  👋 感谢使用,再见! 👋                    ")
                    print("═" * 63 + "\n")
                    sys.exit(0)

                elif choice == '1':
                    self.install_protocol()

                elif choice == '2':
                    self.uninstall_mihomo()

                elif choice == '3':
                    self.check_service_status()

                elif choice == '4':
                    self.restart_service()

                elif choice == '5':
                    self.view_logs()

                else:
                    print("\n❌ 无效的选项,请重新选择")
                    input("按回车键继续...")

            except KeyboardInterrupt:
                print("\n\n" + "═" * 63)
                print("                  👋 感谢使用,再见! 👋                    ")
                print("═" * 63 + "\n")
                sys.exit(0)

            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                import traceback
                traceback.print_exc()
                input("\n按回车键继续...")


def main():
    """主函数入口"""
    manager = MihomoManager()
    manager.run()


if __name__ == "__main__":
    main()