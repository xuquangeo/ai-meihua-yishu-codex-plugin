---
name: meihua-diagram-qa
description: Check whether the final Meihua Yishu teaching card is correct by verifying hexagram names, trigram shapes, moving line, body/use, five-element mappings, and the five-element relation diagram.
metadata:
  short-description: 梅花易数教学图校验
---

# 梅花易数教学图校验

这个 Skill 单独负责最终教学图的验收。

它不是出图 Skill。
它负责判断：

- 这张图能不能交付
- 哪些对应关系画错了

## 必读参考

先读取：

- `../../docs/diagram-qa-checklist.md`
- `../../docs/trigram-visual-reference.md`
- `../../docs/image2-teaching-card-spec.md`

## 校验对象

优先校验：

- 最终 `image2_teaching_card.png`

但在检查最终 PNG 之前，必须先跑一遍确定性校验脚本：

```bash
python3 ../../scripts/meihua_check.py --out-dir <结果目录>
```

它会输出并落盘：

- `qa_report.json`

同时对照：

- `result.json`
- `upper_trigram.svg`
- `lower_trigram.svg`
- `primary_hexagram.svg`
- `changed_hexagram.svg`
- `step_by_step_report.svg`

其中本卦组合优先对照：

- `result.json -> primary -> assembly_lock`

## 校验重点

必须重点检查：

1. 卦名对不对
2. 上卦图形对不对
3. 下卦图形对不对
4. 本卦组合对不对
5. 动爻位置对不对
6. 动爻阴阳变化方向对不对
7. 变卦图形和名字对不对
8. 八卦图形对照表对不对
9. 八卦五行对应对不对
10. 五行生克图是不是完整五节点
11. 三爻卦有没有被错误画成两条线
12. 六爻卦有没有少线或并线
13. 第四爻这种动爻是否按“自下而上”计数
14. 动前阴阳、动后阴阳有没有跟变卦一致

其中本卦组合必须额外检查：

- 本卦上半是否等于已经算出的上卦
- 本卦下半是否等于已经算出的下卦
- 本卦是否确实按 `assembly_lock` 原样拼接，而不是重新画了一个相似图
- 上卦是否明确为 3 条线
- 下卦是否明确为 3 条线
- 本卦是否明确为 6 条线

## 一票否决

只要发现以下任意错误，就判定整张图 `不通过`：

- 卦名错
- 卦形错
- 动爻错
- 体用错
- 五行对应错
- 五行图缺元素

## 输出格式

如果通过：

```text
校验结果：通过
```

如果不通过：

```text
校验结果：不通过
问题：
1. ...
2. ...
应改为：
1. ...
2. ...
```

## 与总流程的关系

推荐位置：

1. `meihua-guided-intake`
2. `meihua-primary-hexagram`
3. `meihua-changed-hexagram`
4. `meihua-interpretation`
5. `meihua-image2-card`
6. `meihua-diagram-qa`

也就是说，图画完以后，必须再过一遍本 Skill，才算完整流程。

## 脚本校验覆盖范围

`meihua_check.py` 目前至少要拦下这些错：

- 三爻卦被画成两条
- 六爻卦少线
- 本卦上半下半没有复用上卦/下卦
- 动爻高亮位置不对
- 动爻不是按“自下而上”数
- 动前阴阳、动后阴阳跟结果不一致
- 变卦线型与结果不一致
