# SuperAddr — macOS 访达路径增强工具

解决 macOS Finder 路径操作不如 Windows 好用的问题。核心思路是**把按钮装进访达工具栏**，点一下就在当前访达窗口里干活，不弹独立窗口。

提供三大能力（对应三个工具栏按钮）：

- **面包屑导航** — 用访达原生路径栏（Show Path Bar 按钮一键开启），点路径里的文件夹直接跳转
- **一键复制路径** — 无需右键+Option
- **一键打开终端** — 在访达当前位置打开终端

## 安装（推荐：访达工具栏按钮）

详见 **[TOOLBAR.md](TOOLBAR.md)**。一句话：把 `apps/` 下三个 `.app` 按住 ⌘ 拖进访达工具栏即可。

| 按钮 | 作用 |
|------|------|
| `Open Terminal Here.app` | 点一下在当前目录打开终端 |
| `Copy Path.app` | 点一下复制当前访达路径 |
| `Show Path Bar.app` | 点一下切换访达底部路径栏（面包屑跳转） |

> 这是"在访达上加按钮"的标准做法，全程不离开访达，没有额外窗口。

## 备选方案（独立 App / 命令行）

- **独立 App**：`dist/SuperAddr.app`（双击运行，会弹一个浮动面包屑窗口；适合没有工具栏按钮时使用）
- **命令行**：`chmod +x install.sh && ./install.sh` 后，终端输入 `saddr` / `saddr --copy` / `saddr --term`

详见下方"功能一览"第 1 节（独立窗口）与第 3 节（右键菜单）。

## 功能一览

### 1. 面包屑路径导航（主窗口）

> 这是独立 App（`SuperAddr.app`）的模式：弹出一个浮动窗口显示当前访达路径，每段可点击跳转。
> 若你用的是**工具栏按钮**方案，面包屑跳转请用 `Show Path Bar` 按钮开启访达原生路径栏。

```
📍 访达路径                              ✕
 /  ▸  Users  ▸  chengzhengbo  ▸  Documents  ▸  项目
                                         ↑ 当前目录

 [📋 复制路径]  [⌨️ 打开终端]  [⬆ 上级目录]  [🔄 刷新]
```

- 点击任意路径片段 → 在访达中打开该目录
- 窗口失焦自动关闭，按 Esc 也可关闭
- "上级目录"按钮快捷跳转

### 2. 命令行快捷操作

| 命令 | 功能 |
|------|------|
| `saddr` | 打开面包屑导航窗口 |
| `saddr --copy` | 复制当前访达路径到剪贴板 |
| `saddr --term` | 在访达当前位置打开终端 |
| `saddr --path` | 打印当前访达路径 |
| `saddr --parent` | 跳转到上级目录 |

### 3. Finder 右键菜单

在任意文件夹上右键 → **Services** → 

- **Open Terminal Here** — 在该目录打开终端
- **Copy Path** — 复制该目录路径

### 4. Finder 工具栏按钮（可选）

安装后，`~/Applications/SuperAddr/` 下会生成两个 `.app`：

1. 打开访达，浏览到 `~/Applications/SuperAddr/`
2. 按住 ⌘Cmd 键，将 `Open Terminal Here.app` 拖入访达工具栏
3. 同样拖入 `Copy Path.app`

之后在访达工具栏点一下就能用。

## 首次使用授权

macOS 安全策略要求授权（点按钮时需要控制访达）：

1. 打开 **系统设置 → 隐私与安全性 → 辅助功能**
2. 添加运行这些按钮的程序（通常是 **Terminal.app**，或你启动它们的终端）
3. 如使用右键服务，可能还需添加 **Automator**

授权后即可正常使用。

## 项目结构

```
super-addr/
├── super_addr.py          # 独立 App 主程序（面包屑+操作面板）
├── install.sh             # 一键安装脚本（CLI + 右键服务）
├── requirements.md        # 需求分析文档
├── TOOLBAR.md             # 访达工具栏按钮安装指南（核心用法）
├── dist/
│   ├── SuperAddr.app      # 已打包的独立应用（内置Python+Tk）
│   └── SuperAddr.dmg      # 分发盘：拖入 Applications 即可安装
├── scripts/
│   ├── saddr              # CLI 入口
│   ├── open-terminal.scpt # AppleScript: 打开终端
│   ├── copy-path.scpt     # AppleScript: 复制路径
│   └── show-pathbar.scpt  # AppleScript: 切换路径栏
└── apps/                  # 编译后的工具栏 .app（按住⌘拖入Finder工具栏）
    ├── Open Terminal Here.app
    ├── Copy Path.app
    └── Show Path Bar.app
```

## 常见问题

**Q: 工具栏按钮点了没反应？**
检查辅助功能权限是否已授予（见上）。按钮读的是"最前面的访达窗口"，先确保访达在前台。

**Q: 右键菜单不出现？**
运行 `killall Finder` 刷新访达。

**Q: 提示"无法获取访达路径"？**
检查辅助功能权限是否已授予。

**Q: 想用 iTerm2 代替 Terminal？**
独立 App 会自动检测 iTerm2 优先使用；工具栏按钮默认用 Terminal，可自行改 `scripts/open-terminal.scpt`。

**Q: 面包屑跳转怎么做？**
点工具栏 **Show Path Bar** 按钮开启访达底部路径栏，点里面的文件夹即逐级跳转（macOS 原生面包屑）。


**Q: .app 能发给别人用吗？**
可以。`SuperAddr.app` 自带 Python 运行环境，拷贝到任何 Apple Silicon Mac（macOS 11+）都能直接双击运行。从其他设备下载的 .dmg 首次打开若被拦截，右键 → 打开 即可。

# mTools
