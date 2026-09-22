# -*- coding: utf-8 -*-
"""续做工具：把还没翻译的条目切块、把译好的结果收回来。

补充包第一轮只覆盖了大部分词表，`supplement/pending-en.json` 里是剩余条目。
以后想接着翻时，用这个脚本，不必回到当初做翻译的临时目录。

用法：
    python resume.py split                  把待译清单切成 jobs/pending_NNN.json
    python resume.py split --max-keys 200   每块最多 200 条（默认 500）
    python resume.py merge                  收回 jobs/done_*.json，更新词表
    python resume.py status                 只看进度

流程：
    1. split 生成 jobs/pending_000.json …（每个都是 {"key": "英文原文"}）
    2. 把这些文件交给模型翻译，要求「键原样、条数一致、{占位符} 原样、答案写成
       同名的 done_NNN.json 放在同一目录」
    3. merge 收回：校验后并入 supplement/frontend-add.json，
       重新算出新的 pending-en.json，并直接落地到 Claude Desktop
"""

from __future__ import print_function

import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUP = os.path.join(HERE, "supplement")
JOBS = os.path.join(HERE, "jobs")
CJK = re.compile(u"[一-鿿]")


def load(p, default=None):
    try:
        with io.open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {} if default is None else default


def save(p, d):
    parent = os.path.dirname(p)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True))


def slots(s):
    """取 ICU 顶层参数名集合，用来校验占位符有没有被译丢。"""
    out, i, depth, name = set(), 0, 0, ""
    while i < len(s):
        c = s[i]
        if c == "'" and i + 1 < len(s) and s[i + 1] == "'":
            i += 2
            continue
        if c == "{":
            depth += 1
            name = "" if depth == 1 else name + c
        elif c == "}":
            if depth == 1 and name.strip():
                out.add(name.split(",")[0].strip())
            depth -= 1
            name = ""
        elif depth >= 1:
            name += c
        i += 1
    return out


def cmd_split(argv):
    max_keys, max_chars = 500, 30000
    if "--max-keys" in argv:
        max_keys = int(argv[argv.index("--max-keys") + 1])
    pending = load(os.path.join(SUP, "pending-en.json"))
    if not pending:
        print("supplement/pending-en.json 是空的——已经没有待译条目了。")
        return 0

    for f in glob.glob(os.path.join(JOBS, "pending_*.json")):
        os.remove(f)

    items = sorted(pending.items(), key=lambda kv: (len(kv[1]), kv[0]))
    jobs, cur, cc = [], {}, 0
    for k, v in items:
        if cur and (cc + len(v) > max_chars or len(cur) >= max_keys):
            jobs.append(cur)
            cur, cc = {}, 0
        cur[k] = v
        cc += len(v) + 20
    if cur:
        jobs.append(cur)

    for i, j in enumerate(jobs):
        save(os.path.join(JOBS, "pending_%03d.json" % i), j)

    print("待译 %d 条，切成 %d 块，每块最多 %d 条" % (len(pending), len(jobs), max_keys))
    print("已写入 " + JOBS)
    print()
    print("下一步：把这些 pending_NNN.json 交给模型翻译，译好的结果命名为")
    print("        done_NNN.json 放回同一目录，然后运行  python resume.py merge")
    return 0


def cmd_merge(argv):
    add_path = os.path.join(SUP, "frontend-add.json")
    add = load(add_path)
    en_all = load(os.path.join(SUP, "pending-en.json"))

    files = sorted(glob.glob(os.path.join(JOBS, "done_*.json")))
    if not files:
        print("jobs/ 里没有 done_*.json，没什么可收回的。")
        return 0

    got, bad = {}, []
    for f in files:
        srcpath = os.path.join(JOBS, os.path.basename(f).replace("done_", "pending_"))
        src = load(srcpath)
        if not src:
            print("  [跳过] 找不到对应的 %s" % os.path.basename(srcpath))
            continue
        out = load(f)
        miss = set(src) - set(out)
        if miss:
            bad.append("%s 少 %d 条（可能是写文件时被截断）"
                       % (os.path.basename(f), len(miss)))
        for k, v in out.items():
            if k not in src:
                bad.append("%s 多出键 %s" % (os.path.basename(f), k))
                continue
            if not isinstance(v, str) or not v.strip():
                bad.append("%s/%s 空值" % (os.path.basename(f), k))
                continue
            if slots(src[k]) != slots(v):
                bad.append("%s/%s 占位符对不上" % (os.path.basename(f), k))
                continue
            got[k] = v

    add.update(got)
    save(add_path, add)

    left = {k: v for k, v in en_all.items() if k not in got}
    save(os.path.join(SUP, "pending-en.json"), left)

    print("收回 %d 条（来自 %d 个文件）" % (len(got), len(files)))
    if bad:
        print()
        print("!! %d 处有问题，已跳过：" % len(bad))
        for b in bad[:20]:
            print("   ", b)
    print("frontend-add.json 现有 %d 条" % len(add))
    print("剩余未译 %d 条（已更新 pending-en.json）" % len(left))
    print()
    print("重新落地：  python apply.py")
    return 0


def cmd_status(argv):
    pending = load(os.path.join(SUP, "pending-en.json"))
    add = load(os.path.join(SUP, "frontend-add.json"))
    print("frontend-add.json  %6d 条" % len(add))
    print("pending-en.json    %6d 条待译" % len(pending))
    done = sorted(glob.glob(os.path.join(JOBS, "done_*.json")))
    print("jobs/ 已收回文件   %6d 个" % len(done))
    raw = sorted(glob.glob(os.path.join(JOBS, "pending_*.json")))
    print("jobs/ 已切块文件   %6d 个" % len(raw))
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("split", "merge", "status"):
        print(__doc__)
        return 1
    return {"split": cmd_split, "merge": cmd_merge, "status": cmd_status}[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
