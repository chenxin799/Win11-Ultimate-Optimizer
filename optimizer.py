import os
import sys
import shutil
import ctypes
import subprocess
import threading
import time
import psutil
import winreg
import stat
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

# ================= 配置与初始化 =================
ctk.set_appearance_mode("Light")

GLASS_COLORS = {
    "window_bg": "#E3F2FD",
    "pane_bg": "#FFFFFF",
    "pane_border": "#90CAF9",
    "text_main": "#1565C0",
    "text_dim": "#546E7A",
    "accent": "#29B6F6",
    "accent_hover": "#039BE5",
    "btn_hover": "#BBDEFB"
}

NtSetTimerResolution = ctypes.windll.ntdll.NtSetTimerResolution

# 用于控制后台自动清理线程的全局事件
STOP_BG_TASK = threading.Event()


class SystemUtils:
    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def elevate():
        if not SystemUtils.is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

    @staticmethod
    def cmd(command):
        try:
            subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            return False

    @staticmethod
    def reduce_self_memory():
        """让软件自身占用的内存最小化 (Self-Trim)"""
        try:
            pid = os.getpid()
            handle = ctypes.windll.kernel32.OpenProcess(0x0500, False, pid)
            ctypes.windll.psapi.EmptyWorkingSet(handle)
            ctypes.windll.kernel32.CloseHandle(handle)
        except:
            pass


# ================= 后端逻辑模块 =================

class LogicBase:
    def __init__(self, log_callback):
        self.log = log_callback


class ForceDeleter(LogicBase):
    def _remove_readonly(self, func, path, excinfo):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    def delete_target(self, path):
        self.log(f"正在尝试强力粉碎: {path}", "header")
        if not os.path.exists(path):
            self.log("路径不存在，操作取消。", "warning")
            return
        try:
            if os.path.isfile(path) or os.path.islink(path):
                try:
                    os.remove(path)
                except PermissionError:
                    os.chmod(path, stat.S_IWRITE)
                    os.remove(path)
                self.log(f"文件已粉碎: {os.path.basename(path)}", "success")
            elif os.path.isdir(path):
                self.log("正在递归删除目录树...", "info")
                shutil.rmtree(path, onerror=self._remove_readonly)
                if os.path.exists(path):
                    self.log("部分文件可能被系统核心占用，未能完全删除。", "warning")
                else:
                    self.log(f"文件夹已彻底粉碎: {os.path.basename(path)}", "success")
        except Exception as e:
            self.log(f"删除失败: {str(e)}", "warning")
        self.log("----------------------------------------", "normal")


class BrowserKiller(LogicBase):
    def __init__(self, log_callback):
        super().__init__(log_callback)
        self.targets = ["msedge.exe", "chrome.exe", "firefox.exe", "qqbrowser.exe", "360se.exe"]

    def run(self):
        self.log(">>> 开始执行: 浏览器进程粉碎", "header")
        count = 0
        for browser in self.targets:
            command = f"taskkill /F /IM {browser} /T"
            try:
                exists = False
                for p in psutil.process_iter(['name']):
                    if p.info['name'] and p.info['name'].lower() == browser:
                        exists = True
                        break
                if exists:
                    self.log(f"正在终止: {browser}", "warning")
                    SystemUtils.cmd(command)
                    count += 1
            except Exception:
                pass
        if count > 0:
            self.log(f"成功关闭 {count} 类浏览器及其后台服务。", "success")
        else:
            self.log("未检测到运行中的浏览器进程。", "info")
        self.log("----------------------------------------", "normal")


