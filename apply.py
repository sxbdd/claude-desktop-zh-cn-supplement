# -*- coding: utf-8 -*-
"""Claude Desktop 中文补充包 —— 安装 / 卸载

上游汉化包 claude-desktop-zh-cn 的中文词表收得不全，它没收录的键在界面上会
回落到英文。本脚本把补充词表合并进去，可重复执行。

用法（需要管理员权限）：
    python apply.py               安装 / 重新安装
    python apply.py --check       只检查，不写入任何文件
    python apply.py --uninstall   卸载，从备份还原
"""

from __future__ import print_function

import glob
import io
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUP = os.path.join(HERE, "supplement")
BAK = ".bak-supplement"

# (补充词表文件, 应用内相对路径, 说明)
TARGETS = [
    ("desktop-add.json", "zh-CN.json",
     "菜单栏 / 对话框"),
    ("frontend-add.json", os.path.join("ion-dist", "i18n", "zh-CN.json"),
     "网页前端界面"),
    ("dynamic-zh-CN.json", os.path.join("ion-dist", "i18n", "dynamic", "zh-CN.json"),
     "模型选择器 / 思考模式"),
]

SHELL_EN = "en-US.json"
FRONT_EN = os.path.join("ion-dist", "i18n", "en-US.json")


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def save(p, d):
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True))


def find_app_resources():
    """定位 Claude Desktop 的 app\\resources 目录，返回 (路径, 全部候选)。"""
    roots = []
    for drv in "CDEFGH":
        roots.append("%s:\\Program Files\\WindowsApps" % drv)
        roots.append("%s:\\WindowsApps" % drv)
    for var in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)"):
        v = os.environ.get(var)
        if v:
            roots.append(os.path.join(v, "WindowsApps"))
    # 非商店版（官方 exe 安装包）
    for var in ("LOCALAPPDATA", "APPDATA"):
        v = os.environ.get(var)
        if v:
            roots.append(os.path.join(v, "AnthropicClaude"))
            roots.append(os.path.join(v, "Programs", "Claude"))

    cands = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        pats = [os.path.join(root, "Claude_*_x64__*", "app", "resources"),
                os.path.join(root, "Claude_*", "app", "resources"),
                os.path.join(root, "app-*", "resources"),
                os.path.join(root, "resources")]
        for pat in pats:
            try:
                cands += glob.glob(pat)
            except Exception:
                pass

    good = [c for c in cands if os.path.isfile(os.path.join(c, "en-US.json"))]
    # 同一个安装可能通过软链接/存储位置迁移在多个盘出现，按真实路径去重
    seen, uniq = set(), []
    for c in good:
        k = os.path.normcase(os.path.realpath(c))
        if k not in seen:
            seen.add(k)
            uniq.append(c)

    def ver(p):
        m = re.search(r"Claude_([\d.]+)_", p) or re.search(r"app-([\d.]+)", p)
        return [int(x) for x in m.group(1).split(".")] if m else [0]

    uniq.sort(key=ver)
    return (uniq[-1] if uniq else None), uniq


def coverage(res, zh_rel, en_rel, label):
    """打印中文覆盖率：分母是英文词表的键。"""
    zh_p, en_p = os.path.join(res, zh_rel), os.path.join(res, en_rel)
    if not (os.path.isfile(zh_p) and os.path.isfile(en_p)):
        return
    zh, en = load(zh_p), load(en_p)
    missing = [k for k in en if k not in zh]
    print("    %s：中文 %d 条 / 英文 %d 条，缺键 %d 条"
          % (label, len(zh), len(en), len(missing)))
    if missing:
        print("      （缺的键会显示成英文，多半是这个 Claude 版本比词表新）")


def do_install(res):
    total = 0
    for src_name, rel, label in TARGETS:
        src = os.path.join(SUP, src_name)
        if not os.path.isfile(src):
            print("  [跳过] 缺少 supplement\\%s" % src_name)
            continue
        add = load(src)
        target = os.path.join(res, rel)
        cur = load(target) if os.path.isfile(target) else {}
        before = len(cur)
        cur.update(add)
        d = os.path.dirname(target)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        # 备份只做一次，保留最初那份
        b = target + BAK
        if os.path.isfile(target) and not os.path.exists(b):
            shutil.copy2(target, b)
            print("    已备份 -> %s" % os.path.basename(b))
        save(target, cur)
        print("  [%s] 新增 %d 条（共 %d 条）" % (label, len(cur) - before, len(cur)))
        total += len(cur) - before
    return total


def do_uninstall(res):
    n = 0
    for _, rel, label in TARGETS:
        target = os.path.join(res, rel)
        b = target + BAK
        if os.path.isfile(b):
            shutil.copy2(b, target)
            os.remove(b)
            print("  [%s] 已还原" % label)
            n += 1
        else:
            print("  [%s] 没有找到备份，跳过" % label)
    return n


def main():
    args = [a.lower() for a in sys.argv[1:]]
    check = "--check" in args or "-c" in args
    uninstall = "--uninstall" in args or "-u" in args

    print("=" * 62)
    print(" Claude Desktop 中文补充包")
    print("=" * 62)

    res, all_cands = find_app_resources()
    if not res:
        print("找不到 Claude Desktop，或没有权限读取它的安装目录。")
        print("请在「以管理员身份运行」的命令行里再试一次。")
        print("若 Claude 装在非常规位置，请把它的 app\\resources 路径告诉作者。")
        return 1

    print("应用目录: %s" % res)
    if len(all_cands) > 1:
        print("（另外还找到 %d 处旧版本目录，已自动选最新的一处）" % (len(all_cands) - 1))

    if not os.path.isfile(os.path.join(res, "zh-CN.json")):
        print("")
        print("！！这个目录里没有 zh-CN.json —— 说明上游汉化包还没装。")
        print("   请先双击 upstream\\install-windows.bat 装好上游汉化包，")
        print("   再回来运行本脚本。光有本补充包是不够的。")
        return 1
    print("")

    if uninstall:
        n = do_uninstall(res)
        print("")
        print("已还原 %d 个文件。完全退出并重新打开 Claude Desktop 后生效。" % n)
        return 0

    if check:
        print("仅检查，未写入：")
        coverage(res, "zh-CN.json", SHELL_EN, "菜单栏 / 对话框")
        coverage(res, os.path.join("ion-dist", "i18n", "zh-CN.json"), FRONT_EN, "网页前端界面")
        return 0

    try:
        total = do_install(res)
    except (IOError, OSError) as e:
        print("")
        print("写入失败：%s" % e)
        print("没有管理员权限就改不动 WindowsApps 里的文件。")
        print("请右键「以管理员身份运行」本脚本所在的 .bat，再试一次。")
        return 1

    print("")
    print("本次写入 %d 条。复核覆盖率：" % total)
    coverage(res, "zh-CN.json", SHELL_EN, "菜单栏 / 对话框")
    coverage(res, os.path.join("ion-dist", "i18n", "zh-CN.json"), FRONT_EN, "网页前端界面")
    print("")
    print("完成。请完全退出并重新打开 Claude Desktop 使其生效")
    print("（不是关窗口，要从托盘图标退出）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
