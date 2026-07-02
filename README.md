# AI梅花易数 Codex 插件

一个可开源分享的 Codex 插件，用来把：

- 一个具体问题
- 一个两位数字

转换成：

- 梅花易数本卦 / 变卦推演结果
- 可校验的结构化数据
- 不乱画卦线的教学推演图 PNG

这个插件的核心目标不是“神神叨叨地给结论”，而是把整个推演过程讲清楚、画清楚、校验清楚。

## 为什么做这个插件

很多“AI 算卦”类产品有两个常见问题：

1. 会说结果，但不会把推演过程讲清楚
2. 一旦让模型直接画卦，很容易把三爻、六爻、动爻位置画错

这个插件重点解决的就是第二类问题：

- 先确定性计算
- 再确定性校验
- 再输出教学图

也就是说，先保证“对”，再考虑“好看”。

## 适合谁用

适合这些用户：

- 想用 Codex 做梅花易数起卦的人
- 想学习梅花易数过程，而不是只看一句结论的人
- 想把“问题 -> 数字 -> 本卦 -> 变卦 -> 体用 -> 五行”完整走一遍的人
- 想把这套能力沉淀成一个别人也能下载使用的 Codex 插件的人

## 插件定位

- 中文名：`AI梅花易数Codex插件`
- 插件目录名：`meihua-yishu`
- 发布目标：独立开源，不依附 OpenCMO 内部项目

## 核心能力

### 1. 起卦计算

依据两位数字计算：

- 上卦
- 下卦
- 本卦
- 动爻
- 变卦

### 2. 结构化结果输出

输出结构化结果文件：

- `result.json`
- `qa_report.json`

其中：

- `result.json` 负责存放事实结果
- `qa_report.json` 负责存放校验结论

### 3. 确定性图形输出

输出可核对的确定性图形资产：

- `upper_trigram.svg`
- `lower_trigram.svg`
- `primary_hexagram.svg`
- `changed_hexagram.svg`
- `process_overview.svg`
- `step_by_step_report.svg`
- `deterministic_teaching_card.png`

### 4. 教学推演图

默认输出一张不会乱画卦线的教学 PNG：

- `deterministic_teaching_card.png`

它会固定包含：

- 问题与数字
- 本卦计算
- 变卦计算
- 动爻高亮
- 八卦数字对应
- 八卦五行对应
- 五行生克图
- 体用关系
- 最终结论

### 5. 可选美化层

插件保留了一个可选美化层：

- `Imma / image2`

但它默认关闭。

原因很简单：

- 美化模型一旦自由生成，容易把卦线、动爻和变卦画错

所以当前默认策略是：

- 默认给“正确版”
- 只有用户明确要求“更好看/海报版/美化版”时才额外生成

## 这个插件的设计原则

这是本项目最重要的地方。

### 原则一：先对，再美

默认优先级：

1. 事实正确
2. 校验通过
3. 再谈视觉美化

### 原则二：三爻和六爻不能交给模型脑补

插件专门避免这些错误：

- 三爻卦被画成两条线
- 六爻卦少一条
- 本卦上下卦拼接错
- 动爻位置错
- 阴阳变化方向错
- 变卦图形与名称不一致

### 原则三：默认主结果是“确定性正确教学图”

前台默认主结果：

- `deterministic_teaching_card.png`

不是：

- SVG
- Magic 2 / image2 直接自由绘图结果

## 当前工作流

插件默认按这个顺序工作：

1. `meihua-guided-intake`
2. `meihua-primary-hexagram`
3. `meihua-changed-hexagram`
4. `meihua-interpretation`
5. `meihua-diagram-qa`
6. `meihua-deterministic-card`
7. `meihua-imma-teaching-png`（可选）

这套流程的好处是：

- 先把结果算准
- 再把图校准
- 最后才允许做美化

## 安装方式

### 方式一：下载 ZIP 后本地安装