class DiskCleaner(LogicBase):
    def __init__(self, log_callback):
        super().__init__(log_callback)
        self.total_deleted_size = 0

    def _get_size(self, path):
        try:
            return os.path.getsize(path)
        except:
            return 0

    def _remove_contents(self, folder_path, desc):
        if not os.path.exists(folder_path): return
        self.log(f"正在扫描: {desc} ...", "info")
        for item in os.scandir(folder_path):
            try:
                path = item.path
                size = self._get_size(path)
                if item.is_file() or item.is_symlink():
                    os.unlink(path)
                    self.total_deleted_size += size
                elif item.is_dir():
                    shutil.rmtree(path)
                    self.total_deleted_size += size
            except:
                pass

    def run(self):
        self.log(">>> 开始执行: 系统深度清理", "header")
        self.total_deleted_size = 0
        paths = [
            (os.environ.get('TEMP'), "用户临时文件"),
            (os.path.join(os.environ.get('SystemRoot'), 'Temp'), "系统临时文件"),
            (os.path.join(os.environ.get('SystemRoot'), 'Prefetch'), "Prefetch 预读取"),
            (os.path.join(os.environ.get('LOCALAPPDATA'), r"Google\Chrome\User Data\Default\Cache\Cache_Data"),
             "Chrome 缓存"),
            (os.path.join(os.environ.get('LOCALAPPDATA'), r"Microsoft\Edge\User Data\Default\Cache\Cache_Data"),
             "Edge 缓存")
        ]
        for path, desc in paths:
            self._remove_contents(path, desc)
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        except:
            pass
        mb = self.total_deleted_size / (1024 * 1024)
        self.log(f"清理完成，共释放空间: {mb:.2f} MB", "success")
        self.log("----------------------------------------", "normal")


class MemoryOptimizer(LogicBase):
    def run(self):
        self.log(">>> 开始执行: 内存工作集压缩", "header")
        psapi = ctypes.windll.psapi
        kernel32 = ctypes.windll.kernel32
        cleaned = 0
        for pid in psutil.pids():
            if pid <= 4: continue
            try:
                handle = kernel32.OpenProcess(0x0500, False, pid)
                if handle:
                    if psapi.EmptyWorkingSet(handle): cleaned += 1
                    kernel32.CloseHandle(handle)
            except:
                continue
        self.log(f"已优化 {cleaned} 个进程的内存占用。", "success")
        mem = psutil.virtual_memory()
        self.log(f"当前可用内存: {mem.available / (1024 ** 3):.2f} GB", "success")
        self.log("----------------------------------------", "normal")

        SystemUtils.reduce_self_memory()


class GameOptimizer(LogicBase):
    def enable_ultimate_power(self):
        self.log("正在激活 '卓越性能' 电源计划...", "info")
        SystemUtils.cmd("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61")
        if not SystemUtils.cmd("powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61"):
            SystemUtils.cmd("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")

    def manage_services(self, action="stop"):
        verb = "暂停" if action == "stop" else "恢复"
        self.log(f"正在{verb}后台非核心服务 (SysMain, Spooler等)...", "info")
        services = ["SysMain", "Spooler", "WSearch", "DiagTrack", "PcaSvc"]
        for srv in services:
            SystemUtils.cmd(f"net {action} {srv}")

    def _auto_clean_loop(self):
        """后台线程：每隔3分钟自动清理一次内存"""
        self.log(">>> ⏳ 自动内存巡航已启动 (每 3 分钟执行一次)", "success")
        SystemUtils.reduce_self_memory()

        while not STOP_BG_TASK.is_set():
            if STOP_BG_TASK.wait(180):
                break

            if not STOP_BG_TASK.is_set():
                self.log(">>> [自动] 周期性内存优化执行中...", "info")
                try:
                    MemoryOptimizer(self.log).run()
                    SystemUtils.reduce_self_memory()
                except:
                    pass

    def run_boost(self):
        self.log(">>> 开始执行: 游戏模式加速", "header")
        self.enable_ultimate_power()
        self.manage_services("stop")
        try:
            NtSetTimerResolution(ctypes.c_ulong(5000), 1, ctypes.byref(ctypes.c_ulong()))
            self.log(f"系统计时器精度已锁定", "success")
        except:
            pass

        STOP_BG_TASK.clear()
        cleaner_thread = threading.Thread(target=self._auto_clean_loop)
        cleaner_thread.daemon = True
        cleaner_thread.start()

        self.log("Windows 终极游戏优化已应用！", "success")
        self.log("----------------------------------------", "normal")

    def restore(self):
        self.log(">>> 开始执行: 恢复默认设置", "header")

        if not STOP_BG_TASK.is_set():
            STOP_BG_TASK.set()
            self.log("已停止后台内存自动清理线程。", "info")

        self.manage_services("start")
        SystemUtils.cmd("netsh int tcp set global autotuninglevel=normal")
        SystemUtils.cmd("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e")
        self.log("系统服务与电源计划已恢复默认。", "success")
        self.log("----------------------------------------", "normal")


