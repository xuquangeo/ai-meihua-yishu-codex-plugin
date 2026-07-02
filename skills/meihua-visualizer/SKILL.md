---
name: meihua-visualizer
description: Visualize the Meihua Yishu derivation process with deterministic SVG hexagram diagrams and optional imagegen-enhanced explanation images.
metadata:
  short-description: 梅花易数过程可视化
---

# 梅花易数过程可视化

这个 Skill 负责后台的确定性可视化校准，不负责前台最终展示。

## 默认可视化层

优先使用 `../../scripts/meihua_calc.py` 生成的 SVG 文件：

- `upper_trigram.svg`
- `lower_trigram.svg`
- `primary_hexagram.svg`
- `changed_hexagram.svg`
- `process_overview.svg`
- `step_by_step_report.svg`

这些图是确定性图，不会把卦画错。
但它们只作为后台校准底稿，不应作为用户最终主结果。

## 默认双输出

以后默认保留两份版本：

1. `后台 SVG 校准图`
2. `前台 image2 / image_gen 教学卡图`

其中：

- SVG 负责校准和核对
- image2 PNG 负责前台展示
- 两者都要保留，但前台只出 PNG

在把 PNG 交付出去之前，必须先跑：

```bash
python3 ../../scripts/meihua_check.py --out-dir <结果目录>
```

如果 `qa_report.json` 显示 `不通过`，就不能把这次图当作合格结果。

## 展示顺序

推荐按这个顺序展示：

1. 上卦
2. 下卦
3. 本卦
4. 动爻位置
5. 变卦
6. 体用五行关系

## 使用 `$imagegen` 的场景

默认就应使用专门的 `meihua-image2-card` Skill 生成一份教学卡图，除非用户明确说不要。

## 硬规则

- 不要把本 Skill 生成的 SVG 直接当作最终展示结果返回给用户
- 本 Skill 的图只用于：
  - 事实校准
  - Prompt 参考
  - image2 出图前的底稿核对

## `$imagegen` 使用原则

- 先读取 `../../docs/image2-teaching-card-spec.md`
- 只把 `result.json` 和已生成 SVG 当作视觉说明依据。
- 不要让 `$imagegen` 自己决定卦象。
- Prompt 中明确写：
  - 本卦是什么
  - 变卦是什么
  - 动爻是哪一爻
  - 体用关系是什么
  - 八卦与五行如何对应
  - 五行生克关系要画出来
  - 这是一张讲解图，不是重新起卦

## 第四步固定元素

第四步“做解析”里，必须尽量明确画出：

- 乾：金
- 兑：金
- 离：火
- 震：木
- 巽：木
- 坎：水
- 艮：土
- 坤：土

并且要把：

- 体是什么
- 用是什么
- 体用五行关系是什么
- 最终吉凶判断是什么

都明确体现在图中。

## 第二步前置教学要求

第二步“做计算，算本卦”里，也要尽量明确画出：

- `1-8` 对应哪一个八卦
- 每一个八卦对应什么五行

目标是让用户在“算本卦”阶段就一眼看懂：

- 这个数字为什么对应这个卦
- 这个卦为什么又对应这个五行

## 推荐 Prompt 方向

```text
Use case: infographic-diagram
Asset type: Meihua Yishu explanation card
Primary request: Create a clean teaching diagram for a Meihua Yishu derivation.
Subject: show upper trigram, lower trigram, primary hexagram, moving line, and changed hexagram exactly as provided.
Style/medium: elegant Chinese divination teaching card
Constraints: do not alter the hexagram lines, do not invent extra symbols, use the provided diagrams as the authoritative reference, explicitly show the number-to-bagua mapping and bagua-to-five-elements mapping in step 2, and the five-elements relation used in the final analysis
Avoid: wrong line order, mirrored hexagrams, decorative clutter, unreadable labels
```