1. 下载本仓库 ZIP
2. 解压到本地插件目录，例如：

```bash
mkdir -p ~/plugins
unzip ai-meihua-yishu-codex-plugin.zip -d ~/plugins
```

3. 确保解压后目录是：

```bash
~/plugins/meihua-yishu
```

4. 在 Codex 中安装：

```bash
codex plugin add meihua-yishu@personal
```

### 方式二：直接克隆仓库后安装

```bash
mkdir -p ~/plugins
cd ~/plugins
git clone https://github.com/xuquangeo/ai-meihua-yishu-codex-plugin.git meihua-yishu
codex plugin add meihua-yishu@personal
```

### 更新插件

如果已经装过旧版本，更新代码后重新执行：

```bash
codex plugin add meihua-yishu@personal
```

建议在新线程里测试更新后的插件能力。

## 如何使用

直接对 Codex 说：

- `按梅花易数帮我起卦，问题是明天杭州会不会下雨，数字73`
- `按梅花易数推演这件事，并把每一步画出来`
- `先给我正确版教学图，不要美化版`

如果你明确想要更漂亮版本，再说：

- `在正确版基础上，再给我一张美化教学图`

## 输出文件说明

### 核心结果文件

- `result.json`
- `qa_report.json`

### 图形文件

- `upper_trigram.svg`
- `lower_trigram.svg`
- `primary_hexagram.svg`
- `changed_hexagram.svg`
- `process_overview.svg`
- `step_by_step_report.svg`
- `deterministic_teaching_card.png`

### 可选美化文件

- `imma_teaching_card.png`

## 仓库结构

- `.codex-plugin/plugin.json`
  插件清单

- `skills/`
  插件 Skill 定义

- `scripts/meihua_calc.py`
  确定性计算和 SVG 出图

- `scripts/meihua_check.py`
  确定性校验脚本

- `scripts/render_deterministic_teaching_card.py`
  正确底稿 PNG 出图脚本

- `docs/manual.md`
  当前采用的规则摘要

- `docs/methodology-reference.md`
  方法论参考

- `docs/image2-teaching-card-spec.md`
  美化层固定规范

- `docs/reference-case-image2-card-rain-73.md`
  参考案例

- `docs/intake-playbook.md`
  输入引导手册

## 当前规则边界

当前版本是“数字起卦”版，先覆盖基础可用能力。

已支持：

- 两位数字起卦
- 本卦 / 变卦
- 动爻
- 体用关系
- 五行关系
- 教学推演图

暂未完整展开：

- 互卦
- 错卦
- 综卦
- 时间法
- 外应法
- 更复杂的断事规则

## 为什么默认不用 Magic 2 / image2 直接出主图

因为我们已经在实际测试中发现：

- 模型可能把三爻画成两条
- 模型可能把第四爻标成第三条或第五条
- 模型可能把“阴变阳”写成“阳变阴”

所以当前项目明确采用：

- `Magic 2 / image2` 不作为默认主结果
- 它只能作为可选美化层

这个决定是刻意的，不是能力缺失。

## Release 发布页是干什么的

如果你在 GitHub 上看到 `Releases`，它的主要作用是：

- 给用户一个“稳定版本下载入口”
- 不用让别人自己去点 `Code -> Download ZIP`
- 可以挂：
  - 版本说明
  - ZIP 安装包
  - 更新日志
  - 使用注意事项

简单说：

- 仓库首页更像“项目介绍页”
- Release 页更像“正式发版下载页”

如果后续这个插件要给更多人下载，建议用 Release 来分发版本。

## Roadmap

后续建议继续做：

- 增加互卦、错卦、综卦
- 增强不同问题类型的断法模板
- 增加更多案例模板
- 增加 GitHub Release 自动化发布
- 继续优化美化层，但不牺牲正确性

## License

本项目采用 [MIT License](./LICENSE)。

欢迎学习、使用、修改和二次分发，但请保留原始许可说明。
