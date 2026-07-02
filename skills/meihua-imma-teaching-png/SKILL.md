---
name: meihua-imma-teaching-png
description: Beautify an already-correct deterministic Meihua Yishu teaching PNG into a more polished Imma/image2 teaching card without changing any facts.
metadata:
  short-description: 梅花易数美化教学 PNG
---

# 梅花易数美化教学 PNG

这个 Skill 只负责第二步：

- 把已经正确的 `deterministic_teaching_card.png` 美化成更有质感的教学图 PNG

默认不要主动调用本 Skill。
只有用户明确要：

- 更好看
- 美化版
- 海报版
- 更精致的 PNG

时，才启用它。

它不负责：

- 重新算卦
- 重新决定动爻
- 重新决定卦线

## 事实来源

只能读取这些事实：

- `deterministic_teaching_card.png`
- `result.json`
- `qa_report.json`

其中优先级最高的是：

1. `deterministic_teaching_card.png`
2. `qa_report.json`
3. `result.json`

## 核心原则

这一步不是“重新画内容”。
这一步是“在不改内容的前提下做美化”。

所以要把它理解成：

- 保留同样的四步结构
- 保留同样的卦线数量
- 保留同样的高亮位置
- 保留同样的文字事实
- 只提升排版、材质、层次、细节

## 禁止事项

- 不允许把三爻画成两条
- 不允许把六爻画少
- 不允许改动高亮爻位置
- 不允许改动本卦、变卦名称
- 不允许改动五行对应

## 与画图 Skill 的关系

以后前台如果要用 `Imma / image2`：

- 必须在 `meihua-deterministic-card` 之后
- 必须把 `deterministic_teaching_card.png` 当作唯一正确底稿
- 只能做“美化版复刻”，不能做“自由生成”
