# Claude Desktop 中文补充包

给第三方汉化包 **claude-desktop-zh-cn** 打的补丁，补上它词表里缺的中文翻译。

**状态：已完成。** 英文词表里的 29,442 个键**全部有中文，缺键 0 条**。

## 为什么需要它

`javaht/claude-desktop-zh-cn`（v1.4.7）的中文词表不完整——**这是它的目录本身没收全，
不是安装失败**：

| 词表 | 英文条目 | 汉化包自带中文 | 结果 |
|---|---|---|---|
| 桌面壳层 `resources\zh-CN.json` | 705 | 362 | 343 条显示英文 |
| 网页前端 `ion-dist\i18n\zh-CN.json` | 29,442 | 12,037 | 17,405 条显示英文 |

应用查不到键就回落到 `en-US`，显示英文原文。所以装完上游补丁后，界面里「设置」是中文，
但「Settings」「Keyboard Shortcuts」「Update now」这些还是英文。上游最新版仍是 1.4.7，
没有更新可等，只能自己补。

## 当前状态（2026-09-23）

| | 上游补丁 | 加上本补充包 |
|---|---|---|
| 桌面壳层 | 362 / 705 | **705 / 705，缺键 0** |
| 网页前端 | 12,037 / 29,442 | **29,442 / 29,442，缺键 0** |

与英文完全相同的只剩 397 条，全是有意保留的品牌名 / 产品名 / 技术标识符
（`Google Play`、`GitHub App`、`Claude Pro`、`Anthropic Sans`、OAuth scope 串、
PEM 证书示例等），符合术语表。**没有漏译的句子。**

## 目录

```
supplement/
  desktop-add.json       菜单栏、对话框（422 条）
  frontend-add.json      网页前端界面（21,161 条）
  dynamic-zh-CN.json     模型选择器 / 思考模式 / 努力程度（47 条，上游没有这个文件）
  pending-en.json        待译清单，现为 0 条
apply.py                 落地脚本（安装 / --check / --uninstall）
resume.py                续做工具（split / merge / status）
应用补充汉化.bat           本地双击运行
release/                 转发给别人的成品
  Claude-Desktop-中文化补丁/    上游 1.4.7 + 本补充包 + 一键脚本 + 说明.md
  Claude-Desktop-中文化补丁.zip  1.85 MB，直接发这个
```

## 用法（本机）

1. 先确认第三方汉化包已装好（见下方「汉化包本身」）。
2. 双击 **应用补充汉化.bat**，或运行 `python apply.py`。
3. 完全退出并重新打开 Claude Desktop（不是关窗口，要退到托盘也没了）。

脚本可反复运行（幂等），首次改动前把原文件备份成 `*.bak-supplement`。
加 `--check` 只看覆盖率不写入，`--uninstall` 从备份还原。

## 转发给别人

直接发 `release\Claude-Desktop-中文化补丁.zip`。接收者解压后按 `说明.md` 走两步：
先跑 `第1步-安装上游汉化.bat`（模式选 1），再跑 `第2步-安装补充汉化.bat`。

包里已经把上游 1.4.7 一起打包了（MIT 许可，保留其 LICENSE），所以对方不用自己去 GitHub 下。

改过词表或 `apply.py` 之后，跑一次打包脚本即可：

```
python build_release.py
```

它会把项目根的 `apply.py` 和 `supplement/*.json` 同步进成品目录、规范 bat 编码、打 zip。

**打包有两个坑，都实测踩过，脚本里已处理：**

1. **自有 bat 必须 GBK 编码 + CRLF + `chcp 936`。** cmd.exe 对 LF-only 的 bat 会
   `goto` 找不到标签；对 `chcp 65001` 下的中文提示会按字节切行，把半句话当成
   独立命令执行（报「不是内部或外部命令」）。别指望 UTF-8 写中文 bat。
2. **绝不能碰 `upstream/` 里的任何文件。** 上游的 `install-windows.bat` 用
   `chcp 65001` 配合它的 PowerShell 脚本，被改成 936 会让上游输出的中文全乱码。
   打包脚本只处理顶层那三个 bat。

中文文件名在 zip 里要带 UTF-8 标志，否则解压乱码——Python 的 `zipfile` 会自动设置，
`build_release.py` 每次会校验一遍。

## 续做（如果 Claude 更新带来新词条）

```
python resume.py split     # 把 pending-en.json 切成 jobs/pending_NNN.json
```

逐块翻译，**要求：键逐字符原样保留、条数一致、`{占位符}` 原样保留、ICU 的
`{x, plural, one {…} other {…}}` 骨架原样保留**，结果命名成同名的 `done_NNN.json` 放回
`jobs\`。然后：

```
python resume.py merge     # 校验并收回，重算 pending-en.json
python apply.py
```

`merge` 会用「少 N 条 / 多出键 / 空值 / 占位符对不上」标出问题并**整块跳过**有问题的文件，
这是唯一可靠的正确性信号。收尾阶段就被它拦下过 5 次，全是哈希键誊写错误。

## 什么时候需要重跑

- Claude Desktop **自动更新**之后（更新会整体覆盖补丁）。
- 重装了 `claude-desktop-zh-cn` 汉化包之后（它的安装脚本只写自己词表里的内容）。

两种情况都是**先重打上游、再跑一次补充包**。

## 汉化包本身

`D:\Administrator\下载\claude-desktop-zh-cn-1.4.7\claude-desktop-zh-cn-1.4.7\`
（分发副本已放进 `release\...\upstream\`，是干净的原版）

- 安装：双击 `install-windows.bat` → 选 `1`（第三方 API / Cowork 兼容）→ 选 `1`（简体中文）。
  安装前必须先退出 Claude Desktop。
- 卸载：同样的入口选 `4`。
- 模式 1 不改 `app.asar` 和 `Claude.exe`，所以 Authenticode 签名和 Cowork 沙箱都正常。
  代价是登录 claude.ai 之后的在线聊天页面仍是英文（那需要模式 2，会破坏签名）。

## 备注

- 补充包只做一件事：往应用的 `zh-CN.json` 词表里塞中文翻译。不改 `app.asar`、
  不改 `Claude.exe`、不改任何可执行文件，因此同样不影响签名和 Cowork。
- 上游若日后更新了词表，本补充包是**键级合并**，不会覆盖掉上游更好的译文，
  只会补上它还缺的键。
- **占位符校验发生在 `resume.py merge` 阶段，不在 `apply.py`。** apply.py 是直接
  `dict.update` 合并，不做校验——所以别绕过 merge 直接把译文塞进 `supplement\*.json`。
- Windows 中文控制台需要 `PYTHONUTF8=1`，已在全局 `settings.json` 的 `env` 里设好。
