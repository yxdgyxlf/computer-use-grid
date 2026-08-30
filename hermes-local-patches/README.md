# Hermes Local Patches — capture 提速补丁存档

本目录存档 **Hermes Agent 0.20.6 本机提速补丁**（2026-08-31 实测），针对 cua-driver 后端的 `computer_use capture` 慢（som 22-64s / vision 11-27s）问题。

## 补丁清单

| 文件 | 说明 | 实测效果 |
|---|---|---|
| `hermes-capture-speedup-20260831.patch` | 两个文件的完整 diff（git apply 一键恢复） | get_window_state：22-64s → **0.9s** |

补丁内容：

1. **`tools/computer_use/cua_backend.py`**（B 方案，+16 行）
   4 处 `get_window_state` 调用追加 `max_elements`/`max_depth` 参数（模块级常量 `_CU_TREE_*=1200/15`、`_CU_VISION_*=400/12`）。cua-driver 0.22.0 官方参数（`cua-driver describe get_window_state` 核实），只加速不改变行为。
2. **`tools/vision_tools.py`**（+10 行）
   支持从 `auxiliary.vision.max_tokens` 读取输出上限注入调用链（对豆包等普通 chat_completions 提供方被 `_build_call_kwargs` 丢弃、仅对 anthropic/nvidia/gemini/moa 生效；豆包侧的真正上限走 `extra_body.max_tokens`，见下）。

## 应用方式

```bash
# 在 Hermes 代码目录（C:\Users\xiany\AppData\Local\hermes\hermes-agent\）
git apply D:/GitHub/computer-use-grid/hermes-local-patches/hermes-capture-speedup-20260831.patch
# 重启后端（桌面端/gateway）后生效

# 回滚
git apply -R D:/GitHub/computer-use-grid/hermes-local-patches/hermes-capture-speedup-20260831.patch
```

升级 Hermes 后被重置时重新 `git apply` 即可；或直接 `git cherry-pick` 对应 commit。

## 配套配置（视觉描述档提速，不在 patch 内，需手动配置）

将视觉分析从 GLM-5.3-Flash（43-49s）切换到火山方舟 Doubao-Seed-Evolving（关思考 3.9s）：

```bash
# .env（密钥）
ARK_API_KEY=<你的火山方舟密钥>

# config.yaml（hermes config set 逐键写入，或直接编辑 auxiliary 段）
auxiliary:
  vision:
    provider: custom
    model: doubao-seed-evolving
    base_url: https://ark.cn-beijing.volces.com/api/v3
    key_env: ARK_API_KEY
    extra_body:
      thinking:
        type: disabled      # 关思考：3.9s vs 23s，关键
      max_tokens: 300       # 输出上限：必须放 extra_body 里才生效
```

注意事项（实测确认）：

- **火山方舟新账户须在控制台「开通管理」逐模型开通**才能调用；`GET /api/v3/models` 列出 ≠ 可调用。
- **豆包思考档（Evolving/2.1 全系）默认开思考**，不注入 `thinking:disabled` 则截图描述 20-25s。
- **max_tokens 放 `extra_body` 而非顶层**：`auxiliary.vision.max_tokens` 顶层键会被 Hermes `_build_call_kwargs` 有意丢弃（防 GPT-5 400 策略），只有 `extra_body` 原样透传到请求体。
- config 改动热生效，无需重启；代码改动（patch）需重启后端。

## 实测数据（2026-08-31，Hermes 0.20.6 + cua-driver 0.22.0）

| 环节 | 改前 | 改后 |
|---|---|---|
| get_window_state（som 全树） | 22-64s | 0.9s |
| 视觉描述（GLM-5.3-Flash） | 43-49s | Evolving 关思考 3.9s（短答）/ 13.7s（600 tokens 长答） |
| capture 端到端 | 22-64s | ~1s 截图建树 + 6-13s 分析 |
