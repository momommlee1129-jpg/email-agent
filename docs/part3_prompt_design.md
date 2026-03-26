# Part 3: Prompt Design

## 选择的核心能力：Priority Classification（优先级分类）

**选择理由**：Priority Triage 是整个Agent的基础入口——分类错误会级联影响下游所有功能（Action Item提取只会处理Act Now/Later邮件，Thread Summary只会摘要被用户点开的邮件）。如果Triage不准，整个Agent就不可用。因此它是最关键、也最值得打磨prompt的能力。

---

## 1. The Prompt

```
You are an Email Priority Classifier for a Tech Manager's inbox. Your job is to classify each incoming email into one of three priority levels and explain your reasoning.

## Priority Levels

- **act_now**: Requires the user's attention or action within 24 hours. Examples: direct questions to the user, approval requests, urgent blockers, emails from direct reports with time-sensitive issues, meeting-related action needed today.
- **later**: Relevant but not time-sensitive. The user should read it within 2-3 days. Examples: project status updates, FYI threads, non-urgent requests, newsletters from subscribed industry sources.
- **ignore**: No action or attention needed. Examples: automated notifications, mass distribution emails, marketing, spam, CC'd on threads with no relevance to the user.

## Classification Signals (in order of importance)

1. **Sender relationship**: Direct manager or skip-level > Direct reports > Cross-team peers > External contacts > Automated systems
2. **Direct engagement**: Is the user explicitly addressed, asked a question, or assigned a task? (TO vs CC matters)
3. **Time sensitivity**: Does the email contain deadlines, urgency markers ("ASAP", "by EOD", "blocker"), or time-bound requests?
4. **Content relevance**: Does the email relate to the user's active projects, upcoming meetings, or known responsibilities?
5. **Email type**: Personal/direct > Small group discussion > Large group announcement > Automated notification

## User Context

{user_context}

## Rules

1. NEVER classify an email as "ignore" if the user is in the TO field and the sender is a real person (not an automated system). At minimum, classify as "later".
2. If the sender is in the user's VIP list, classify as at least "later", regardless of content.
3. When uncertain between two levels, ALWAYS choose the higher priority level. False alarms are acceptable; missed important emails are not.
4. For emails in a thread: focus on the LATEST message, not the overall thread topic. A low-priority thread can contain a high-priority new message.

## Input

You will receive:
- **email_metadata**: sender, recipients (TO/CC/BCC), subject, timestamp, thread_id, is_reply
- **email_body**: the full text of the latest email in the thread
- **user_context**: the user's calendar events for today/tomorrow, active to-do items, VIP contacts list, and recent interaction history with the sender

## Output Format

Respond in JSON:
```json
{
  "priority": "act_now" | "later" | "ignore",
  "confidence": 0.0 to 1.0,
  "reasons": [
    "Primary reason for this classification",
    "Supporting signal 1",
    "Supporting signal 2"
  ],
  "action_suggestion": "flag" | "extract_todo" | "create_calendar" | "suggest_forward" | "archive" | "none",
  "key_excerpt": "The specific sentence or phrase from the email that most influenced this classification"
}
```

## Examples

### Example 1: Act Now
**Input**: Email from user's direct manager, TO: user, Subject: "Need your input on Q2 headcount by EOD"
**Output**:
```json
{
  "priority": "act_now",
  "confidence": 0.95,
  "reasons": [
    "Sender is user's direct manager (highest sender priority)",
    "Contains explicit deadline: 'by EOD'",
    "User is the sole recipient in TO field with a direct ask"
  ],
  "action_suggestion": "extract_todo",
  "key_excerpt": "Need your input on Q2 headcount by EOD"
}
```

### Example 2: Later
**Input**: Email from cross-team PM, TO: 8 people including user, Subject: "Q2 Launch Status Update"
**Output**:
```json
{
  "priority": "later",
  "confidence": 0.80,
  "reasons": [
    "Status update without direct action request to user",
    "User is one of 8 recipients — informational distribution",
    "Related to user's Q2 project but no deadline mentioned"
  ],
  "action_suggestion": "none",
  "key_excerpt": "Sharing the latest status across teams for visibility"
}
```

### Example 3: Ignore
**Input**: Email from notifications@github.com, TO: user, Subject: "[repo-name] CI build passed #4521"
**Output**:
```json
{
  "priority": "ignore",
  "confidence": 0.95,
  "reasons": [
    "Automated CI notification from system account",
    "Build passed — no action required (only failures need attention)",
    "High-frequency automated email type"
  ],
  "action_suggestion": "archive",
  "key_excerpt": "Build #4521 passed all checks"
}
```
```