# ================= GUI 主程序 =================

class OptimizeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Windows 11 终极优化助手 - Light Blue Pro")
        self.geometry("940x680")
        self.iconbitmap(default='')
        self.configure(fg_color=GLASS_COLORS["window_bg"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === 左侧侧边栏 ===
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=10,
                                          fg_color=GLASS_COLORS["pane_bg"],
                                          border_width=1, border_color=GLASS_COLORS["pane_border"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="系统优化大师",
                                       font=ctk.CTkFont(family="Microsoft YaHei UI", size=18, weight="bold"),
                                       text_color=GLASS_COLORS["text_main"])
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 15))

        self.monitor_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.monitor_frame.grid(row=1, column=0, padx=20, pady=15, sticky="ew")

        # 字体大小保持 15号加粗
        monitor_font = ctk.CTkFont(family="Consolas", size=15, weight="bold")
        self.cpu_label = ctk.CTkLabel(self.monitor_frame, text="CPU: 0%", font=monitor_font,
                                      text_color=GLASS_COLORS["text_dim"])
        self.cpu_label.pack(anchor="w", pady=(0, 5))
        self.ram_label = ctk.CTkLabel(self.monitor_frame, text="RAM: 0%", font=monitor_font,
                                      text_color=GLASS_COLORS["text_dim"])
        self.ram_label.pack(anchor="w")

        # 按钮组
        self.create_sidebar_button(2, "🧹  系统垃圾清理", self.start_clean)
        self.create_sidebar_button(3, "🔪  浏览器粉碎", self.start_kill_browser)
        self.create_sidebar_button(4, "🧠  内存深度优化", self.start_mem_opt)
        self.create_sidebar_button(5, "💣  强力粉碎文件", self.start_force_delete)
        self.create_sidebar_button(6, "🚀  开启游戏模式", self.start_boost)
        self.create_sidebar_button(7, "🔄  恢复默认设置", self.start_restore)

        self.btn_all = ctk.CTkButton(self.sidebar_frame, text="⚡ 一键起飞 (全套)",
                                     fg_color=GLASS_COLORS["accent"],
                                     hover_color=GLASS_COLORS["accent_hover"],
                                     text_color="white",
                                     height=45, corner_radius=8,
                                     font=ctk.CTkFont(family="Microsoft YaHei UI", size=13, weight="bold"),
                                     command=self.start_all_in_one)
        self.btn_all.grid(row=8, column=0, padx=20, pady=(25, 25), sticky="ew")

        # 版本号
        self.footer_label = ctk.CTkLabel(self.sidebar_frame, text="v2.5 Pro Edition",
                                         font=ctk.CTkFont(size=10),
                                         text_color=GLASS_COLORS["text_dim"])
        self.footer_label.grid(row=11, column=0, padx=20, pady=(15, 0))

        # 作者签名 (固定显示)
        self.author_label = ctk.CTkLabel(self.sidebar_frame, text="作者: chenxin",
                                         font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
                                         text_color=GLASS_COLORS["text_dim"])
        self.author_label.grid(row=12, column=0, padx=20, pady=(2, 20))

        # === 右侧主区域 ===
        self.main_frame = ctk.CTkFrame(self, corner_radius=10,
                                       fg_color=GLASS_COLORS["pane_bg"],
                                       border_width=1, border_color=GLASS_COLORS["pane_border"])
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(self.main_frame, text="运行日志",
                                         font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
                                         text_color=GLASS_COLORS["text_dim"])
        self.header_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        self.log_box = ctk.CTkTextbox(self.main_frame,
                                      font=("Consolas", 13),
                                      text_color=GLASS_COLORS["text_main"],
                                      fg_color="transparent",
                                      border_width=0,
                                      activate_scrollbars=True)
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        self.log_message("欢迎使用。自动内存清理功能已就绪 (后台静默运行)。\n", "normal")
        self.update_monitor()

    def create_sidebar_button(self, row, text, command):
        btn = ctk.CTkButton(self.sidebar_frame, text=text, command=command,
                            anchor="w", height=40, corner_radius=8,
                            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
                            text_color=GLASS_COLORS["text_main"],
                            fg_color="transparent",
                            hover_color=GLASS_COLORS["btn_hover"],
                            border_width=1,
                            border_color=GLASS_COLORS["pane_border"])
        btn.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
        return btn

    def log_message(self, msg, msg_type="normal"):
        try:
            timestamp = datetime.now().strftime("[%H:%M:%S] ")
            full_msg = f"{timestamp} {msg}\n"

            self.log_box.configure(state="normal")

            # 日志过长清理机制
            content = self.log_box.get("1.0", "end")
            lines = int(self.log_box.index('end-1c').split('.')[0])
            if lines > 100:
                self.log_box.delete("1.0", "2.0")

            self.log_box.insert("end", full_msg)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        except:
            pass

    def run_in_thread(self, target_func):
        thread = threading.Thread(target=target_func)
        thread.daemon = True
        thread.start()

    def start_clean(self):
        self.run_in_thread(lambda: DiskCleaner(self.log_message).run())

    def start_kill_browser(self):
        self.run_in_thread(lambda: BrowserKiller(self.log_message).run())

    def start_mem_opt(self):
        self.run_in_thread(lambda: MemoryOptimizer(self.log_message).run())

    def start_boost(self):
        self.run_in_thread(lambda: GameOptimizer(self.log_message).run_boost())

    def start_restore(self):
        self.run_in_thread(lambda: GameOptimizer(self.log_message).restore())

    def start_force_delete(self):
        target_path = filedialog.askdirectory(title="选择要强制粉碎的文件夹 (小心操作!)")
        if target_path:
            confirm = messagebox.askyesno("危险操作警告",
                                          f"确定要彻底粉碎此文件夹及其所有内容吗？\n\n路径: {target_path}\n\n此操作不可恢复！")
            if confirm:
                self.run_in_thread(lambda: ForceDeleter(self.log_message).delete_target(target_path))
        else:
            self.log_message("取消文件选择。", "info")

    def start_all_in_one(self):
        def task():
            self.log_message(">>> 启动一键全自动优化流程...", "header")
            DiskCleaner(self.log_message).run()
            time.sleep(0.5)
            BrowserKiller(self.log_message).run()
            time.sleep(0.5)
            MemoryOptimizer(self.log_message).run()
            time.sleep(0.5)
            GameOptimizer(self.log_message).run_boost()
            self.log_message(">>> 任务完成！自动内存清理将在后台持续运行。", "success")

        self.run_in_thread(task)

    def update_monitor(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            self.cpu_label.configure(text=f"CPU: {cpu}%")
            self.ram_label.configure(text=f"RAM: {ram}%")
            if ram > 85:
                self.ram_label.configure(text_color="#D32F2F")
            else:
                self.ram_label.configure(text_color=GLASS_COLORS["text_dim"])

            SystemUtils.reduce_self_memory()

        except:
            pass
        self.after(2000, self.update_monitor)


if __name__ == "__main__":
    SystemUtils.elevate()
    app = OptimizeApp()
    app.mainloop()