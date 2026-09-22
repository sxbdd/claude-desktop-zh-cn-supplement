# -*- coding: utf-8 -*-
"""重新组装并打包 release\\Claude-Desktop-中文化补丁.zip

改过 supplement\\*.json 或 apply.py 之后跑一次即可：

    python build_release.py

两个必须记住的点：

1. **批处理文件必须是 GBK 编码 + CRLF 行尾 + `chcp 936`。** cmd.exe 对 LF-only 的 .bat
   会解析错乱，对 `chcp 65001` 下的中文提示会按字节截断。细节见 `fix_bat()`。
2. **中文文件名在 zip 里要带 UTF-8 标志**，否则解压出来是乱码。Python 的
   `zipfile` 对非 ASCII 名会自动设置，这里顺手校验一下。
"""

from __future__ import print_function

import io
import os
import shutil
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "release", "Claude-Desktop-中文化补丁")
ZIP = os.path.join(HERE, "release", "Claude-Desktop-中文化补丁.zip")


def sync_sources():
    """把项目根的 apply.py 与 supplement/ 同步进成品目录。"""
    shutil.copy2(os.path.join(HERE, "apply.py"), os.path.join(DIST, "apply.py"))
    for n in os.listdir(os.path.join(HERE, "supplement")):
        # pending-en.json 是续做用的待译清单，对接收者没意义
        if n.endswith(".json") and n != "pending-en.json":
            shutil.copy2(os.path.join(HERE, "supplement", n),
                         os.path.join(DIST, "supplement", n))
    print("已同步 apply.py 与 supplement/*.json")


def fix_bat():
    """规范成品里的 .bat：GBK 编码 + CRLF 行尾 + chcp 936。

    cmd.exe 有两个老毛病，都实测踩过：

    - **LF-only 的 .bat**：`goto` 找不到标签、行被拼接，满屏「不是内部或外部命令」。
    - **`chcp 65001` + 中文提示**：cmd 读 bat 时按字节切行，UTF-8 的多字节汉字
      在缓冲区边界被截断，后半句会被当成独立命令执行。

    所以中文 bat 一律按中文 Windows 的传统做法：GBK 存盘、强制 936 代码页。
    Python 那边输出的是 Unicode，Windows 控制台走 WriteConsoleW，不受影响；
    但 bat 里额外设了 `PYTHONIOENCODING=gbk`，兼顾输出被重定向的场合。

    **只处理本包自己那三个 bat，绝不碰 upstream\\ 里的。** 上游的
    install-windows.bat 是给 PowerShell 用的，它的 `chcp 65001` 不能动——
    改成 936 会让上游脚本输出的中文全乱码。
    """
    for f in sorted(os.listdir(DIST)):
        if not f.endswith(".bat"):
            continue
        p = os.path.join(DIST, f)
        raw = open(p, "rb").read()
        if b"chcp 65001" in raw:
            try:
                txt = raw.decode("utf-8")
            except UnicodeDecodeError:
                txt = raw.decode("gbk", "replace")
            txt = txt.replace("chcp 65001 >nul", "chcp 936 >nul")
            print("  转 GBK + chcp 936: %s" % f)
        else:
            txt = raw.decode("gbk", "replace")
        txt = txt.replace("\r\n", "\n").replace("\n", "\r\n")
        open(p, "wb").write(txt.encode("gbk"))


def clean_cache():
    for root, dirs, _ in os.walk(DIST):
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))
                dirs.remove(d)


def make_zip():
    if os.path.exists(ZIP):
        os.remove(ZIP)
    n = 0
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for root, dirs, files in os.walk(DIST):
            dirs.sort()
            for f in sorted(files):
                p = os.path.join(root, f)
                arc = os.path.join("Claude-Desktop-中文化补丁",
                                   os.path.relpath(p, DIST)).replace("\\", "/")
                z.write(p, arc)
                n += 1
    z = zipfile.ZipFile(ZIP)
    bad = [i.filename for i in z.infolist()
           if not (i.flag_bits & 0x800) and any(ord(c) > 127 for c in i.filename)]
    print("打包完成：%d 个文件，%.2f MB" % (n, os.path.getsize(ZIP) / 1024 / 1024))
    if bad:
        print("！中文名未标 UTF-8，解压会乱码：%s" % bad)

    # 再复制一份 ASCII 文件名的副本，专供 GitHub Release 上传：
    # gh CLI 会把中文附件名截断，实测 "Claude-Desktop-中文化补丁.zip"
    # 上传后变成了 "Claude-Desktop-.zip"。zip 内部的目录名仍是中文，不受影响。
    ascii_zip = os.path.join(os.path.dirname(ZIP), "Claude-Desktop-zh-CN-Patch.zip")
    shutil.copy2(ZIP, ascii_zip)
    print("发布用副本：%s（%.2f MB）"
          % (os.path.basename(ascii_zip), os.path.getsize(ascii_zip) / 1024 / 1024))
    return 0 if not bad else 1


def main():
    print("=" * 60)
    print(" 重新打包 Claude Desktop 中文化补丁")
    print("=" * 60)
    sync_sources()
    fix_bat()
    clean_cache()
    return make_zip()


if __name__ == "__main__":
    raise SystemExit(main())