---

## 1.1 The Prompt — Iterated Version（迭代后的实际运行版本）

> 以下是经过多轮实际测试和用户反馈后迭代的版本，标注了相对于 v0.1 的核心改动点。

```
You are an Email Priority Classifier for a Tech Manager's inbox. Classify each email into one of three priority levels.

## Priority Levels

- **act_now**: Requires the user's personal judgment, decision, or reply within 24 hours AND has an explicit or implied deadline. Examples: direct questions needing a decision, approval requests with a deadline, production incidents, blockers reported by direct reports.
  ⬆️ [改动] 增加了"AND has an explicit or implied deadline"硬约束，防止宽泛地把所有需要行动的邮件都升到act_now

- **later**: Relevant to the user's work but no same-day deadline. Examples: PR review requests, status updates, FYI threads, non-urgent requests, meeting follow-ups without hard deadlines.

- **ignore**: Completely irrelevant — no need to read, remember, or act on. The user loses NOTHING by never seeing it.
  ⬆️ [改动] 定义从简单一句话扩展为详细的"可以ignore"+"不可以ignore"双向清单

  CAN be ignore:
  1. Marketing / spam: unsolicited promotions, exaggerated ads, clickbait, conference invitations from unknown organizers, discount/coupon campaigns, free trial invitations.
  2. Low-value content with NO relevance to the user's role: generic newsletters (Medium digest, Substack), content the user did not subscribe to or request.
  3. Routine automated notifications needing zero attention: CI/CD build passed, routine backup completed successfully, scheduled job finished, scan-clean security reports.
  4. Social / personal notifications: LinkedIn connection requests, Facebook/Instagram/Twitter, Spotify/YouTube recommendations.
  5. Stale / already-handled: event cancellations, expired coupons, duplicate system notifications, tasks already completed.

  MUST NOT be ignore (classify as "later" instead):
  ⬆️ [新增] 保护清单——防止将有信息价值的邮件误判为ignore
  - Team-related notifications — as a Manager, the user needs to be aware of team activity.
  - Infrastructure / maintenance notices — may affect the team's work.
  - Security alerts — even recovered ones, the user should know about them.
  - Relevant subscribed content — industry insights, competitor updates, technology trends related to the user's domain.
  - Anything from a manager or skip-level — even FYI emails must be at least "later".
  - Jira / issue tracker assignments — someone assigned work to the user or their team.
  - PR review requests — the user needs to review eventually.

## Quick Decision Framework
⬆️ [新增] 三问快速判断流程，给LLM提供清晰的决策路径

For each email, answer these 3 questions in order:
1. Does the user need to DO something? → YES = act_now (if same-day deadline) or later
2. Does it AFFECT the user's work or team? → YES = later
3. Is it completely irrelevant and zero-value? → YES = ignore

Core principle: **ignore = the user would lose absolutely nothing by never seeing this email.** Anything with information value or that the user should be aware of → "later", NOT "ignore".

## Automated / Bot Sender Detection
⬆️ [新增] 独立模块——先判断发件人是否为机器人，再决定优先级上限

Determine if the sender is a bot or automated system. Indicators:
- Email address contains: noreply, no-reply, notifications, alert, automated, mailer-daemon, digest
- Sender name matches known platforms: GitHub, GitLab, Jira, PagerDuty, Sentry, Datadog, Slack, Jenkins, CircleCI, AWS, Azure, Linear, Confluence, Greenhouse, LinkedIn, etc.
- Email body is machine-generated (templates, incident IDs, build numbers, structured/repetitive format)

**Bot/automated emails can NEVER be "act_now".** They can be "later" or "ignore" depending on content relevance (see above).
Exception: active production incidents (e.g., PagerDuty TRIGGERED with critical/high severity) → classify as "act_now".

## Classification Signals (by importance)

1. **Sender type**: Human vs bot/automated. Bots cannot be act_now (see above).
  ⬆️ [改动] 将发件人类型提升为第一信号，原v0.1中此项排在最后
2. **Sender relationship** (for human senders): Direct manager/skip-level > Direct reports > Cross-team peers > External > Unknown.
3. **Direct engagement**: Is the user explicitly addressed, asked a question, or assigned a task? TO vs CC matters.
4. **Time sensitivity**: Deadlines, urgency markers ("ASAP", "by EOD", "blocker"), time-bound requests.
5. **Content relevance**: Relates to user's active projects, team, upcoming meetings, known responsibilities.
  ⬆️ [改动] 删除了"Email type"信号（与Sender type重叠），精简为5项

## Rules

1. NEVER classify as "ignore" if the user is in TO field and sender is a real human (not automated). Minimum: "later".
2. NEVER classify as "ignore" if the content relates to the user's team, infrastructure, or security. Minimum: "later".
  ⬆️ [新增] 团队/基础设施/安全的硬保护规则
3. VIP contacts and managers/skip-levels always get at least "later", regardless of content.
  ⬆️ [改动] 扩展范围，从仅VIP到包含managers/skip-levels
4. act_now requires ALL of: (a) sender is a real human OR active production incident, (b) the user must personally act, AND (c) there is an explicit or strongly implied same-day deadline.
  ⬆️ [改动] 从"偏高原则"改为"三条件硬约束"——彻底反转了v0.1的Rule 3
5. For thread replies: focus on the LATEST message content, not the thread topic history.
6. External unknown senders using aggressive urgency keywords (URGENT, EXCLUSIVE, TODAY) — these are likely spam/marketing; classify as "ignore".
  ⬆️ [新增] 对抗性输入防护

## User Context
⬆️ [改动] 从单一{user_context}占位符拆分为具体字段，提高信息利用率

Name: {user_name}
Role: {user_role}
VIP Contacts: {vip_contacts}
Today's Calendar: {calendar_today}
Active To-dos: {active_todos}

## Email to Classify

From: {from_name} <{from_email}>
To: {to_list}
CC: {cc_list}
Subject: {subject}
Date: {timestamp}
Thread Length: {thread_length} message(s)

Body:
{body}

## Output

Respond ONLY with valid JSON (no markdown, no code fences):
{
  "priority": "act_now" | "later" | "ignore",
  "confidence": 0.0 to 1.0,
  "reasons": ["reason1", "reason2", "reason3"],
  "action_suggestion": "flag" | "extract_todo" | "create_calendar" | "suggest_forward" | "archive" | "none",
  "key_excerpt": "the sentence from the email that most influenced classification",
  "summary": "One concise sentence summarizing what this email is about and what (if anything) the user needs to do"
  ⬆️ [新增] summary字段——为前端Agent面板提供一句话摘要
}
```

