#!/usr/bin/env python3
"""
Build three native Swift .app bundles for Finder toolbar buttons.
v6: Swift 6 strict mode compatible — all fixes applied.
"""

import os, subprocess, shutil

APPS_DIR = "/Users/chengzhengbo/WorkBuddy/super-addr/apps"
ICNS_TMP = "/tmp/icicons2"

SWIFT_TERMINAL = r'''
import Foundation

func runAS(_ script: String) -> String {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
    p.arguments = ["-e", script]
    let pipe = Pipe()
    p.standardOutput = pipe
    p.standardError = pipe
    do { try p.run(); p.waitUntilExit() }
    catch { return "" }
    let d = pipe.fileHandleForReading.readDataToEndOfFile()
    return String(data: d, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
}

let path = runAS("""
tell application "Finder"
    try
        set win to front Finder window
        set targetPath to (target of win as alias)
        return POSIX path of targetPath
    on error
        try
            return POSIX path of (selection as alias)
        on error
            return POSIX path of (desktop as alias)
        end try
    end try
end tell
""")

guard !path.isEmpty else {
    _ = runAS("display notification \"无法获取访达路径\" with title \"SuperAddr\" sound name \"default\"")
    exit(1)
}

_ = runAS("""
tell application "Terminal"
    activate
    if not (exists window 1) then
        do script "cd \(path)"
    else
        set newTab to do script "cd \(path)"
    end if
end tell
""")

_ = runAS("""
tell application "iTerm2"
    activate
    if (count of windows) = 0 then create window with default profile
    tell current session of current window
        write text "cd \(path); clear"
    end tell
end tell
""")

exit(0)
'''

SWIFT_COPY = r'''
import Foundation

func runAS(_ script: String) -> String {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
    p.arguments = ["-e", script]
    let pipe = Pipe()
    p.standardOutput = pipe
    p.standardError = pipe
    do { try p.run(); p.waitUntilExit() }
    catch { return "" }
    let d = pipe.fileHandleForReading.readDataToEndOfFile()
    return String(data: d, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
}

let path = runAS("""
tell application "Finder"
    try
        set win to front Finder window
        set targetPath to (target of win as alias)
        return POSIX path of targetPath
    on error
        try
            return POSIX path of (selection as alias)
        on error
            return POSIX path of (desktop as alias)
        end try
    end try
end tell
""")

guard !path.isEmpty else {
    _ = runAS("display notification \"无法获取路径\" with title \"SuperAddr\" sound name \"default\"")
    exit(1)
}

_ = runAS("set the clipboard to \"" + path + "\"")
_ = runAS("display notification \"已复制: " + path + "\" with title \"SuperAddr\" sound name \"default\"")
exit(0)
'''

SWIFT_PATHBAR = r'''
import Foundation

func runAS(_ script: String) -> String {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
    p.arguments = ["-e", script]
    let pipe = Pipe()
    p.standardOutput = pipe
    p.standardError = pipe
    do { try p.run(); p.waitUntilExit() }
    catch { return "" }
    let d = pipe.fileHandleForReading.readDataToEndOfFile()
    return String(data: d, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
}

let msg = runAS("""
tell application "Finder"
    try
        set win to front Finder window
        set currentVal to shows path bar of win
        set shows path bar of win to not currentVal
        if not currentVal then
            return "路径栏已显示"
        else
            return "路径栏已隐藏"
        end if
    on error errMsg number errNum
        return "切换失败 (" & errNum & ")"
    end try
end tell
""")

_ = runAS("display notification \"" + (msg.isEmpty ? "完成" : msg) + "\" with title \"SuperAddr\" sound name \"default\"")
exit(0)
'''

APPS = [
    ("Open Terminal Here", "OpenTerminalHere", SWIFT_TERMINAL, "terminal"),
    ("Copy Path",          "CopyPath",         SWIFT_COPY,     "copy"),
    ("Show Path Bar",      "ShowPathBar",      SWIFT_PATHBAR,  "pathbar"),
]

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.stdout.strip(): print(f"  {r.stdout.strip()}")
    if r.returncode != 0 and r.stderr.strip(): print(f"  [stderr] {r.stderr.strip()}")
    return r.returncode == 0

def make_app(name, exe_name, swift_src, icon_name):
    app_path = os.path.join(APPS_DIR, f"{name}.app")
    contents = os.path.join(app_path, "Contents")
    macos_dir = os.path.join(contents, "MacOS")
    resources = os.path.join(contents, "Resources")

    if os.path.exists(app_path):
        shutil.rmtree(app_path)

    os.makedirs(macos_dir)
    os.makedirs(resources)

    src_path = os.path.join(macos_dir, f"{exe_name}.swift")
    exe_path = os.path.join(macos_dir, exe_name)
    with open(src_path, "w") as f:
        f.write(swift_src)

    print(f"\n--- Compiling {name} ---")
    ok = sh(f'swiftc -O -o "{exe_path}" "{src_path}" 2>&1')
    if not ok:
        print(f"  COMPILE FAILED for {name}")
        return False

    os.remove(src_path)
    os.chmod(exe_path, 0o755)

    icns_src = os.path.join(ICNS_TMP, f"{icon_name}.icns")
    icns_dst = os.path.join(resources, "AppIcon.icns")
    if os.path.exists(icns_src):
        shutil.copy2(icns_src, icns_dst)
        print(f"  icon: {os.path.getsize(icns_dst)} bytes")

    plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key><string>en</string>
    <key>CFBundleExecutable</key><string>{exe_name}</string>
    <key>CFBundleIconFile</key><string>AppIcon</string>
    <key>CFBundleIconName</key><string>AppIcon</string>
    <key>CFBundleIdentifier</key><string>com.superaddr.{exe_name.lower()}</string>
    <key>CFBundleInfoDictionaryVersion</key><string>6.0</string>
    <key>CFBundleName</key><string>{name}</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>CFBundleShortVersionString</key><string>1.0</string>
    <key>CFBundleVersion</key><string>1</string>
    <key>LSMinimumSystemVersion</key><string>10.15</string>
    <key>NSHighResolutionCapable</key><true/>
    <key>LSUIElement</key><true/>
</dict>
</plist>'''
    with open(os.path.join(contents, "Info.plist"), "w") as f:
        f.write(plist)

    sh(f'codesign --force --deep --sign - "{app_path}"')
    print(f"  signed ✓")
    return True


print("=== Building v6: Swift 6 strict + osascript subprocess ===\n")
for name, exe, src, icon in APPS:
    make_app(name, exe, src, icon)

print("\n✅ Done!")
