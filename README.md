✨ 主要功能

📊 实时监控: 侧边栏实时显示 CPU 和 RAM 占用率。

🧹 系统垃圾清理: 深度扫描并清理系统临时文件、浏览器缓存 (Chrome/Edge) 及回收站。

🧠 智能内存优化:

工作集 (Working Set) 压缩技术。

后台静默线程：每 3 分钟自动执行一次无感内存清理。

🚀 游戏/性能模式:

一键激活 Windows "卓越性能" 电源计划。

暂停非核心后台服务 (SysMain, WSearch 等)。

锁定系统计时器精度以降低延迟。

💣 强力文件粉碎: 能够强制删除被系统占用或无法常规删除的文件/文件夹。

🔪 隐私保护: 一键终止所有主流浏览器进程 (Edge, Chrome, Firefox, etc.) 及其残留后台。

🎨 现代化 UI: 基于 CustomTkinter 的玻璃拟态风格界面，支持高分屏。

🛠️ 安装与运行

环境要求

Windows 10 或 Windows 11

Python 3.8 或更高版本

必须以管理员身份运行 (程序会自动请求提权)

1. 克隆仓库

git clone [https://github.com/chenxin799/Win11-Ultimate-Optimizer.git](https://github.com/chenxin799/Win11-Ultimate-Optimizer.git)
cd Win11-Ultimate-Optimizer



2. 安装依赖

pip install -r requirements.txt



3. 运行程序

python optimizer.py



📦 如何打包为 EXE

如果你想生成独立的可执行文件（无需安装 Python 即可运行），可以使用 PyInstaller：

安装 PyInstaller:

pip install pyinstaller



执行打包命令 (去除控制台窗口):

pyinstaller --noconsole --onefile --name="Win11Optimizer" --icon=icon.ico optimizer.py



(注：你需要自备一个 icon.ico 图标文件，如果没有，可以去掉 --icon 参数)

⚠️ 免责声明 (Disclaimer)

本工具涉及系统底层操作（如注册表修改、服务管理、进程终止）。

虽然代码经过测试，但在不同的系统环境下可能会有不同表现。

请在使用“强力粉碎文件”功能前，务必确认文件内容。

作者不对因使用本软件导致的任何数据丢失或系统不稳定承担责任。建议在使用前创建系统还原点。

👤 作者

chenxin - 核心开发

📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。✨ 主要功能

📊 实时监控: 侧边栏实时显示 CPU 和 RAM 占用率。

🧹 系统垃圾清理: 深度扫描并清理系统临时文件、浏览器缓存 (Chrome/Edge) 及回收站。

🧠 智能内存优化:

工作集 (Working Set) 压缩技术。

后台静默线程：每 3 分钟自动执行一次无感内存清理。

🚀 游戏/性能模式:

一键激活 Windows "卓越性能" 电源计划。

暂停非核心后台服务 (SysMain, WSearch 等)。

锁定系统计时器精度以降低延迟。

💣 强力文件粉碎: 能够强制删除被系统占用或无法常规删除的文件/文件夹。

🔪 隐私保护: 一键终止所有主流浏览器进程 (Edge, Chrome, Firefox, etc.) 及其残留后台。

🎨 现代化 UI: 基于 CustomTkinter 的玻璃拟态风格界面，支持高分屏。

🛠️ 安装与运行

环境要求

Windows 10 或 Windows 11

Python 3.8 或更高版本

必须以管理员身份运行 (程序会自动请求提权)

1. 克隆仓库

git clone [https://github.com/chenxin799/Win11-Ultimate-Optimizer.git](https://github.com/chenxin799/Win11-Ultimate-Optimizer.git)
cd Win11-Ultimate-Optimizer



2. 安装依赖

pip install -r requirements.txt



3. 运行程序

python optimizer.py



📦 如何打包为 EXE

如果你想生成独立的可执行文件（无需安装 Python 即可运行），可以使用 PyInstaller：

安装 PyInstaller:

pip install pyinstaller



执行打包命令 (去除控制台窗口):

pyinstaller --noconsole --onefile --name="Win11Optimizer" --icon=icon.ico optimizer.py



(注：你需要自备一个 icon.ico 图标文件，如果没有，可以去掉 --icon 参数)

⚠️ 免责声明 (Disclaimer)

本工具涉及系统底层操作（如注册表修改、服务管理、进程终止）。

虽然代码经过测试，但在不同的系统环境下可能会有不同表现。

请在使用“强力粉碎文件”功能前，务必确认文件内容。

作者不对因使用本软件导致的任何数据丢失或系统不稳定承担责任。建议在使用前创建系统还原点。

👤 作者

陈鑫 - 核心开发

📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。