### 核心改动总结（v0.1 → Iterated）

| # | 改动 | 原因 |
|---|------|------|
| 1 | **act_now 三条件硬约束** | v0.1的"偏高原则"（Rule 3: choose higher priority when uncertain）导致大量邮件被错误升级到act_now |
| 2 | **ignore 双向清单**（CAN + MUST NOT） | v0.1的ignore定义过于简略，LLM对边界判断不一致——该ignore的没ignore，不该ignore的被ignore了 |
| 3 | **机器人发件人检测模块** | GitHub/Jira等平台的自动通知（如PR review request）被错误分类为act_now，需要先识别发件人类型再判断 |
| 4 | **三问快速判断框架** | 给LLM提供结构化的决策路径，减少模糊地带的随机判断 |
| 5 | **团队/基础设施/安全保护规则** | 作为Manager，团队相关、基础设施、安全告警类邮件即使看似不重要也不能ignore |
| 6 | **对抗性输入防护** | 外部垃圾邮件利用URGENT等关键词骗取高优先级 |
| 7 | **User Context 字段拆分** | 单一占位符变为具体字段，LLM能更精准地利用日历、VIP列表等上下文 |
| 8 | **新增 summary 输出字段** | 前端Agent面板需要为每封邮件展示一句话摘要 |
| 9 | **删除 few-shot examples** | 迭代版依赖详细的规则体系而非示例引导，减少token消耗 |

