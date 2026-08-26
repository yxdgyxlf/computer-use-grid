---
name: computer-use-grid
description: computer_use点按漂移/陌生应用定位：截图叠坐标网格，vision读格子坐标再点按。
version: 1.1.0
author: yxdgyxlf
license: MIT
---

# computer-use-grid — 网格坐标定位法

让 computer_use（桌面控制）在 **窗口截图 → 像素坐标** 路径上稳定命中目标的实战工程方案。

## 什么时候用
- 需要**精确点按** computer_use 目标（按钮/输入框/会话行），尤其：
  - 陌生应用（WebView2 / Electron / Chromium 窗口，AX 树细粒度缺失）
  - 屏幕缩放 ≠ 100%（例如 2560×1600 @150%，逻辑分辨率 1707×1067 —— 坐标系统换算极易漂移）
  - 多次点偏、直接用 vision 估坐标不可靠时（裸估偏差可达 50-80px，会点到隔壁按钮）

## 资产坐标台账（永久基准模式）
- 台账：`<HERMES_HOME>/scripts/grids/coords.json` — 按应用分组；**坐标 = 截图像素**（即 computer_use 的 `coordinate` 输入），**只收实测命中值**（落点 + 截图验证），**禁用推算值**（换算必错，实测自愈）。
- 基准网格图：`<HERMES_HOME>/scripts/grids/<app>_base_grid.png` — 每应用一张（绑定其 base_size），由 `overlay-grid.py` 生成。
- 示例结构见 `examples/coords.sample.json`。

## 主流程（先）：查台账
1. 确认目标窗口**尺寸未变**——与台账 `base_size` 一致（建议操作前先把窗口最大化/恢复到台账时的尺寸；不一致 → 走 Fallback 并**更新台账**）。
2. `coords.json` 查该应用 + 键 → 得 [x, y] → 直接 `computer_use click/double_click coordinate=[x,y]`，capture_after 验证。
3. 命中即结束；未命中（罕见）→ Fallback 重新定位，并把新坐标修正回台账。

## Fallback 流程：动态网格定位（台账未登记/失配时）
1. **capture**：`computer_use capture mode='vision'`（含 `app=<窗口>`），记下截图路径（width/height 即视口）。**不要移动/缩放窗口、不要滚动**（网格是快照）。
2. **叠网格**：`python3 scripts/overlay-grid.py <截图> --out <输出>`（输出与截图同尺寸；红主格 100px + 白细格 25px + 边缘数字刻度）。
3. **读坐标**：`vision_analyze(网格图)`，固定提示词句式：
   > 图上有坐标网格：红色粗线每100px一格（顶部/左侧标数字刻度），白细线每25px。请读出「目标UI」中心的网格坐标（x,y），精确到刻度，并同时读出相邻对照元素坐标。
   **读数 = 截图像素坐标 = 传给 computer_use 的 coordinate（同一坐标系）**，不要再乘缩放。
4. **点按**：`computer_use click/double_click coordinate=[x,y] capture_after=true`。若 AX 树里已有该元素（som 捕获），优先用元素 bounds。
5. **校准**：看 capture_after —— 命中 → 继续；未命中 → 读出偏差 delta（落点 vs 实际命中的元素），修正坐标重试一次。**通常第一次校准后即命中**，别盲点第三次。

## 页面结构判断与兜底校验：AX/DOM 优先
**教训**：搜索页找"视频"一度卡在截图上判断"有没有视频卡片"——而页面的 AX 树里"视频"选项卡/链接一直都在（grep label 即得）。判断页面内容：
- **规则 1**：判断"页面上有没有 X"→ 先读 AX 树（elements json）grep label（视频/图片/筛选/直播…）；树里有 → 直接点（用其 bounds）；树里无 → 才允许 vision 看图。
- **规则 2**：领域预判——教程/菜谱/怎么做 类查询，默认"视频在分类 tab 里"；首屏无视频卡片是**正常形态**，主动点「视频」tab。
- **规则 3**：自动备选链——目标缺失 → 自动试"分类 tab 找目标" → 仍无 → 才报告用户。**不中途停等**。
- **规则 4**：打开成功断言——地址栏/Document 标题变化即算打开（页面"正在加载"中也可确认），不必等渲染完。
- 读格法（vision）降级为 rescue：仅 Canvas 渲染 / 无 AX 的界面使用。

## 关键坑位
- **coordinate 单位 = 截图像素**，与网格图同层；AX 元素 bounds 是 native 坐标（×缩放系数），两者勿混用换算——一切以网格读数为准。
- **高 DPI 环境**：逻辑分辨率与物理像素不一致、UIA/screenshot/点击 API 各用一套坐标系且无提示——理论上任何手算都会错，所以本方案坚持"实测校准 + 记录"。
- **background 文字/键盘输入被拒**：Chromium 类窗口（`Chrome_WidgetWin_1` 等）的 `type`/`key_combo` 后台不投递（报 background_unavailable）→ 升级 `delivery_mode='foreground'`（窗口短暂前置，需批准）。`click` 一般后台可用。
- **桌面应用启动失败**：命令行 `start` 启动的 exe 若工作目录不对会拉起失败（部分启动器需要 cwd=exe 目录）→ 用桌面双击（explorer 双击会设对工作目录）。
- 点错按钮开了菜单/面板 → 先复位（Esc 或点关闭）再继续，别在错误状态上继续点。
- 网格刻度数字会轻微遮挡边缘 UI（可接受）；深浅色界面均可（红主格足够区分）。

## 已验证案例（示例：IM/短视频客户端私信流程）
路径：桌面双击应用图标 → 消息入口(≈1180,50) → 会话列表点目标(≈1193,280+校准) → 输入框点位 → 文本先写 UTF-8 文件 → PowerShell Set-Clipboard → (foreground) Ctrl+V 或直接 foreground type → Enter 发送。
- 网格读数与 driver 落点存在固定映射偏差（示例环境实测 x 准、y≈+38px），一次 capture_after 校准即可收敛；每个窗口/尺寸首次操作校准一次，之后同窗口坐标可靠。

### 进阶：动态列表 → 搜索定位
会话/列表会随内容实时重排，网格坐标时效性差、点击易扑空。**稳定解法**：面板内搜索框 → 输入完整目标名（foreground type）→ 结果列表出现目标 + 动作按钮 → 直接点按钮。搜索模式下 AX 树常给出真实 bounds（不在 0,0），grep 树里 label 匹配目标名取 bounds —— 比视觉读格更快。

## 与官方 cua-driver 手册的对照
- 官方默认 **element_token 语义寻址**（绕过坐标数学）；像素路径仅用于 canvas/视频/树失效场景 —— 本方案 = 官方像素路径 + **实测校准层**（更稳：换算必错、实测自愈）。
- 官方"树会撒谎"（suspected_noop/degraded）→ 转像素；本方案 AX bounds 失效(0,0) → 转网格/台账 —— 同一决策同构。
- 官方元素索引**跨快照失效**（No cached AX state）→ 反证"台账存实测像素坐标"优于存元素索引/快照依赖。
- 参考阅读：trycua/cua 仓库 `libs/cua-driver/rust/Skills/cua-driver/SKILL.md`（`references/` 内有存档）。
