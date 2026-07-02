---
name: meihua-yishu-entry
description: Use when the user wants a Meihua Yishu reading, a step-by-step derivation, or a visualized hexagram workflow from a question and digits.
metadata:
  short-description: 梅花易数总入口
---

# 梅花易数总入口

当用户要你“按梅花易数起卦、推演、看结果、画过程图”时，先用这个 Skill。

## 目标

把请求拆成六件事：

1. 收集输入
2. 算本卦
3. 算变卦
4. 做解析
5. 先生成正确底稿
6. 如有明确需要，再生成美化图

## 输入要求

当前版本优先接受：

- 一个明确的问题
- 两位数字，例如 `78`
  或两个单独数字，例如 `7 8`

如果用户只给了模糊问题，先帮助他把问题收束成一个具体判断题。
如果用户没有给足两位数字，就请他补齐。

## 引导优先级

如果用户还没有把问题和数字说清楚，优先先走：

- `meihua-guided-intake`

## 执行顺序

1. 先读取：
   - `../../docs/manual.md`
   - `../../docs/methodology-reference.md`
   - `../../docs/intake-playbook.md`
2. 运行：

```bash
python3 ../../scripts/meihua_calc.py \
  --question "<用户的问题>" \
  --packed 78 \
  --out-dir <输出目录>
```

或：

```bash
python3 ../../scripts/meihua_calc.py \
  --question "<用户的问题>" \
  --digits 7 8 \
  --out-dir <输出目录>
```

3. 第二步按 `meihua-primary-hexagram` 的规则理解本卦
4. 第三步按 `meihua-changed-hexagram` 的规则理解变卦
5. 第四步按 `meihua-interpretation` 的规则完成体用与五行解析
6. 先调用 `meihua-diagram-qa`，确保确定性结果校验通过
7. 再调用 `meihua-deterministic-card`，先产出一张 `deterministic_teaching_card.png`
8. 只有用户明确要“更好看/美化版”时，才调用 `meihua-imma-teaching-png` 或 `meihua-image2-card`
9. 美化层只能复刻底稿，不能改事实
10. 若美化层出现错字、错卦、错动爻，则明确以正确底稿为准

## 输出要求

默认输出顺序：

1. 结论
2. 本卦、变卦、动爻
3. 体用与五行关系
4. 一份确定性正确底稿 PNG
5. 只有用户明确要求美化时，再给一份美化教学 PNG
6. 若用户要沉淀，则顺手保存案例素材或方法论记录

## 重要原则

- 核心计算必须以 `../../scripts/meihua_calc.py` 的结果为准。
- 不要把 AI 生成图片当成计算依据。
- 图像层只负责“展示”，不负责“决定卦象”。
- 默认保留两层产物：`后台 SVG 校准稿` + `确定性正确底稿 PNG`。
- 第二步固定交给 `meihua-primary-hexagram`。
- 第三步固定交给 `meihua-changed-hexagram`。
- 第四步固定交给 `meihua-interpretation`。
- 第五步先固定交给 `meihua-diagram-qa`。
- 第六步固定交给 `meihua-deterministic-card`。
- 第七步如有明确需要，再交给 `meihua-imma-teaching-png` 或 `meihua-image2-card`。
- 前台美化图必须建立在正确底稿之上。
- image2 教学卡必须体现 `八卦数字对应`、`八卦五行对应`、`五行生克`、`体用关系`。
- 第二步里要尽量把 `先天八卦数字对应` 和 `八卦五行对应` 前置表现出来，方便用户边看边学。
- 先读取 `../../docs/image2-teaching-card-spec.md`，再写 image2 Prompt。
- 默认直接走 `教学推演`，默认主结果就是正确底稿 PNG。
- 不要把 SVG 当作默认主展示结果返回给用户。