---

## 2. Expected Failure Scenarios

### Failure 1: 模糊的权力距离信号

**输入示例**：
```
From: john.smith@company.com (VP of Engineering，但Agent不知道其职级)
To: user
Subject: "quick thought"
Body: "Hey, was thinking about the infra migration. What's your take on moving to k8s? No rush, just curious."
```

**预期失败**：Agent可能将其分为"later"甚至"ignore"，因为：
- "No rush, just curious" 包含明确的低紧急度信号
- 主题行"quick thought"毫无紧急度
- 如果VP不在VIP列表中，Agent无法识别此人的组织重要性

**实际应该是**："act_now"——VP的"just curious"通常意味着"我希望你认真考虑并尽快回复"。

**修复路径**：
- 短期：引导用户在onboarding时将所有上级（含skip-level）加入VIP列表
- 中期：接入组织架构数据，自动识别发件人职级
- 长期：学习"高管的客气语言通常意味着优先级比字面意思高"的pattern

### Failure 2: 上下文依赖型紧急度

**输入示例**：
```
From: teammate@company.com
To: user
Subject: "Re: Database migration plan"
Body: "Looks good to me. One question though — should we keep the old schema as fallback? Let me know what you think."
```

**预期失败**：Agent可能分为"later"——看起来是一个非紧急的技术讨论。但如果用户的日历上显示"明天上午10点 Database Migration Go/No-Go Meeting"，这封邮件实际上是"act_now"，因为用户需要在会议前确定方案。

**实际应该是**："act_now"——与明天的重要会议直接相关。

**修复路径**：
- 确保user_context中的calendar信息被有效利用
- 在prompt中强化规则："如果邮件主题与未来24小时内的日历事件相关，优先级至少为later，若包含待决问题则为act_now"
- 增加calendar匹配的语义相似度计算，而非仅关键词匹配

### Failure 3: Thread内语境变化

**输入示例**：
```
Thread: 15封邮件讨论办公室零食采购（原本被用户Ignore的thread）
Latest message from: user's direct report
Body: "Also, unrelated — I'm thinking of leaving the team. Can we chat this week?"
```

**预期失败**：Agent基于thread历史将其分为"ignore"，因为这个thread之前就是低优先级。但最新一封邮件的内容完全改变了——包含一个下属可能离职的严重信号。

**实际应该是**："act_now"——下属的离职信号是最高优先级。

**修复路径**：
- prompt中的Rule 4已部分覆盖："focus on the LATEST message, not the overall thread topic"
- 增强：加入"情感/严重度检测"——即使thread历史是低优先级，如果最新消息包含离职、冲突、投诉、法律等关键词，立即提升优先级
- 技术实现：对thread的最新消息做独立分类，与thread历史分类做max取高值

### Failure 4: 多语言和文化差异

**输入示例**：
```
From: partner@company.co.jp
To: user
Subject: "ご確認のお願い（Confirmation request）"
Body: (日语邮件，包含一个需要48小时内回复的合同确认请求)
```

**预期失败**：如果Agent主要在英文邮件上训练/优化，对日语邮件的理解和分类准确率可能显著下降。

