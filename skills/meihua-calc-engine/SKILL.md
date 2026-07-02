---
name: meihua-calc-engine
description: Deterministically calculate the upper trigram, lower trigram, primary hexagram, moving line, changed hexagram, body/use relation, and entry-level verdict for Meihua Yishu.
metadata:
  short-description: 梅花易数计算引擎
---

# 梅花易数计算引擎

这个 Skill 负责“算”，不负责花哨表达。

## 规则来源

读取：

- `../../docs/manual.md`
- `../../docs/methodology-reference.md`

并严格以 `../../scripts/meihua_calc.py` 输出为准。

## 计算内容

- 上卦
- 下卦
- 本卦
- 动爻
- 变卦
- 体
- 用
- 五行关系
- 入门级判断

## 分工建议

如果需要把计算流程拆细：

- `本卦` 可由本 Skill 负责总算
- `变卦` 优先交给 `meihua-changed-hexagram`

也就是第三步应单独强调：

- 先把两个数字相加
- 再除以 6
- 余数就是动爻

## 执行命令

```bash
python3 ../../scripts/meihua_calc.py \
  --question "<用户问题>" \
  --packed 78 \
  --out-dir <输出目录>
```

## 结果读取

读取 `<输出目录>/result.json`，优先使用其中字段：

- `primary`
- `changed`
- `moving_line`
- `body`
- `use`
- `relation`
- `verdict`

## 表达规范

- 先报结论，再报依据。
- 说清“这是入门规则版本”，不要冒充更复杂流派。
- 如果是在第二步解释本卦计算，要顺手把 `先天八卦数字对应` 和 `八卦五行对应` 一起讲明白。
- 如果用户追问更深层断法，可以继续分析，但要明确哪些是规则内、哪些是延伸判断。
