# AI梅花易数 Codex 插件

一个可开源分享的 Codex 插件，用于把“问题 + 两位数字”转成一套可复用、可校验、可教学展示的梅花易数推演流程。

## 适用场景

- 想按梅花易数起卦
- 想把本卦、变卦、动爻过程讲清楚
- 想输出一张不会乱画卦线的教学 PNG
- 想把这套方法沉淀成别人也能下载使用的 Codex 插件

## 插件名称

- 中文名：`AI梅花易数Codex插件`
- 插件目录名：`meihua-yishu`

## 当前能力

- 依据两位数字计算上卦、下卦、本卦、动爻、变卦。
- 输出结构化 JSON 结果。
- 生成可视化 SVG：
  - 上卦
  - 下卦
  - 本卦
  - 变卦
  - 过程总览图
  - 四步推演图
- 可选保留一份 `image2 / image_gen` 教学卡版本，用于更美观的展示。
- 通过多个 Skill 协调：
  - 引导式输入
  - 起卦输入
  - 算本卦
  - 算变卦
  - 做解析
  - 正确底稿 PNG
  - 后台校准可视化
  - Imma / image2 美化教学图
  - 教学图校验

## 目录

- `.codex-plugin/plugin.json`：插件清单
- `skills/`：插件技能
- `scripts/meihua_calc.py`：确定性计算和 SVG 出图脚本
- `scripts/meihua_check.py`：确定性校验脚本
- `scripts/render_deterministic_teaching_card.py`：正确底稿 PNG 出图脚本
- `docs/manual.md`：当前版本采用的规则摘要
- `docs/methodology-reference.md`：按你的《梅花易数.png》整理的方法论参考
- `docs/image2-teaching-card-spec.md`：image2 教学卡固定规范
- `docs/reference-case-image2-card-rain-73.md`：image2 教学卡参考案例
- `docs/intake-playbook.md`：输入引导手册

## 安装方式

### 方式一：下载 ZIP 后本地安装

1. 下载本仓库 ZIP，解压到本地插件目录，例如：

```bash
mkdir -p ~/plugins
unzip ai-meihua-yishu-codex-plugin.zip -d ~/plugins
```

2. 确保解压后插件目录为：

```bash
~/plugins/meihua-yishu
```

3. 把它加入你的 Codex 本地插件市场后安装：

```bash
codex plugin add meihua-yishu@personal
```

### 方式二：直接克隆仓库后安装

```bash
mkdir -p ~/plugins
cd ~/plugins
git clone <你的仓库地址> meihua-yishu
codex plugin add meihua-yishu@personal
```

如果你已经装过旧版本，更新后重新执行一次：

```bash
codex plugin add meihua-yishu@personal
```

## 当前规则边界

- 先按你提供的梅花易数入门手册实现“数字起卦”版本。
- 默认接受两位数字，或两个单独数字。
- 五行判断先按手册里的入门规则输出“体用关系 + 五行关系 + 简要吉凶提示”。
- 复杂断事、时间法、外应法、互卦等暂未进入这一版。

## 脚本示例

```bash
python3 scripts/meihua_calc.py \
  --question "今年这个合作能不能顺利推进？" \
  --digits 7 8 \
  --out-dir ./work/example
```

输出结果：

- `result.json`
- `upper_trigram.svg`
- `lower_trigram.svg`
- `primary_hexagram.svg`
- `changed_hexagram.svg`
- `process_overview.svg`
- `step_by_step_report.svg`

## 默认输出策略

以后插件的可视化分成两层：

1. `正确底稿层`
- 先由脚本输出 `result.json + qa_report.json`
- 再由脚本直接生成 `deterministic_teaching_card.png`
- 这一层负责“绝对正确”
- 不允许模型自由改线

2. `Imma / image2 美化层`
- 在正确底稿之上做美化 PNG
- 只负责美术呈现
- 不负责卦象事实
- 如果美化层和底稿冲突，以底稿为准
- 这一层默认关闭，只有用户明确需要更美观版本时才启用

## 推荐使用方式

直接对 Codex 说：

- `按梅花易数帮我起卦，问题是明天杭州会不会下雨，数字73`
- `按梅花易数推演这件事，并把每一步画出来`
- `先给我正确版教学图，不要美化版`

## 默认交互策略

以后插件默认先走一层引导式输入：

1. 你想占什么事？
2. 请输入两位数字

该能力已独立封装为 `meihua-guided-intake` Skill。

## 推荐编排

当前插件推荐按这个固定顺序工作：

1. `meihua-guided-intake`
2. `meihua-primary-hexagram`
3. `meihua-changed-hexagram`
4. `meihua-interpretation`
5. `meihua-diagram-qa`
6. `meihua-deterministic-card`
7. `meihua-imma-teaching-png`（可选）

这样可以最大限度降低规则混乱。

## 前台展示硬规则

- 用户第一眼看到的最终结果，默认应为 `deterministic_teaching_card.png`
- `SVG` 只允许作为后台校准稿、开发稿、核对稿存在
- 不要把 `SVG` 作为默认展示结果返回给用户
- `Imma / image2` 美化版不再默认返回，只有用户明确需要时才追加

## 默认承诺

插件默认不让用户选模式。
它会直接告诉用户：

- 最后会给你一张图
- 这张图会说明这件事是怎么算出来的
- 这张图会给出最后结论
- 默认先给正确版，再视需要补美化版

## 教学卡固定要素

无论以后生成哪一次教学卡，都应尽量固定包含：

- 问题与数字
- 八卦名称与图形对照表
- 本卦计算过程
- 变卦计算过程
- 本卦图、变卦图、动爻高亮
- 八卦数字对应
- `八卦 -> 五行` 对应
- 五行生克图
- 体用关系
- 最终结论

其中五行生克图必须完整包含：

- 金
- 水
- 木
- 火
- 土

## 后续建议

- 增加互卦、错卦、综卦。
- 把 image2 教学卡做成真正的固定输出模式。
- 继续强化“先引导、再出最终教学图”的体验。

## License

默认采用 `MIT License`，便于开源传播和二次使用。
