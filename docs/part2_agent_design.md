# Part 2: Agent Design

实现范围：Priority Classification + Action Item Extraction

---

## 1. Decision Logic

### 1.1 架构

```
┌────────────────────────────────────────────────┐
│              Email Processing Agent              │
│                                                  │
│  Bot Detection ──▶ Priority Classifier ──▶ Action Router
│  (内部/外部)       (3问 + 硬规则 + LLM)     │
│                                              ▼
│                                    Action Item Extractor
│                                    (To-do / Calendar)
│                                              │
│                                         User Actions
│                                    (确认/修改/标记已处理)
└────────────────────────────────────────────────┘
```

### 1.2 信号体系（按权重排序）

| 信号 | 权重 | 说明 |
|------|------|------|
| 发件人类型 | 最高 | 人类 vs 内部机器人 vs 外部机器人 |
| 发件人关系 | 高 | 上级 > 下属 > 跨组 > 外部 > 未知 |
| 直接参与度 | 高 | TO vs CC、是否被提问/分配任务 |
| 时效性 | 高 | 截止日期、"ASAP"、"by EOD" |
| VIP/黑名单 | 高 | VIP → 最低later；黑名单 → 强制ignore |
| 内容相关性 | 中 | 与活跃项目/近期会议的关联度 |

### 1.3 分类流程

```
Step 1: Bot Detection
  内部机器人（Jira/PagerDuty/Sentry等）→ 紧急告警可act_now，常规最高later
  外部机器人（LinkedIn/Medium/营销等）→ 上限later，营销类直接ignore

Step 2: 三问判断
  ① 需要用户做什么？ → act_now（当天截止）或 later
  ② 影响用户工作/团队？ → later
  ③ 完全无关零价值？ → ignore

Step 3: 联系人规则（前端硬规则，优先于LLM）
  黑名单 → ignore | VIP → 最低later

Step 4: LLM硬规则
  真人TO → 最低later | 团队/基础设施/安全 → 最低later | 上级 → 最低later
  act_now = 真人或内部事故 + 需亲自行动 + 当天截止/正在发生

Step 5: ignore双向校验
  CAN: 营销、无关推送、无需关注的通知、社交通知、过时信息
  CANNOT: 团队通知、基础设施、安全告警、上级邮件、工单分配、PR review

Step 6: LLM综合分类 → { priority, confidence, reasons, summary }
```

### 1.4 Action Item Extraction

| 行动 | 触发条件 | 自动化 |
|------|---------|--------|
| Extract to-do | 包含任务指派/截止日期 | act_now自动，later手动 |
| Create calendar | 包含会议/时间安排 | act_now自动，later手动 |

提取规则：只提取分配给用户的任务 · 逐段扫描含"btw"/"also"等附带请求 · 每项附带原文出处 · 已添加项不可重复添加

### 1.5 Handled + Re-evaluation

| 功能 | 机制 |
|------|------|
| 已处理 | 手动标记Done → 移入Handled tab，Undo可恢复 |
| 重评估 | 每日9:00自动重评later邮件 + AI Settings手动触发，升级时toast通知 |

### 1.6 自动化原则

可逆操作自动化，不可逆需确认。

| 操作 | 程度 |
|------|------|
| 分类展示 / AI摘要 | 全自动 |
| Act Now的Action Item提取 | 全自动（可删除） |
| 标记已处理 / 修改优先级 | 用户手动 |
| 关闭AI服务 | 需确认（保留已有数据） |

---

## 2. Failure Modes

### FM1: 重要邮件误判为Ignore

**场景**：VP用个人邮箱发的随意主题邮件被标为Ignore。

**缓解**：真人TO → 最低later；VIP白名单保护；ignore双向校验；手动修改优先级。

**改进方向**：新发件人前3封不允许ignore；接入组织架构自动识别职级。

### FM2: Action Item遗漏

**场景**：长邮件最后一段的"btw, can you send me budget numbers by Thursday?"被遗漏。

**缓解**：prompt要求逐段扫描含"btw"等弱信号；每项附带source_quote可验证；用户可手动补充。

### FM3: 内部告警被降级

**场景**：PagerDuty生产告警被归为later（因为是机器人发件）。

**缓解**：区分内部/外部机器人；内部告警（TRIGGERED/critical）可升至act_now；涉及基础设施/安全 → 最低later。

### FM4: 优先级随时间变化

**场景**：周一later的邮件到周三截止日变为紧急。

**缓解**：每日9点自动重评later邮件（基于最新日历/to-do上下文）；手动Re-evaluate按钮；升级时toast通知。

---

## 3. Evaluation Framework

### 3.1 分类指标

| 指标 | 目标 | 测量 |
|------|------|------|
| Overall Accuracy | ≥ 80% | 1 - 用户纠正率 |
| Critical Miss Rate（Act Now误判为Ignore） | ≤ 2% | 从Ignore提升到Act Now的次数 |
| False Alarm Rate（Ignore误判为Act Now） | ≤ 15% | 从Act Now降级到Ignore的次数 |

### 3.2 提取指标

| 指标 | 目标 | 测量 |
|------|------|------|
| Recall | ≥ 85% | 人工标注ground truth对比 |
| Precision | ≥ 75% | 用户确认率 |

### 3.3 信任指标

| 指标 | 健康范围 | 危险信号 |
|------|---------|---------|
| Ignore Check Rate | 第1周>80% → 第4周<30% | 4周后仍>60% |
| Suggestion Acceptance | ≥ 70% | <50% |
| Override Trend | 逐周递减 | 持续不减 |
| Handled Adoption | 每日活跃 | 从不使用 |

### 3.4 Ship-readiness

全部满足方可发布：Accuracy ≥ 80% · Critical Miss ≤ 2% · Precision ≥ 75% · Recall ≥ 85% · 第4周Ignore Check ≤ 30% · P0 = 0 · P95延迟 ≤ 3s

**红线**：Critical Miss > 5% · 数据泄露 · 因Agent错误导致实际工作问题

### 3.5 数据采集

```
隐式信号：优先级纠正 · Action item确认/拒绝 · Handled使用 · Re-evaluate频率
显式反馈：手动修改优先级 · 手动添加/删除Action item · VIP/黑名单设置
人工评估：每周50封分类抽检 + 20个Action item recall评估
```
