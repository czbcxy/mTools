# mTools — 访达工具栏路径按钮

解决 macOS Finder 路径操作不如 Windows 好用的问题。核心思路是**把按钮装进访达工具栏**，点一下就在当前访达窗口里干活，不弹独立窗口。

提供三个访达工具栏按钮：

| 按钮 | 作用 |
|------|------|
| `Open Terminal Here` | 点一下在当前目录打开终端 |
| `Copy Path` | 点一下复制当前访达路径到剪贴板 |
| `Show Path Bar` | 点一下切换访达底部路径栏（点路径里的文件夹即逐级跳转，即 macOS 原生面包屑） |

> 这是"在访达上加按钮"的标准做法，全程不离开访达，没有额外窗口。

## 安装

两种等价方式，详见 **[TOOLBAR.md](TOOLBAR.md)**。

**方式一：dmg 安装包（推荐分发）**
1. 双击 `dist/mTools.dmg`
2. 把三个 `.app` 拖到访达窗口里的 **Applications**
3. 打开任意访达窗口，按住 ⌘ 把 Applications 中的三个 `.app` 逐个拖进访达工具栏
4. 终端执行 `killall Finder` 刷新

**方式二：直接用 `apps/` 目录**
按住 ⌘ 把 `apps/` 下三个 `.app` 直接拖进访达工具栏即可（建议先放到 Applications 固定位置）。

## 首次使用授权

按钮通过 `osascript` 控制访达，首次需要授权：

1. 打开 **系统设置 → 隐私与安全性 → 辅助功能**（或 自动化）
2. 把 **Terminal.app** 加进去

授权后即可正常使用。

## 项目结构

```
mTools/
├── README.md              # 本说明
├── TOOLBAR.md             # 访达工具栏按钮安装指南
├── dist/
│   └── mTools.dmg         # 分发安装包（含三个 .app + 预览图）
├── apps/                  # 三个工具栏按钮 .app（按住⌘拖入访达工具栏）
│   ├── Open Terminal Here.app
│   ├── Copy Path.app
│   └── Show Path Bar.app
└── scripts/               # 构建脚本（用于重建 .app 与图标）
    ├── build_swift_apps.py  # 用 swiftc 编译三个原生 macOS .app
    ├── make_icons.py        # 生成统一风格图标 PNG
    └── apply_icons.sh       # PNG→icns→注入→重签 流程
```

## 常见问题

**Q: 工具栏按钮点了没反应？**
检查辅助功能/自动化权限是否已授予（见上）。按钮读的是"最前面的访达窗口"，先确保访达在前台。

**Q: 图标不显示或显示旧图标？**
工具栏按钮图标在拖入时缓存。右键工具栏旧按钮 → 移除，重新按住 ⌘ 拖入新 .app，再 `killall Finder`。

**Q: 提示"无法获取访达路径"？**
检查辅助功能权限是否已授予（Terminal 需能控制 Finder）。

**Q: 面包屑跳转怎么做？**
点工具栏 **Show Path Bar** 按钮开启访达底部路径栏，点里面的文件夹即逐级跳转（macOS 原生面包屑）。

**Q: .app 能发给别人用吗？**
可以。拖进访达工具栏即用，无需安装运行环境。从其他设备下载的 dmg 首次打开若被拦截，右键 → 打开 即可。