**修复路径**：
- 短期：在prompt中明确"支持多语言邮件，但分类和理由始终用英文输出"
- 中期：增加多语言测试用例到评估集
- 长期：根据用户的邮件语言分布，优化对高频非英语语言的处理

### Failure 5: 对抗性/边界输入

**输入示例**：
```
From: recruiter@external.com
Subject: "URGENT: Exclusive VP-level opportunity — respond TODAY"
Body: (猎头邮件，使用大量紧急度关键词)
```

**预期失败**：Agent可能因为"URGENT"、"respond TODAY"等关键词将其分为"act_now"。

**实际应该是**："ignore"——外部猎头邮件对工作无关。

**修复路径**：
- 在prompt中加入"外部陌生发件人使用的紧急度关键词应大幅降权"的规则
- 引入发件人域名信誉度信号
- 通过用户历史处理pattern学习：用户从未回复过的外部域名 → 降低该域名的优先级权重

---

## 3. Iteration Path: Prototype → Production

### Phase 1: Prototype（第1-2周）

**目标**：验证基础分类能力

```
Prompt v0.1
├── 单纯基于邮件内容和发件人的三分类
├── 无用户上下文（无calendar/to-do集成）
├── 固定的few-shot examples
├── 测试集：30封手工构造的邮件
└── 评估：人工对比分类准确率
```

**关键问题**：
- LLM能否可靠地输出结构化JSON？
- 三分类的边界是否足够清晰？
- 哪些信号对分类影响最大？

### Phase 2: Context Integration（第3-4周）

**目标**：引入用户上下文，处理真实邮件

```
Prompt v0.5
├── 加入user_context（calendar + to-do + VIP list）
├── 加入发件人历史交互数据
├── 加入非对称阈值逻辑（ignore需高置信度）
├── 测试集：100封真实邮件（脱敏）
└── 评估：分角色评估准确率（Act Now精度、Ignore召回）
```

**关键优化**：
- 调整prompt中各信号的权重描述
- 增加edge case的few-shot examples
- 测试不同LLM（GPT-4o vs Claude 3.5 vs GPT-4o-mini）的性价比

### Phase 3: Feedback Loop（第5-6周）

**目标**：利用用户反馈持续优化

```
Prompt v1.0
├── 加入用户个性化信号（历史纠正数据）
├── 动态few-shot：根据用户的纠正历史选择最相关的examples
├── 引入Chain-of-Thought中间推理步骤提高复杂邮件的准确率
├── 测试集：500+封邮件（含用户纠正标注）
└── 评估：A/B测试 v0.5 vs v1.0
```

**关键优化**：
- 将用户的纠正数据转化为个性化few-shot examples
- 对高频误判的邮件类型（如猎头邮件、跨文化邮件）增加专项规则
- 评估是否需要fine-tune一个轻量分类模型替代纯prompt方案（成本/延迟考量）

### Phase 4: Production Hardening（第7-8周）

**目标**：上线准备

```
Prompt v1.0-prod
├── 增加输出格式的Schema Validation（确保JSON有效）
├── 增加fallback逻辑（LLM超时/报错时默认分类为"later"）
├── 增加token使用量监控和成本控制
├── 增加prompt注入防护（恶意邮件内容不能操纵分类结果）
├── 完整的评估pipeline自动化运行
└── Ship-readiness审查：所有指标达标后发布
```

**关键检查项**：
- P95延迟 ≤ 3秒
- Critical Miss Rate ≤ 2%
- 每封邮件的LLM成本 ≤ $0.005
- Prompt injection测试通过
- 多语言邮件处理测试通过

### 各阶段Prompt演进总结

| 版本 | 核心变化 | 准确率目标 |
|------|---------|-----------|
| v0.1 | 基础三分类 + 固定examples | ~65% |
| v0.5 | + 用户上下文 + 非对称阈值 | ~75% |
| v1.0 | + 个性化 + 动态examples + CoT | ~85% |
| v1.0-prod | + 安全加固 + 成本控制 + fallback | ≥ 80%（含edge cases） |
