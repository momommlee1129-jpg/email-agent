# Part 4: Prototype — Build Log & Analysis

## 1. Prototype Overview

### 选择的组件
构建了一个覆盖 **三个核心功能的端到端 prototype**：
- **(A) Priority Triage** — 邮件优先级三分类
- **(C) Action Item Extraction** — 待办事项提取
- **(D) Thread Summary** — 长邮件链摘要

### 技术栈
- **Frontend**: Streamlit（快速原型，交互式UI）
- **LLM**: OpenAI API（支持任意兼容接口，通过环境变量配置）
- **Data**: 10封mock邮件 + 1个12封邮件的长thread，模拟Tech Manager真实场景

### 为什么选择这个组合而非单个组件
Priority Triage是最关键的单一组件，但**仅演示分类缺乏说服力**——分类的价值在于它驱动下游动作。通过串联A→C→D，prototype展示了完整的用户流：分类→理解→行动。这本身也是一个产品判断：Agent的价值不在单个功能，而在功能之间的协同。

---

## 2. Build Log: Iteration Process

### Iteration 1: Baseline Prompt（最简版本）

**做法**：直接给LLM一封邮件，让它分为act_now/later/ignore三类。

**问题**：
- 外部猎头邮件因为包含"URGENT"、"TODAY"等关键词被分为act_now
- 自动通知邮件的分类不稳定，有时ignore有时later
- 输出格式不稳定，偶尔返回markdown而非JSON

**调整**：
- 增加Rule 5：明确外部陌生发件人的urgency关键词应降权
- 增加自动化邮件的判断规则（no-reply地址、系统账号）
- 在output要求中强调"Respond ONLY with valid JSON (no markdown, no code fences)"

### Iteration 2: 加入User Context

**做法**：将用户的日历、to-do列表、VIP联系人注入prompt。

**问题**：
- 日历信息有助于提升与会议相关邮件的分类准确度
- 但prompt变长后，LLM对few-shot examples的关注度下降
- Token成本增加约40%

**调整**：
- 精简user context的格式，用列表而非段落
- 将few-shot examples移到prompt末尾（靠近output要求），利用recency bias
- 测试gpt-4o-mini vs gpt-4o的成本/质量权衡

### Iteration 3: 非对称阈值 + 错误处理

**做法**：在分类逻辑中加入"宁可False Positive不可False Negative"的原则。

**问题**：
- 单纯靠prompt中的规则表述，LLM不总是遵守
- JSON解析偶尔失败（LLM在JSON外包裹了code fences）

**调整**：
- 在prompt中多处重复强调"when uncertain, choose higher priority"
- 加入JSON解析的fallback逻辑（去除code fences后重试）
- 增加temperature=0.1以提高输出稳定性

### Iteration 4: Action Item Extraction + Thread Summary

**做法**：在Triage基础上增加两个下游功能。

**问题**：
- Action Item提取对"隐式任务"（如"btw, can you also..."）的召回率偏低
- Thread Summary对立场变化的识别不够强

**调整**：
- 在extraction prompt中增加规则"scan every paragraph, including btw/also/one more thing sections"
- 在summary prompt中增加结构化输出字段"direction_changes"，强制模型关注立场变化
- 增加时间加权规则"focus on LATEST state"

---

## 3. Prototype vs. Design Gap Analysis

经过实际构建和测试，以下是Part 2设计与prototype实际表现之间的差距：

### Gap 1: 信号体系的理想 vs 现实

**设计中**：定义了丰富的信号体系（发件人关系、历史交互频率、情感分析等）。

**Prototype中**：实际只使用了：发件人身份、TO/CC区分、邮件内容关键词、日历关联、VIP名单。

**原因**："历史交互频率"和"用户对类似邮件的历史处理速度"需要持久化的用户行为数据，MVP阶段没有。

**修正建议**：Part 2的信号体系应分为"V1可用信号"和"V2需数据积累的信号"两层。V1应聚焦前5个信号，足以达到可用准确率。

