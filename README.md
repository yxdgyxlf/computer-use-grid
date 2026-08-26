# computer-use-grid

解决 AI 桌面操作（computer_use）**高 DPI 下坐标漂移**的工程方案：**截图网格叠层 + 实测坐标校准 + 坐标台账**。

> 核心主张：Windows 高缩放（125%/150%/175%/200%）下，截图、UIA、点击 API 各用一套坐标系且不告诉你用哪套——**任何理论换算都会错；实测校准才是自愈的**。

## 特性

- 🎯 **网格叠层**：`overlay-grid.py` 给任意 computer_use 截图叠上透明网格（红主格 100px / 白细格 25px + 刻度数字），vision 模型读格子即可得到「截图像素坐标」——与 `coordinate` 输入同坐标系，零换算。
- 🧭 **坐标台账**：`coords.json` 按应用记录**实测命中**的按钮坐标（落点 + 截图验证才入库，禁用推算值），同一窗口尺寸下一次校准、此后直接点。
- 🔁 **Fallback 兜底**：台账未登记/窗口尺寸变化 → 网格法重新定位，校准后回写台账。
- 🧠 **AX/DOM 优先**：判断页面内容（有没有视频/列表/筛选）先 grep 无障碍树，vision 只做兜底（Canvas、无 AX 界面）。

## 安装

```bash
git clone https://github.com/<your-name>/computer-use-grid.git
python3 -m pip install pillow        # 依赖（脚本唯一外部库）
```

## 用法（三步）

```bash
# 1. 截图（任意 computer_use 客户端，如 cua-driver / Hermes computer_use）
computer_use capture mode='vision'   # 得到 截图.png

# 2. 叠网格
python3 scripts/overlay-grid.py 截图.png --out 截图_grid.png

# 3. vision 模型读格 -> 得到目标中心 (x, y) -> 点它
computer_use click coordinate=[x, y] capture_after=true
```

### 台账模式（推荐，第二次起免截图）

```json
{
  "base_size": [1456, 869],
  "coords": {
    "menu_button":     [1191, 25],
    "search_box":      [691, 134],
    "input_field":     [711, 318]
  }
}
```

查台账 → 直接 `click coordinate=[x,y]` → 命中。窗口尺寸变了一次 → 重做一次 Fallback 校准 → 回写台账。

## 校准原理（为什么能收敛）

1. 网格读数与真实落点存在**固定系统偏差**（由 DPI + 驱动视口系数叠加产生，不同窗口不同）。
2. 第一次点按后，用 `capture_after` 截图判定「落点 vs 目标」的偏差 delta。
3. 坐标修正后重试——**通常一次即命中**。
4. 把修正后的实测坐标（而非读数）记入台账——误差从此归零，这就是"换算必错、实测自愈"。

## 项目结构

```
computer-use-grid/
├── README.md               # 本文档
├── SKILL.md                # 技能/方法论手册（可直接作为 Agent skill 加载）
├── scripts/
│   └── overlay-grid.py     # 网格叠层脚本（Pillow，单文件）
├── examples/
│   └── coords.sample.json  # 坐标台账示例（策略与结构）
└── references/
    └── cua-driver-official-skill.md  # 官方 cua-driver 最佳实践存档（对照阅读）
```

## 已知边界

- 主要针对 Windows + 高 DPI（实测 2560×1600 @150%）；其他平台/缩放比例应可复用（流程与坐标系无关），未经全套验证。
- 元素索引路径（element_token）在本方案是"可用则用"，像素路径是主力——方向与官方手册相反，但经实测在 AX 缺失/失效场景更稳。
- 多显示器/DPI 变更后，旧台账失效，需要重校准一次。

## License

MIT © 2026 yxdgyxlf — 详情见 [LICENSE](LICENSE)。
