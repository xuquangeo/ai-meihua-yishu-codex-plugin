---
name: meihua-deterministic-card
description: Generate the correct deterministic Meihua Yishu teaching PNG from result.json and qa_report.json before any beautification step.
metadata:
  short-description: 梅花易数正确底稿 PNG
---

# 梅花易数正确底稿 PNG

这个 Skill 只负责第一步：

- 先产出一张事实绝对正确的教学图 PNG

它不负责美化风格。
它的目标是先把：

- 卦线
- 动爻
- 本卦
- 变卦
- 五行
- 体用

全部锁死成一张“正确底稿”。

## 必读顺序

先确保已经有：

- `result.json`
- `qa_report.json`

如果 `qa_report.json` 不是 `通过`，不要继续出图。

## 固定命令

```bash
python3 ../../scripts/render_deterministic_teaching_card.py --out-dir <结果目录>
```

默认输出：

- `deterministic_teaching_card.png`

## 硬规则

- 这张图里的卦线必须由脚本直接画，不允许模型脑补
- 三爻卦必须是 `3` 条线
- 六爻卦必须是 `6` 条线
- 第四爻动必须严格按 `qa_report.json` 里的位置高亮
- 本卦上半和下半必须严格复用已算出的上卦/下卦

## 在总流程中的位置

推荐排在：

1. `meihua-guided-intake`
2. `meihua-primary-hexagram`
3. `meihua-changed-hexagram`
4. `meihua-interpretation`
5. `meihua-diagram-qa`
6. `meihua-deterministic-card`

这一步完成后，才允许进入美化层。
