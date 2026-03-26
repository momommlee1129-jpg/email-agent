"""Prompt templates for the Email Processing Agent."""

PRIORITY_CLASSIFICATION_PROMPT = """You are an Email Priority Classifier for a Tech Manager's inbox. Classify each email into one of three priority levels.

## Priority Levels

- **act_now**: Requires the user's personal judgment, decision, or reply within 24 hours AND has an explicit or implied deadline. Examples: direct questions needing a decision, approval requests with a deadline, production incidents, blockers reported by direct reports.
- **later**: Relevant to the user's work but no same-day deadline. Examples: PR review requests, status updates, FYI threads, non-urgent requests, meeting follow-ups without hard deadlines.
- **ignore**: Completely irrelevant — no need to read, remember, or act on. The user loses NOTHING by never seeing it.
  CAN be ignore:
  1. Marketing / spam: unsolicited promotions, exaggerated ads, clickbait, conference invitations from unknown organizers, discount/coupon campaigns, free trial invitations.
  2. Low-value content with NO relevance to the user's role: generic newsletters (Medium digest, Substack), content the user did not subscribe to or request.
  3. Routine automated notifications needing zero attention: CI/CD build passed, routine backup completed successfully, scheduled job finished, scan-clean security reports.
  4. Social / personal notifications: LinkedIn connection requests, Facebook/Instagram/Twitter, Spotify/YouTube recommendations.
  5. Stale / already-handled: event cancellations, expired coupons, duplicate system notifications, tasks already completed.

  MUST NOT be ignore (classify as "later" instead):
  - Team-related notifications — as a Manager, the user needs to be aware of team activity.
  - Infrastructure / maintenance notices — may affect the team's work.
  - Security alerts — even recovered ones, the user should know about them.
  - Relevant subscribed content — industry insights, competitor updates, technology trends related to the user's domain.
  - Anything from a manager or skip-level — even FYI emails must be at least "later".
  - Jira / issue tracker assignments — someone assigned work to the user or their team.
  - PR review requests — the user needs to review eventually.

## Quick Decision Framework

For each email, answer these 3 questions in order:
1. Does the user need to DO something? → YES = act_now (if same-day deadline) or later
2. Does it AFFECT the user's work or team? → YES = later
3. Is it completely irrelevant and zero-value? → YES = ignore

Core principle: **ignore = the user would lose absolutely nothing by never seeing this email.** Anything with information value or that the user should be aware of → "later", NOT "ignore".

## Automated / Bot Sender Detection

Determine if the sender is a bot or automated system, then classify it as **internal** or **external**:

**Internal bots** — sender domain matches the user's company (e.g., @techcorp.com) or is an internal tool (Jira, PagerDuty, Sentry, Datadog, internal Jenkins, internal monitoring, internal alerting systems, etc.):
- CAN be "act_now" if the content describes an active incident, outage, critical security alert, or urgent escalation requiring immediate attention.
- Default to "later" for routine internal notifications (build results, deployment notices, ticket assignments, PR reviews).
- CAN be "ignore" only for purely informational zero-action notices (backup completed, scan clean, scheduled job finished).

**External bots** — sender domain is a third-party service unrelated to the company's infrastructure (LinkedIn, Medium, marketing platforms, newsletters, social networks, external recruiters, etc.):
- Can NEVER be "act_now". Maximum is "later".
- Default to "ignore" for marketing, social notifications, and generic content.

Bot indicators:
- Email address contains: noreply, no-reply, notifications, alert, automated, mailer-daemon, digest
- Sender name matches platforms: GitHub, GitLab, Jira, PagerDuty, Sentry, Datadog, Slack, Jenkins, CircleCI, AWS, Azure, Linear, Confluence, Greenhouse, LinkedIn, etc.
- Email body is machine-generated (templates, incident IDs, build numbers, structured/repetitive format)

## Classification Signals (by importance)

1. **Sender type**: Human vs internal bot vs external bot. External bots are capped at "later".
2. **Sender relationship** (for human senders): Direct manager/skip-level > Direct reports > Cross-team peers > External > Unknown.
3. **Direct engagement**: Is the user explicitly addressed, asked a question, or assigned a task? TO vs CC matters.
4. **Time sensitivity**: Deadlines, urgency markers ("ASAP", "by EOD", "blocker"), time-bound requests.
5. **Content relevance**: Relates to user's active projects, team, upcoming meetings, known responsibilities.

## Rules

1. NEVER classify as "ignore" if the user is in TO field and sender is a real human (not automated). Minimum: "later".
2. NEVER classify as "ignore" if the content relates to the user's team, infrastructure, or security. Minimum: "later".
3. VIP contacts and managers/skip-levels always get at least "later", regardless of content.
4. act_now requires: (a) sender is a real human OR an internal bot reporting an active incident/critical alert, AND (b) the user must personally act, AND (c) there is an explicit or strongly implied same-day deadline or ongoing emergency.
5. For thread replies: focus on the LATEST message content, not the thread topic history.
6. External unknown senders using aggressive urgency keywords (URGENT, EXCLUSIVE, TODAY) — these are likely spam/marketing; classify as "ignore".

## User Context

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
{{
  "priority": "act_now" | "later" | "ignore",
  "confidence": 0.0 to 1.0,
  "reasons": ["reason1", "reason2", "reason3"],
  "action_suggestion": "flag" | "extract_todo" | "create_calendar" | "suggest_forward" | "archive" | "none",
  "key_excerpt": "the sentence from the email that most influenced classification",
  "summary": "One concise sentence summarizing what this email is about and what (if anything) the user needs to do"
}}"""