### Gap 2: 渐进式信任建立的复杂性

**设计中**：设想了"第1周只展示→第2周启用折叠→第3周开放action item"的渐进路径。

**Prototype中**：所有功能同时可用，没有渐进逻辑。

**原因**：渐进式信任需要用户级别的状态管理和时间追踪，原型阶段实现成本过高。

**修正建议**：V1可以简化为两个阶段——"观察期（第1周，只展示不折叠）"和"正常期（第2周起，启用折叠+action item）"。比原设计的四阶段更可行。

### Gap 3: Thread Summary的结构化难度

**设计中**：要求摘要包含"讨论主题、关键分歧、最新结论"三段结构。

**Prototype中**：LLM基本能生成结构化输出，但"direction_changes"字段的质量不稳定——有时会把正常的讨论推进也标记为"方向变化"。

**修正建议**：在prompt中更精确定义"direction change"为"对之前已达成的共识的推翻或重大修改"，而非"讨论的自然演进"。

### Gap 4: 确认流程的UX复杂性被低估

**设计中**：简单描述了"用户确认后执行"。

**Prototype中**：每个action item需要单独点击确认按钮，当Act Now邮件多（5+封）且每封有2-3个action item时，确认操作本身成为负担。

**修正建议**：应设计"批量确认"和"一键全部确认"机制。对高置信度（>0.9）的action item可以默认勾选，用户只需取消不需要的。

### Gap 5: 错误展示的重要性

**设计中**：关注了LLM输出的准确性指标。

**Prototype中**：发现当LLM返回错误（API超时、JSON解析失败）时，用户体验断裂严重——没有优雅降级。

**修正建议**：Part 2应增加一个"Degraded Mode"设计——当LLM不可用时，至少基于规则引擎做基础分类（自动通知→Ignore，VIP→Act Now），而非完全失败。

---

## 4. Eval Dry-Run

### 测试用例设计

10封mock邮件覆盖以下场景分布：

| 场景 | 数量 | 期望分类 |
|------|------|---------|
| 上级紧急请求 | 1 | act_now |
| 直接下属+阻塞问题 | 2 | act_now |
| CTO直接指派任务 | 1 | act_now |
| 跨团队状态更新（含action item） | 1 | act_now |
| HR通知（有截止日但不紧急） | 1 | later |
| 同级coffee chat | 1 | later |
| CI自动通知（通过） | 1 | ignore |
| 安全扫描自动报告（无问题） | 1 | ignore |
| 外部猎头spam | 1 | ignore |

### 运行方式

```bash
cd email-agent
cp .env.example .env   # 填入API key
pip install -r requirements.txt
python -m eval.run_eval  # 命令行评估
streamlit run app.py     # 交互式UI（含Evaluation tab）
```

### 预期结果分析

| 指标 | 目标 | 说明 |
|------|------|------|
| Overall Accuracy | ≥ 80% (8/10) | 10封中允许最多2封分错 |
| Critical Miss Rate | 0% | 5封act_now邮件不应有任何一封被标为ignore |
| 最可能的误判 | email_005 (David's status update) | 这封邮件形式是群发status update，但包含对用户的explicit action item，Agent可能因群发形式而降级 |
| Recruiter Spam | 正确ignore | 测试Agent是否能抵抗fake urgency signals |

### 关键测试场景深度分析

**Case 1: CTO邮件在CC中 (email_010)**
- CTO在邮件中直接@用户要求提交风险评估
- 但用户是CC而非TO（TO是Sarah Wong）
- 测试Agent是否能识别"虽然是CC但内容直接指向用户"

**Case 2: 猎头spam (email_006)**
- 充斥URGENT、TODAY等假紧急信号
- 测试Rule 5（外部陌生发件人urgency降权）是否生效

**Case 3: 直接下属的career discussion (email_007)**
- 同时包含两类内容：career话题（敏感）+ PR审批（blocking）
- 测试Agent是否能同时识别两个不同的action item
