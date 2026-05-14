# 视觉模板索引

这份索引用于说明当前 skill 中已经保存了哪些真实视觉样本，以及它们分别适合拿来对照什么类型的论文页面或图表。

## 1. 论文插图样式

目录：
- `references/visual-style-samples/figures`

当前样本文件：
- `figure-er-diagram-sample-01.png`
- `figure-er-diagram-sample-01.svg`
- `figure-flowchart-vertical-sample-01.png`
- `figure-flowchart-vertical-sample-01.svg`
- `figure-system-structure-tree-sample-01.png`
- `figure-system-structure-tree-sample-01.svg`
- `figure-use-case-diagram-sample-01.png`
- `figure-use-case-diagram-sample-01.svg`
- `figure-sequence-diagram-sample-01.svg`

默认语义用途：
- 系统总体结构图
- 模块结构图或功能结构图
- ER 图或实体关系图
- 用例图或流程类示意图
- 纵向黑白教材式流程图
- UML 时序图

使用规则：
- 当用户没有提供更强的新样本时，先拿这些样本与新生成的论文插图做视觉比对。
- 如果当前图形类型比这些样本更具体，则优先使用用户提供的样本或当前论文模板。

## 2. 公式样式

目录：
- `references/visual-style-samples/formulas`

当前样本文件：
- `formula-layout-sample-01.png`
- `formula-layout-sample-01.svg`

默认语义用途：
- 公式行外观
- 公式编号位置
- 公式上下留白

使用规则：
- 只有在当前模板没有明确规定公式外观时，才把这里的样本作为视觉兜底参考。
- 如果当前模板或已接受稿件已经使用按章节编号的形式，例如 `(2-1)`，则必须继续沿用该编号体系，不能改成全文顺排 `(1)(2)(3)`。

## 3. 表格样式

目录：
- `references/visual-style-samples/tables`

当前样本文件：
- `table-style-sample-03-20260419-page.png`

默认语义用途：
- 论文表格边框风格
- 表题位置
- 表格密度与对齐
- WPS 内置 `第二个三线表` 预设的渲染验收页参考

使用规则：
- 优先看模板。
- 对 skill 当前保存的三线表规则，只保留 `WPS 表格样式里第二个三线表` 这一套。
- `table-style-sample-03-20260419-page.png` 不是 WPS 样式库缩略图本体，而是该内置预设的渲染验收页样本。
- 不要再把旧表格样本当成其他可选三线表变体来使用。

## 4. 目录样式

目录：
- `references/visual-style-samples/toc`

当前样本文件：
- `toc-style-sample-01.png`
- `toc-style-sample-01.svg`

默认语义用途：
- 目录缩进层级
- 点线引导符
- 页码右对齐
- 目录行距节奏

使用规则：
- 如果存在目录样本，在论文最终格式复核时应把它视为强视觉对照目标。

## 5. 当前缺失的样本类别

以下类别在视觉样本体系里是概念上支持的，但当前 skill 快照中还没有确认存在的真实样本图：
- `title-pages`
- `headers-footers`
- `body-text`

如果后续任务高度依赖这些页面样式，在把它们当作稳定样式基线前，应先补充真实样本图。

## 6. 维护规则

当新增样本图片时：
- 放到正确的分类目录中
- 同步更新这份索引
- 记录的是样本的语义用途，不只是一个文件名
- 不要留下没有用途说明的截图文件