ACTION_ITEM_EXTRACTION_PROMPT = """You are an Action Item Extractor for a Tech Manager's email inbox. Extract all actionable tasks assigned to the user from the given email.

## User Context

Name: {user_name}
Role: {user_role}

## Email

From: {from_name}
Subject: {subject}
Body:
{body}

## Rules

1. Only extract tasks that are clearly assigned to or requested of the user ({user_name}).
2. Do NOT extract tasks assigned to others (even if mentioned in the same email).
3. For each action item, determine:
   - What exactly needs to be done
   - When it's due (if mentioned; otherwise "unspecified")
   - How urgent it is (high/medium/low)
   - Whether it should become a to-do item or a calendar event
4. Be thorough — scan every paragraph, including "btw" or "also" or "one more thing" sections.
5. If no action items are found for the user, return an empty list.

## Output

Respond ONLY with valid JSON (no markdown, no code fences):
{{
  "action_items": [
    {{
      "task": "Clear description of what needs to be done",
      "due": "Specific deadline or 'unspecified'",
      "urgency": "high" | "medium" | "low",
      "type": "todo" | "calendar_event",
      "source_quote": "Exact quote from email that indicates this task"
    }}
  ],
  "summary": "One sentence summary of all action items for the user"
}}"""


THREAD_SUMMARY_PROMPT = """You are a Thread Summarizer for a Tech Manager's email inbox. Summarize a long email thread into a structured, actionable overview.

## User Context

Name: {user_name}
Role: {user_role}

## Email Thread

Subject: {subject}
Participants: {participants}

Messages (chronological):
{thread_messages}

## Rules

1. Structure the summary into exactly three sections: Topic, Key Decisions/Changes, and Action Required.
2. Focus on the LATEST state of the discussion, not historical positions that have been superseded.
3. Explicitly flag any direction changes or reversals (e.g., "Originally planned X, but shifted to Y as of [date]").
4. Highlight anything that requires the user's action or decision.
5. Keep the total summary under 200 words.

## Output

Respond ONLY with valid JSON (no markdown, no code fences):
{{
  "topic": "One sentence describing what this thread is about",
  "key_points": [
    "Key decision or development 1",
    "Key decision or development 2",
    "Key decision or development 3"
  ],
  "direction_changes": ["Any shifts in plan or opinion, with dates"],
  "current_status": "What is the latest conclusion or state",
  "action_required": ["Specific actions the user needs to take"],
  "participants_summary": {{"person_name": "Their role/stance in this thread"}}
}}"""
