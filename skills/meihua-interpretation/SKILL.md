---
name: meihua-interpretation
description: Turn the deterministic Meihua Yishu calculation result into a concise, structured interpretation with body/use and five-element reasoning.
metadata:
  short-description: 梅花易数解读
---

# 梅花易数解读

这个 Skill 单独负责第四步：

- 做解析

它负责把已经确定的本卦、变卦、体用、五行关系解释清楚。

## 输入

读取 `../../scripts/meihua_calc.py` 生成的 `result.json`。

并参考：

- `../../docs/manual.md`
- `../../docs/methodology-reference.md`

## 解读顺序

1. 先说结论
2. 再说本卦说明了什么起势
3. 再说动爻说明了哪里变化
4. 再说变卦说明了什么结果走向
5. 再说体用与五行关系
6. 最后说建议

## 规则写死

### 体用判定

- `不变为体，变化为用`
- 动爻在 `1-3` 爻：下卦在变，所以上卦为体、下卦为用
- 动爻在 `4-6` 爻：上卦在变，所以下卦为体、上卦为用

### 解析要点

- 先确认体和用分别是谁
- 再确认体和用的五行
- 再看五行关系
- 最后再给结论

## 话术要求

- 不要空泛神叨。
- 语言尽量像“辅助决策报告”，不是故弄玄虚。
- 明确区分：
  - `脚本已算出的确定部分`
  - `基于规则做的解释部分`

## 风险提示

- 当前版本属于入门规则版，不等于完整术数体系。
- 如果用户把结果用于高风险现实决策，要提醒其只作辅助参考。
- 若用户的问题本身含糊，先指出“问题越具体，结果越可用”。
