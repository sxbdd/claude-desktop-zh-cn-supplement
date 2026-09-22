<div align="center">

# Claude Desktop 完整中文化补丁

**把 Claude Desktop 的界面变成 100% 简体中文**

上游汉化包漏掉的 **17,748 条**界面词条，这里全补齐了。

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4.svg)]()
[![Claude Desktop](https://img.shields.io/badge/Claude%20Desktop-2.2553.1.0-8A63D2.svg)]()

**[⬇️ 下载最新版](../../releases/latest)** · [快速开始](#-快速开始) · [常见问题](#-常见问题) · [它是怎么工作的](#-它是怎么工作的)

</div>

---

## 🤔 为什么需要它

装了 [claude-desktop-zh-cn](https://github.com/javaht/claude-desktop-zh-cn) 之后，界面确实变中文了，
但**到处还残留着英文**——「设置」是中文，「Keyboard Shortcuts」「Update now」却是英文。

这不是安装失败，是那个项目的**中文词表本身没收全**：

| 词表 | 英文词条 | 上游自带中文 | 缺口 |
|---|---:|---:|---:|
| 菜单栏 / 对话框 | 705 | 362 | 343 条 |
| 网页前端界面 | 29,442 | 12,037 | 17,405 条 |

Claude 查不到中文键就回落到英文原文，于是这些缺口就明晃晃地留在界面上。

**本补丁把这 17,748 条全部补齐：29,442 个英文键 100% 有中文，缺键 0 条。**

只有品牌名、产品名、技术标识符按惯例保留原文——`Google Play`、`GitHub App`、
`Claude Pro`、`Anthropic Sans`、OAuth scope 串、PEM 证书示例之类，这些本来就该是英文。

---

## 🚀 快速开始

### 1. 下载

去 [Releases](../../releases/latest) 下载 `Claude-Desktop-zh-CN-Patch.zip`（约 1.9 MB）。

> **上游汉化包已经打包在里面了**，全程不需要联网，不需要自己再去下载别的东西。

### 2. 解压

解压到**本地硬盘**任意位置（别在网络盘里，也别在压缩包里直接双击）。

### 3. 双击两个脚本

| 顺序 | 文件 | 说明 |
|---|---|---|
| ① | `第1步-安装上游汉化.bat` | 装上游汉化包，**模式选「1」** |
| ② | `第2步-安装补充汉化.bat` | 装本补丁，自动提权 |

**等第 1 步的窗口彻底跑完**再执行第 2 步。

第 2 步结束会打印覆盖率报告，看到「**缺键 0 条**」就成了：

```
本次写入 21630 条。复核覆盖率：
    菜单栏 / 对话框：中文 784 条 / 英文 705 条，缺键 0 条
    网页前端界面：中文 31549 条 / 英文 29442 条，缺键 0 条
```

### 4. 重启 Claude Desktop

**从托盘图标右键退出**，再重新打开。只关窗口不够。

> 前置条件：Windows 10/11 + 已装 [Python 3](https://www.python.org/downloads/)
> （安装时记得勾 **Add python.exe to PATH**）。

---

## ❓ 常见问题

<details>
<summary><b>装完界面还是全英文？</b></summary>

第 1 步没装成功。本补丁只负责补词表，**不负责把界面语言切换成中文**——
那是上游汉化包干的活（它要改 Claude 的前端语言白名单和语言设置）。
回到第 1 步重跑，注意选「模式 1」。

</details>

<details>
<summary><b>大部分是中文，但还有零星英文？</b></summary>

看第 2 步结尾报告里的「缺键」数。不是 0 的话，说明你的 Claude 版本比词表新，
有若干新词条还没翻译，界面只在这几处残留英文。把报告发到 [Issues](../../issues) 就能补上。

另外确认重启时是「从托盘完全退出」，而不是只关窗口。

</details>

<details>
<summary><b>找不到 Python / 提示没有权限？</b></summary>

装一个 Python 3 并勾上 Add to PATH。权限问题就右键那个 .bat →
「以管理员身份运行」；同时确认 Claude Desktop 已从托盘完全退出，
否则程序文件被占用也写不进去。

</details>

<details>
<summary><b>Claude Desktop 更新后中文没了？</b></summary>

正常的，更新会覆盖程序文件。按 **第 1 步 → 第 2 步** 重跑一遍，两分钟的事。
建议每次更新后顺手跑一次。

</details>

<details>
<summary><b>Cowork / 沙箱功能坏了？</b></summary>

第 1 步选错模式了（选了完整模式）。用上游安装程序卸载后重装，这次选「模式 1」。

</details>

<details>
<summary><b>怎么卸载？</b></summary>

- 只撤销本补丁：双击 `卸载还原.bat`
- 完全卸载：先跑 `卸载还原.bat`，再运行 `upstream\install-windows.bat` 选卸载

</details>

---

## 🔧 它是怎么工作的

Claude Desktop 用 i18next 管理界面文案，词表是按语言分的扁平 JSON 文件。
某个键在当前语言里找不到，就回落到 `en-US`——**这就是英文残留的全部原因**。

所以本补丁做的事非常朴素：**往 `zh-CN.json` 里补键值对**。

```
app/resources/
├── zh-CN.json                          ← 菜单栏、对话框
└── ion-dist/i18n/
    ├── zh-CN.json                      ← 网页前端界面
    └── dynamic/zh-CN.json              ← 模型选择器（上游没有这个文件，本补丁补上）
```

它**不碰** `app.asar`、不碰 `Claude.exe`、不改任何可执行文件，
因此**不影响代码签名，也不影响 Cowork 和沙箱**。

写入是**键级合并**且幂等的，可以反复运行；首次改动前会把原文件备份成 `*.bak-supplement`。

### 翻译的过程

补充词表里的每一条都过了 ICU MessageFormat 校验：

- `{count, plural, one {…} other {…}}`、`{x, select, …}` 的骨架原样保留
- `{orgName}`、`<link>`、`<bold>` 这类占位符和标签**逐字符**保留、大小写一致
- 中文的 `one`/`other` 分支写相同文字

校验由 `resume.py merge` 执行，对不上的整块跳过——这正是它拦下了几十处
哈希键誊写错误和占位符位置错误的地方。

---

## 📦 目录结构

```
supplement/                   补充词表（21,630 条）
  desktop-add.json              菜单栏 / 对话框
  frontend-add.json             网页前端界面
  dynamic-zh-CN.json            模型选择器 / 思考模式
apply.py                      安装脚本（--check 只看覆盖率，--uninstall 还原）
build_release.py              重新打包成发布 zip
resume.py                     续做工具（切块 / 校验 / 收回）
release/
  Claude-Desktop-中文化补丁/     可直接分发的成品（含上游 1.4.7 原件）
应用补充汉化.bat                本机快捷方式
DEVELOPMENT.md                开发笔记：翻译流水线、踩过的坑
```

---

## 🧩 版本兼容性

本补丁按 **Claude Desktop 2.2553.1.0** 制作。查自己的版本：设置 → 关于，
或看安装目录名（形如 `Claude_2.2553.1.0_x64__pzs8sxrjxfjjc`）。

词表是按键合并的，所以版本对不上**不会把界面弄坏**：

| 你的版本 | 结果 |
|---|---|
| 与 2.2553.1.0 相同 | 完整中文，报告显示「缺键 0 条」 |
| 更新 | 新增词条没翻译，这几处显示英文，报告会给出「缺键 N 条」 |
| 更旧 | 正常，多余的键用不上，不报错也不空白 |

缺翻译只会回落成英文，不会让界面报错或空白，所以放心装。

> ⚠️ **上游汉化包本身挑版本。** 本补丁是纯词表合并，几乎不挑；但第 1 步的上游包要改
> Claude 的前端语言白名单等内部文件，跟版本强相关。如果你的 Claude 明显比上游 1.4.7
> 适配的版本新，**第 1 步可能直接失败**。这种情况下去上游项目看有没有更新版本，
> 有就用它的新版走第 1 步，本补丁照跑不误。

---

## 🙏 致谢

- 上游汉化包：[javaht/claude-desktop-zh-cn](https://github.com/javaht/claude-desktop-zh-cn)（MIT）
  ——没有它把中文语言选项接进 Claude，本补丁无从谈起
- 界面资源版权归 Anthropic 所有

## ⚖️ 免责声明

本项目是**非官方**汉化，与 Anthropic 无任何关联。它只修改界面显示用的语言资源文件，
不修改任何可执行文件，不改变请求内容、模型路由或账号数据。仅供学习交流使用，
请自行评估风险。

本项目以 [MIT 许可证](LICENSE) 开源。
