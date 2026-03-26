"""
Mock email data simulating a Tech Manager's inbox.
Covers diverse scenarios for testing Priority Triage, Action Item Extraction, and Thread Summary.
"""

USER_CONTEXT = {
    "user_name": "Alex Chen",
    "user_role": "Engineering Manager, Platform Team",
    "user_email": "alex.chen@techcorp.com",
    "vip_contacts": [
        "sarah.wong@techcorp.com",   # Direct manager (VP of Engineering)
        "mike.liu@techcorp.com",     # Skip-level (CTO)
    ],
    "calendar_today": [
        {"time": "10:00-10:30", "title": "1:1 with James (Direct Report)", "attendees": ["james.park@techcorp.com"]},
        {"time": "14:00-15:00", "title": "Q2 Planning Review", "attendees": ["sarah.wong@techcorp.com", "david.kim@techcorp.com"]},
        {"time": "16:00-16:30", "title": "Database Migration Go/No-Go", "attendees": ["lisa.zhang@techcorp.com", "ryan.ma@techcorp.com"]},
    ],
    "active_todos": [
        "Finalize Q2 headcount proposal (Due: Friday)",
        "Review database migration rollback plan",
        "Approve Lisa's PTO request",
    ],
}

MOCK_EMAILS = [
    {
        "id": "email_001",
        "from": "sarah.wong@techcorp.com",
        "from_name": "Sarah Wong (VP of Engineering)",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Need your Q2 headcount numbers by EOD",
        "body": (
            "Hi Alex,\n\n"
            "I'm pulling together the Q2 headcount plan for the exec review tomorrow morning. "
            "Can you send me your team's headcount request with justifications by end of day today?\n\n"
            "Please include:\n"
            "- Current team size\n"
            "- Requested new hires (with role descriptions)\n"
            "- Business justification for each\n\n"
            "Thanks,\nSarah"
        ),
        "timestamp": "2025-03-24 08:15:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "act_now",
        "expected_reason": "Direct manager requesting deliverable with EOD deadline",
    },
    {
        "id": "email_002",
        "from": "notifications@github.com",
        "from_name": "GitHub Notifications",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "[platform-core] CI Build #4521 passed",
        "body": (
            "Build #4521 on branch main passed all checks.\n\n"
            "Commit: a1b2c3d - Update dependency versions\n"
            "Author: james.park@techcorp.com\n"
            "Duration: 12m 34s\n\n"
            "View details: https://github.com/techcorp/platform-core/actions/runs/4521"
        ),
        "timestamp": "2025-03-24 07:45:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "Automated CI notification, build passed, no action needed",
    },
    {
        "id": "email_003",
        "from": "lisa.zhang@techcorp.com",
        "from_name": "Lisa Zhang (Senior Engineer, Direct Report)",
        "to": ["alex.chen@techcorp.com"],
        "cc": ["ryan.ma@techcorp.com"],
        "subject": "Re: Database migration — rollback concern",
        "body": (
            "Hi Alex,\n\n"
            "I've been reviewing the migration plan and I'm worried about the rollback strategy. "
            "If the migration fails midway, we could lose 2-3 hours of data because the current "
            "backup window doesn't cover the migration period.\n\n"
            "I think we need to either:\n"
            "1. Schedule an additional backup right before the migration starts\n"
            "2. Implement a point-in-time recovery mechanism\n\n"
            "Can we discuss this before the Go/No-Go meeting at 4pm today? "
            "I'd hate to bring this up without a recommendation.\n\n"
            "Lisa"
        ),
        "timestamp": "2025-03-24 09:30:00",
        "is_reply": True,
        "thread_length": 5,
        "expected_priority": "act_now",
        "expected_reason": "Direct report raising risk before today's Go/No-Go meeting, needs pre-meeting discussion",
    },
    {
        "id": "email_004",
        "from": "hr-updates@techcorp.com",
        "from_name": "HR Communications",
        "to": ["all-engineering@techcorp.com"],
        "cc": [],
        "subject": "Reminder: Open Enrollment Period Ends March 31",
        "body": (
            "Dear Engineering Team,\n\n"
            "This is a reminder that the annual benefits open enrollment period ends on March 31, 2025. "
            "Please review and update your benefits selections in Workday before the deadline.\n\n"
            "Key dates:\n"
            "- Enrollment deadline: March 31, 2025\n"
            "- Changes effective: April 1, 2025\n\n"
            "If you have questions, contact benefits@techcorp.com.\n\n"
            "Best,\nHR Team"
        ),
        "timestamp": "2025-03-24 06:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "HR announcement relevant to user but deadline is a week away, not urgent today",
    },
    {
        "id": "email_005",
        "from": "david.kim@techcorp.com",
        "from_name": "David Kim (PM, Cross-team Peer)",
        "to": ["alex.chen@techcorp.com", "emma.lee@techcorp.com", "kevin.wu@techcorp.com", "nina.patel@techcorp.com"],
        "cc": ["product-updates@techcorp.com"],
        "subject": "Q2 Launch Status Update — Week 12",
        "body": (
            "Hi all,\n\n"
            "Here's the weekly status update for the Q2 launch:\n\n"
            "**On Track:**\n"
            "- Payment integration (Kevin's team) — 90% complete\n"
            "- API documentation (Nina's team) — shipped\n\n"
            "**At Risk:**\n"
            "- Platform migration (Alex's team) — dependency on database migration Go/No-Go\n"
            "- Mobile app update — blocked on design review\n\n"
            "**Action Items:**\n"
            "- Alex: Confirm database migration timeline after today's Go/No-Go meeting\n"
            "- Kevin: Share payment API test results by Wednesday\n"
            "- Nina: Update API changelog for v2.3 changes\n\n"
            "We'll discuss all of this in the Q2 Planning Review at 2pm today.\n\n"
            "David"
        ),
        "timestamp": "2025-03-24 09:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "Status update with action item, but will be discussed in the 2pm meeting — no immediate action needed",
    },
    {
        "id": "email_006",
        "from": "recruiter@talentfirm.com",
        "from_name": "Jessica Taylor (External Recruiter)",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "URGENT: Exclusive Director-level opportunity — respond by TODAY",
        "body": (
            "Hi Alex,\n\n"
            "I came across your profile and I'm incredibly impressed. I have an URGENT Director of Engineering "
            "opportunity at a Series C startup that's perfect for you.\n\n"
            "This role won't last — they're making a decision THIS WEEK. "
            "Please respond TODAY to schedule a confidential conversation.\n\n"
            "Compensation: $280-350K + equity\n\n"
            "Best regards,\nJessica Taylor\nSenior Recruiter, TalentFirm"
        ),
        "timestamp": "2025-03-24 10:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "External recruiter spam using fake urgency signals, not work-related",
    },
    {
        "id": "email_007",
        "from": "james.park@techcorp.com",
        "from_name": "James Park (Junior Engineer, Direct Report)",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Quick question before our 1:1",
        "body": (
            "Hey Alex,\n\n"
            "Before our 1:1 at 10am, wanted to give you a heads up — I've been thinking about "
            "my career growth and I'd like to discuss moving to the ML team. I know this might be "
            "sensitive timing with the migration project, so I wanted you to have time to think about it.\n\n"
            "Also, on a technical note, can you approve my PR #2847 for the config refactor? "
            "It's blocking the staging deploy.\n\n"
            "Thanks,\nJames"
        ),
        "timestamp": "2025-03-24 09:15:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "act_now",
        "expected_reason": "Direct report with career discussion + blocking PR approval, 1:1 is in 45 minutes",
    },
    {
        "id": "email_008",
        "from": "security-alerts@techcorp.com",
        "from_name": "Security Team (Automated)",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "[INFO] Weekly Security Scan Report — No Issues Found",
        "body": (
            "Weekly Security Scan Report\n"
            "========================\n\n"
            "Scan completed: 2025-03-24 03:00 UTC\n"
            "Scope: platform-core, platform-api, platform-worker\n\n"
            "Results: No vulnerabilities found\n"
            "Previous scan: No vulnerabilities found\n\n"
            "This is an automated report. No action required."
        ),
        "timestamp": "2025-03-24 03:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "Automated security scan with no issues found, explicitly states no action required",
    },
    {
        "id": "email_009",
        "from": "emma.lee@techcorp.com",
        "from_name": "Emma Lee (Engineering Manager, Peer)",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Coffee chat this week?",
        "body": (
            "Hey Alex,\n\n"
            "It's been a while since we caught up! Would love to grab coffee this week "
            "and hear how the platform migration is going. I'm also dealing with some similar "
            "challenges on the mobile side.\n\n"
            "Any day works for me — just let me know what's convenient.\n\n"
            "Emma"
        ),
        "timestamp": "2025-03-24 08:30:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "Peer social/networking request, no time pressure, can respond within a few days",
    },
    {
        "id": "email_010",
        "from": "mike.liu@techcorp.com",
        "from_name": "Mike Liu (CTO)",
        "to": ["sarah.wong@techcorp.com"],
        "cc": ["alex.chen@techcorp.com", "david.kim@techcorp.com"],
        "subject": "Re: Q2 strategy alignment",
        "body": (
            "Sarah,\n\n"
            "Thanks for the update. I'm generally aligned with the plan but have one concern — "
            "the platform migration timeline feels aggressive given the current team size. "
            "Alex, can you put together a risk assessment with mitigation options? "
            "I'd like to see it before the board meeting next Tuesday.\n\n"
            "Also, let's make sure we have a rollback plan that the board will be comfortable with.\n\n"
            "Mike"
        ),
        "timestamp": "2025-03-24 10:30:00",
        "is_reply": True,
        "thread_length": 8,
        "expected_priority": "act_now",
        "expected_reason": "CTO (VIP) directly asking user for a deliverable (risk assessment) with deadline (before Tuesday)",
    },
    {
        "id": "email_011",
        "from": "lisa.zhang@techcorp.com",
        "from_name": "Lisa Zhang (Senior Engineer, Direct Report)",
        "to": ["alex.chen@techcorp.com"],
        "cc": ["ryan.ma@techcorp.com"],
        "subject": "FYI: Rollback plan v3 is ready for review",
        "body": (
            "Hi Alex,\n\n"
            "Just a heads up — I've uploaded the final rollback plan (v3) to Confluence. "
            "Ryan already reviewed the scripts section and signed off.\n\n"
            "No rush, but would be good if you could skim through it before the Go/No-Go meeting. "
            "The link is in the doc: [Confluence link]\n\n"
            "Let me know if you have any questions.\n\n"
            "Lisa"
        ),
        "timestamp": "2025-03-24 11:15:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "FYI from direct report, review requested but not urgent — can be done before the meeting",
    },
    {
        "id": "email_012",
        "from": "kevin.wu@techcorp.com",
        "from_name": "Kevin Wu (Engineering Manager, Payments Team)",
        "to": ["alex.chen@techcorp.com", "david.kim@techcorp.com"],
        "cc": ["nina.patel@techcorp.com", "emma.lee@techcorp.com"],
        "subject": "Re: API versioning strategy — we need to align",
        "body": (
            "Alex, David,\n\n"
            "After a week of back and forth I think we're converging. Here's my understanding:\n\n"
            "✅ Agreed:\n"
            "- v2 endpoints use the new schema\n"
            "- v1 stays alive for 6 months (deprecation period)\n"
            "- Mobile gets early access to v2 /payments and /auth\n\n"
            "❓ Still open:\n"
            "- Who owns the v1→v2 migration guide for external partners? Nina says her team is at capacity.\n"
            "- Rate limiting on v2 — Alex, your platform team controls this. Can we do 1000 req/s per partner initially?\n\n"
            "I need answers on both by Wednesday so I can update the partner communication plan.\n\n"
            "Kevin\n\n"
            "---- Replied Message ----\n"
            "From    David Kim <david.kim@techcorp.com>\n"
            "Date    03/23/2025 11:30\n"
            "To      <kevin.wu@techcorp.com>, <alex.chen@techcorp.com>\n"
            "Cc      <nina.patel@techcorp.com>, <emma.lee@techcorp.com>\n"
            "Subject Re: API versioning strategy — we need to align\n\n"
            "I'm fine with 6 months deprecation. But the migration guide is critical — we can't "
            "just deprecate without giving partners a clear path. Nina, is there anyone on your team "
            "who can at least draft the outline?\n\n"
            "David\n\n"
            "---- Replied Message ----\n"
            "From    Nina Patel <nina.patel@techcorp.com>\n"
            "Date    03/22/2025 15:00\n"
            "To      <kevin.wu@techcorp.com>, <alex.chen@techcorp.com>, <david.kim@techcorp.com>\n"
            "Subject Re: API versioning strategy — we need to align\n\n"
            "My team just shipped the v2.3 changelog and we're now heads-down on the developer portal "
            "redesign. I genuinely don't have bandwidth for a migration guide right now. Can we push it to April?\n\n"
            "Nina\n\n"
            "---- Replied Message ----\n"
            "From    Alex Chen <alex.chen@techcorp.com>\n"
            "Date    03/22/2025 10:15\n"
            "To      <kevin.wu@techcorp.com>, <david.kim@techcorp.com>\n"
            "Cc      <nina.patel@techcorp.com>, <emma.lee@techcorp.com>\n"
            "Subject Re: API versioning strategy — we need to align\n\n"
            "Re: deprecation timeline — I think 6 months is reasonable. 3 months is too aggressive "
            "given how many external partners rely on v1.\n\n"
            "For rate limiting, let me check what the current infrastructure can handle. "
            "I'll have numbers by next week.\n\n"
            "Alex\n\n"
            "---- Replied Message ----\n"
            "From    Kevin Wu <kevin.wu@techcorp.com>\n"
            "Date    03/21/2025 09:00\n"
            "To      <alex.chen@techcorp.com>, <david.kim@techcorp.com>\n"
            "Cc      <nina.patel@techcorp.com>, <emma.lee@techcorp.com>\n"
            "Subject API versioning strategy — we need to align\n\n"
            "Hey all, we need to get on the same page about the API versioning strategy.\n"
            "Current situation: v1 is live, v2 is in beta, and mobile team needs v2 endpoints ASAP.\n\n"
            "Questions we need to answer:\n"
            "1. How long do we keep v1 alive?\n"
            "2. Who writes the migration guide?\n"
            "3. What are the rate limits for v2?\n\n"
            "Kevin"
        ),
        "timestamp": "2025-03-24 10:45:00",
        "is_reply": True,
        "thread_length": 5,
        "expected_priority": "later",
        "expected_reason": "Cross-team alignment thread, Wednesday deadline gives buffer, not urgent today",
    },
    {
        "id": "email_013",
        "from": "learning@techcorp.com",
        "from_name": "TechCorp Learning & Development",
        "to": ["all-managers@techcorp.com"],
        "cc": [],
        "subject": "New course available: 'Leading Through Organizational Change'",
        "body": (
            "Hi Managers,\n\n"
            "We're excited to announce a new course on our learning platform:\n\n"
            "📚 Leading Through Organizational Change\n"
            "Instructor: Dr. Karen Mitchell\n"
            "Duration: 4 hours (self-paced)\n"
            "Deadline to complete: April 30, 2025\n\n"
            "This course covers:\n"
            "- Communicating change effectively to your team\n"
            "- Managing resistance and building buy-in\n"
            "- Supporting team members through transitions\n"
            "- Measuring change adoption success\n\n"
            "Start the course: https://learn.techcorp.com/courses/leading-change\n\n"
            "Best,\nL&D Team"
        ),
        "timestamp": "2025-03-24 07:15:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "Mass email to all managers about optional training course, April 30 deadline, not urgent",
    },
    {
        "id": "email_014",
        "from": "ryan.ma@techcorp.com",
        "from_name": "Ryan Ma (Staff Engineer)",
        "to": ["alex.chen@techcorp.com", "lisa.zhang@techcorp.com"],
        "cc": [],
        "subject": "Re: Staging environment issues — resolved (mostly)",
        "body": (
            "Alex, Lisa,\n\n"
            "Good news: the staging DB replication lag is fixed. Root cause was a misconfigured "
            "connection pool — I've documented it in the incident log.\n\n"
            "However, I noticed something else while debugging: our staging environment is running "
            "PostgreSQL 14.2 but production is on 15.1. This version mismatch could cause subtle "
            "behavior differences during migration testing. Not urgent, but we should probably "
            "upgrade staging before the Go/No-Go.\n\n"
            "I can handle the upgrade tonight if you give me the green light. Downtime would be "
            "~20 minutes.\n\n"
            "Ryan\n\n"
            "---- Replied Message ----\n"
            "From    Alex Chen <alex.chen@techcorp.com>\n"
            "Date    03/23/2025 15:30\n"
            "To      <ryan.ma@techcorp.com>, <lisa.zhang@techcorp.com>\n"
            "Subject Re: Staging environment issues\n\n"
            "Ryan, any update on the staging issues? We need staging stable for the migration rehearsal.\n\n"
            "Alex\n\n"
            "---- Replied Message ----\n"
            "From    Lisa Zhang <lisa.zhang@techcorp.com>\n"
            "Date    03/23/2025 10:15\n"
            "To      <alex.chen@techcorp.com>, <ryan.ma@techcorp.com>\n"
            "Subject Re: Staging environment issues\n\n"
            "I'm seeing intermittent failures in my migration test runs. Staging DB seems to have "
            "replication lag — some queries return stale data. Ryan, can you look into this?\n\n"
            "Lisa\n\n"
            "---- Replied Message ----\n"
            "From    Ryan Ma <ryan.ma@techcorp.com>\n"
            "Date    03/22/2025 17:00\n"
            "To      <alex.chen@techcorp.com>, <lisa.zhang@techcorp.com>\n"
            "Subject Staging environment issues\n\n"
            "Heads up: I'm seeing some weird behavior in staging. Writes to the primary are taking "
            "2-3 seconds to replicate. Going to investigate tomorrow.\n\n"
            "Ryan"
        ),
        "timestamp": "2025-03-24 12:00:00",
        "is_reply": True,
        "thread_length": 4,
        "expected_priority": "later",
        "expected_reason": "Staging issue resolved, PG version upgrade is optional and can wait — not blocking Go/No-Go",
    },
    # --- External marketing / spam / newsletter emails ---
    {
        "id": "email_015",
        "from": "marketing@cloudplatform.io",
        "from_name": "CloudPlatform Marketing",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "🚀 Limited Time: 50% off Enterprise Plan — Ends Friday!",
        "body": (
            "Hi Alex,\n\n"
            "You're missing out! For a limited time, get 50% off our Enterprise Plan.\n\n"
            "✅ Unlimited API calls\n"
            "✅ 99.99% uptime SLA\n"
            "✅ Priority support\n"
            "✅ Custom integrations\n\n"
            "This offer expires THIS FRIDAY. Don't wait!\n\n"
            "👉 Claim your discount: https://cloudplatform.io/enterprise-deal\n\n"
            "Best,\nThe CloudPlatform Team\n\n"
            "---\n"
            "You're receiving this because you signed up for CloudPlatform updates.\n"
            "Unsubscribe: https://cloudplatform.io/unsubscribe"
        ),
        "timestamp": "2025-03-24 06:30:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "External marketing email with promotional content, not work-related",
    },
    {
        "id": "email_016",
        "from": "noreply@jira.techcorp.com",
        "from_name": "Jira (Automated)",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "[PLAT-1234] Bug: API timeout on /v2/payments endpoint — Assigned to you",
        "body": (
            "Alex Chen, a Jira issue has been assigned to you.\n\n"
            "Project: Platform Core (PLAT)\n"
            "Issue: PLAT-1234\n"
            "Type: Bug\n"
            "Priority: Critical\n"
            "Reporter: Kevin Wu\n"
            "Assignee: Alex Chen\n\n"
            "Description:\n"
            "The /v2/payments endpoint is intermittently timing out under load. "
            "Response times spike to 30s+ when concurrent requests exceed 200. "
            "This is blocking the payments team's integration testing.\n\n"
            "Steps to reproduce:\n"
            "1. Run load test with 200+ concurrent requests\n"
            "2. Observe timeout errors on /v2/payments\n\n"
            "Expected: Response time < 500ms\n"
            "Actual: Response time > 30s (timeout)\n\n"
            "View issue: https://jira.techcorp.com/browse/PLAT-1234"
        ),
        "timestamp": "2025-03-24 09:45:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "Jira bug assigned to user, critical but can be triaged — not a live production outage",
    },
    {
        "id": "email_017",
        "from": "newsletter@techweekly.com",
        "from_name": "Tech Weekly Newsletter",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "This Week in Tech: OpenAI's New Model, Kubernetes 1.30, and the Rise of Rust",
        "body": (
            "TECH WEEKLY — March 24, 2025\n"
            "================================\n\n"
            "Top Stories This Week:\n\n"
            "1. OpenAI Launches GPT-5 with Native Tool Use\n"
            "   OpenAI released GPT-5 this week with built-in tool use capabilities...\n\n"
            "2. Kubernetes 1.30 Released with Sidecar Containers GA\n"
            "   The long-awaited sidecar containers feature is now generally available...\n\n"
            "3. Why Rust Is Replacing C++ in Systems Programming\n"
            "   A new survey shows 40% of systems teams are adopting Rust...\n\n"
            "4. AWS Announces 30% Price Cut on Lambda\n"
            "   Serverless just got cheaper...\n\n"
            "Read more: https://techweekly.com/issue/2025-w13\n\n"
            "You're subscribed to Tech Weekly. Unsubscribe: https://techweekly.com/unsub"
        ),
        "timestamp": "2025-03-24 05:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "Newsletter subscription, informational only, no action required",
    },
    {
        "id": "email_018",
        "from": "noreply@slack.com",
        "from_name": "Slack Notification",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "You have 12 unread messages in #platform-incidents",
        "body": (
            "Hi Alex,\n\n"
            "You have unread messages in channels you follow:\n\n"
            "#platform-incidents (12 new)\n"
            "  - ryan.ma: \"Staging DB replication lag resolved ✅\"\n"
            "  - lisa.zhang: \"Migration rehearsal dry-run passed on attempt 2\"\n"
            "  - bot: \"Alert resolved: CPU usage back to normal on staging-worker-03\"\n"
            "  ... and 9 more messages\n\n"
            "#platform-general (5 new)\n"
            "  - james.park: \"PR #2847 is ready for re-review\"\n"
            "  - emma.lee: \"Anyone know the zoom link for the Go/No-Go meeting?\"\n"
            "  ... and 3 more messages\n\n"
            "View in Slack: https://techcorp.slack.com\n\n"
            "Manage notification settings: https://slack.com/settings/notifications"
        ),
        "timestamp": "2025-03-24 11:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "Slack digest notification, relevant context about incidents and PRs but not directly actionable via email",
    },
    {
        "id": "email_019",
        "from": "noreply@pagerduty.com",
        "from_name": "PagerDuty Alert",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "🔴 [TRIGGERED] High Error Rate on platform-api-prod (>5% 5xx)",
        "body": (
            "INCIDENT TRIGGERED\n"
            "==================\n\n"
            "Service: platform-api-prod\n"
            "Alert: High Error Rate\n"
            "Severity: Critical\n"
            "Triggered at: 2025-03-24 11:42:00 UTC\n\n"
            "Details:\n"
            "5xx error rate exceeded 5% threshold.\n"
            "Current rate: 8.3%\n"
            "Affected endpoints: /v2/payments, /v2/auth\n"
            "Duration: 12 minutes and counting\n\n"
            "On-call: Ryan Ma (primary), Alex Chen (secondary)\n\n"
            "Acknowledge: https://pagerduty.com/incidents/P12345/ack\n"
            "Resolve: https://pagerduty.com/incidents/P12345/resolve\n"
            "View Dashboard: https://grafana.techcorp.com/d/api-errors"
        ),
        "timestamp": "2025-03-24 11:42:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "act_now",
        "expected_reason": "Production incident alert, user is secondary on-call, critical severity with active impact",
    },
    {
        "id": "email_020",
        "from": "events@oreilly.com",
        "from_name": "O'Reilly Media",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Invitation: O'Reilly Software Architecture Conference 2025 — Early Bird Pricing",
        "body": (
            "Hi Alex,\n\n"
            "You're invited to the O'Reilly Software Architecture Conference 2025!\n\n"
            "📅 June 15-17, 2025 | San Jose Convention Center\n\n"
            "Featured sessions:\n"
            "- \"Scaling Microservices at Netflix\" — Casey Rosenthal\n"
            "- \"Platform Engineering: Build vs Buy\" — Kelsey Hightower\n"
            "- \"AI-Assisted Code Review in Practice\" — Panel Discussion\n\n"
            "Early bird pricing: $999 (regular $1,499) — ends April 15.\n\n"
            "Register now: https://oreilly.com/arch-conf-2025\n\n"
            "Use code TECHLEADER25 for an additional 10% off.\n\n"
            "Hope to see you there!\n"
            "O'Reilly Events Team"
        ),
        "timestamp": "2025-03-24 07:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "Conference marketing email, promotional with early bird pricing, no urgent action",
    },
    {
        "id": "email_021",
        "from": "noreply@github.com",
        "from_name": "GitHub Notifications",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "[platform-core] PR #2847: Config refactor — Review requested",
        "body": (
            "james.park requested your review on pull request #2847.\n\n"
            "platform-core / Config refactor — simplify environment management\n\n"
            "Changes:\n"
            "- Consolidated 3 config files into 1 unified config.yaml\n"
            "- Added environment variable override support\n"
            "- Removed deprecated config_legacy.py\n"
            "- Added unit tests for config parsing\n\n"
            "+342 −189 across 12 files\n\n"
            "Reviewers: @alex.chen (requested)\n"
            "Labels: refactor, config, ready-for-review\n\n"
            "View PR: https://github.com/techcorp/platform-core/pull/2847"
        ),
        "timestamp": "2025-03-24 09:20:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "PR review request from direct report, important but not time-critical today",
    },
    {
        "id": "email_022",
        "from": "no-reply@linkedin.com",
        "from_name": "LinkedIn",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Alex, you have 8 new connection requests and 3 messages",
        "body": (
            "Hi Alex,\n\n"
            "Here's what's happening on LinkedIn:\n\n"
            "🔗 8 new connection requests\n"
            "  - Jessica Taylor (Senior Recruiter at TalentFirm)\n"
            "  - Mark Johnson (VP Engineering at StartupXYZ)\n"
            "  - ... and 6 others\n\n"
            "💬 3 new messages\n"
            "  - David Park: \"Great article on platform engineering!\"\n"
            "  - Recruiter: \"Exciting opportunity at Google...\"\n"
            "  - Stanford Alumni: \"Upcoming networking event in SF\"\n\n"
            "View on LinkedIn: https://linkedin.com/notifications\n\n"
            "You're receiving LinkedIn notification emails.\n"
            "Unsubscribe: https://linkedin.com/settings/email"
        ),
        "timestamp": "2025-03-24 07:30:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "LinkedIn digest notification, social networking, not work-related",
    },
    {
        "id": "email_023",
        "from": "noreply@datadog.com",
        "from_name": "Datadog Monitor",
        "to": ["platform-team@techcorp.com"],
        "cc": [],
        "subject": "[Recovered] Memory usage on platform-worker-05 back to normal",
        "body": (
            "Monitor Status: Recovered ✅\n\n"
            "Monitor: High Memory Usage — platform-worker-05\n"
            "Group: platform-worker-05\n\n"
            "Previous status: ALERT (triggered 2025-03-24 02:15 UTC)\n"
            "Current status: OK (recovered 2025-03-24 04:30 UTC)\n\n"
            "Duration of alert: 2h 15m\n\n"
            "Current value: 62% memory usage\n"
            "Threshold: >85%\n"
            "Peak during alert: 91%\n\n"
            "Root cause: Nightly batch job consumed extra memory due to larger-than-usual dataset.\n"
            "No action required — job completed successfully and memory was released.\n\n"
            "Dashboard: https://app.datadoghq.com/monitors/platform-workers"
        ),
        "timestamp": "2025-03-24 04:30:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "Monitoring alert already recovered, explicitly states no action required",
    },
    {
        "id": "email_024",
        "from": "aws-notifications@amazon.com",
        "from_name": "AWS Billing",
        "to": ["alex.chen@techcorp.com"],
        "cc": ["finance@techcorp.com"],
        "subject": "AWS Cost Alert: Your March spending is 20% over budget",
        "body": (
            "Hello,\n\n"
            "This is an automated alert from AWS Cost Management.\n\n"
            "Account: techcorp-production (123456789)\n"
            "Budget: Platform Team — Monthly ($45,000)\n"
            "Current spend: $37,800 (84% of budget)\n"
            "Forecasted end-of-month: $54,200 (120% of budget)\n\n"
            "Top cost drivers this month:\n"
            "1. EC2 Instances: $18,200 (+15% vs last month)\n"
            "2. RDS: $8,900 (+32% — likely due to staging DB scaling)\n"
            "3. S3: $4,100 (normal)\n"
            "4. Lambda: $3,200 (+8%)\n\n"
            "Recommended actions:\n"
            "- Review staging environment sizing\n"
            "- Check for unused EC2 instances\n"
            "- Consider Reserved Instances for stable workloads\n\n"
            "View full report: https://console.aws.amazon.com/cost-management\n\n"
            "This is an automated notification. Do not reply to this email."
        ),
        "timestamp": "2025-03-24 08:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "AWS billing alert with budget overage, relevant but not urgent today — needs review this week",
    },
    {
        "id": "email_025",
        "from": "confluence-noreply@techcorp.com",
        "from_name": "Confluence (Automated)",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Weekly digest: 5 pages updated in Platform Team space",
        "body": (
            "Here's your weekly digest for the Platform Team space:\n\n"
            "Updated pages:\n"
            "1. Database Migration Rollback Plan v3 — Lisa Zhang (3 edits)\n"
            "2. Q2 OKRs — David Kim (1 edit)\n"
            "3. On-call Runbook — Ryan Ma (2 edits)\n"
            "4. Team Norms & Working Agreements — Alex Chen (1 edit)\n"
            "5. Platform Architecture Overview — Lisa Zhang (1 edit)\n\n"
            "View all updates: https://confluence.techcorp.com/spaces/PLAT\n\n"
            "Manage notifications: https://confluence.techcorp.com/settings/notifications"
        ),
        "timestamp": "2025-03-24 06:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "Automated Confluence weekly digest, informational only, no action required",
    },
    {
        "id": "email_026",
        "from": "promotions@saas-tools.com",
        "from_name": "SaaS Tools Weekly",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "The 10 Best DevOps Tools of 2025 — Free Report Inside",
        "body": (
            "Hi Alex,\n\n"
            "We've just released our annual report on the top DevOps tools!\n\n"
            "Download your FREE copy:\n"
            "📥 https://saas-tools.com/devops-2025-report\n\n"
            "What's inside:\n"
            "- Comparison of 50+ CI/CD platforms\n"
            "- ROI calculator for DevOps investments\n"
            "- Expert interviews with CTOs from Stripe, Airbnb, and Netflix\n"
            "- 2025 trends: AI-powered testing, platform engineering, and more\n\n"
            "\"This report saved us $200K in tool sprawl\" — VP Eng, Fortune 500 company\n\n"
            "Download now — available for a limited time.\n\n"
            "SaaS Tools Weekly\n"
            "Unsubscribe: https://saas-tools.com/unsubscribe"
        ),
        "timestamp": "2025-03-24 06:15:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "External marketing email promoting a report download, not work-related",
    },
    {
        "id": "email_027",
        "from": "noreply@sentry.io",
        "from_name": "Sentry Alert",
        "to": ["platform-team@techcorp.com"],
        "cc": [],
        "subject": "[platform-api] New issue: NullPointerException in PaymentProcessor.validateCard()",
        "body": (
            "New Issue in platform-api\n"
            "========================\n\n"
            "NullPointerException: cardToken is null\n"
            "  at PaymentProcessor.validateCard(PaymentProcessor.java:142)\n"
            "  at PaymentController.processPayment(PaymentController.java:87)\n"
            "  at RequestHandler.handle(RequestHandler.java:34)\n\n"
            "First seen: 2025-03-24 10:30 UTC\n"
            "Events: 47 in the last hour\n"
            "Users affected: 23\n\n"
            "Environment: production\n"
            "Release: v2.3.1\n"
            "Browser: Chrome 122, Safari 17\n\n"
            "View issue: https://sentry.io/techcorp/platform-api/issues/98765/\n\n"
            "Unsubscribe from these alerts: https://sentry.io/settings/notifications"
        ),
        "timestamp": "2025-03-24 10:30:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "Sentry error alert sent to team, not assigned to user specifically, moderate user impact",
    },
    {
        "id": "email_028",
        "from": "it-admin@techcorp.com",
        "from_name": "IT Admin (Automated)",
        "to": ["all-staff@techcorp.com"],
        "cc": [],
        "subject": "Scheduled maintenance: VPN will be unavailable Saturday 2am-6am",
        "body": (
            "Dear TechCorp Staff,\n\n"
            "Planned maintenance notification:\n\n"
            "What: VPN infrastructure upgrade\n"
            "When: Saturday, March 29, 2:00 AM — 6:00 AM PDT\n"
            "Impact: VPN access will be unavailable during this window\n"
            "Duration: ~4 hours\n\n"
            "What you need to do:\n"
            "- Save any remote work before 2:00 AM Saturday\n"
            "- No VPN access during the maintenance window\n"
            "- VPN will automatically reconnect after maintenance is complete\n\n"
            "If you need emergency access during this time, contact IT on-call: +1-555-0199\n\n"
            "We apologize for the inconvenience.\n\n"
            "IT Operations Team"
        ),
        "timestamp": "2025-03-24 10:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "IT maintenance notice for Saturday, relevant to be aware of but not actionable today",
    },
    {
        "id": "email_029",
        "from": "noreply@zoom.us",
        "from_name": "Zoom",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Cloud Recording Available: Q2 Planning Review (03/23)",
        "body": (
            "Hi Alex Chen,\n\n"
            "Your cloud recording is now available.\n\n"
            "Meeting: Q2 Planning Review\n"
            "Date: March 23, 2025 2:00 PM PDT\n"
            "Duration: 58 min\n"
            "Host: Sarah Wong\n\n"
            "Recording links:\n"
            "🎥 Video: https://zoom.us/rec/share/abc123\n"
            "📝 Transcript: https://zoom.us/rec/transcript/abc123\n\n"
            "This recording will be available for 30 days.\n\n"
            "Best,\nZoom Team"
        ),
        "timestamp": "2025-03-24 08:45:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "Automated Zoom recording notification, informational only",
    },
    {
        "id": "email_030",
        "from": "vendor@dbconsulting.com",
        "from_name": "Tom Harris (DB Consulting Inc.)",
        "to": ["alex.chen@techcorp.com"],
        "cc": ["procurement@techcorp.com"],
        "subject": "Re: Database Migration Support — Proposal Attached",
        "body": (
            "Hi Alex,\n\n"
            "Thanks for the call last week. As discussed, please find attached our proposal for "
            "database migration consulting support.\n\n"
            "Summary:\n"
            "- Scope: PostgreSQL 14→15 migration assistance + performance tuning\n"
            "- Team: 2 senior DBAs, on-site for 3 weeks\n"
            "- Timeline: April 1 — April 18\n"
            "- Cost: $48,000 (includes after-hours support during migration window)\n\n"
            "Key deliverables:\n"
            "1. Migration runbook review and validation\n"
            "2. Performance baseline and tuning\n"
            "3. On-call support during migration weekend\n"
            "4. Post-migration health check\n\n"
            "I'll need a signed SOW by this Friday if you want us to start April 1. "
            "Happy to jump on a quick call if you have questions.\n\n"
            "Best regards,\n"
            "Tom Harris\nSenior Consultant, DB Consulting Inc.\n"
            "+1-555-0142\n\n"
            "---- Replied Message ----\n"
            "From    Alex Chen <alex.chen@techcorp.com>\n"
            "Date    03/19/2025 14:00\n"
            "To      <vendor@dbconsulting.com>\n"
            "Cc      <procurement@techcorp.com>\n"
            "Subject Database Migration Support\n\n"
            "Hi Tom,\n\n"
            "Thanks for the intro from Sarah. We're planning a major database migration "
            "in April and could use some expert support. Could you put together a proposal "
            "for 2-3 weeks of DBA consulting?\n\n"
            "Happy to discuss details on a call.\n\n"
            "Alex"
        ),
        "timestamp": "2025-03-24 09:50:00",
        "is_reply": True,
        "thread_length": 2,
        "expected_priority": "later",
        "expected_reason": "Vendor proposal reply, relevant to migration project, Friday deadline for SOW but not urgent today",
    },
    {
        "id": "email_031",
        "from": "noreply@greenhouse.io",
        "from_name": "Greenhouse (Recruiting)",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Interview reminder: Backend Engineer candidate tomorrow at 11am",
        "body": (
            "Hi Alex,\n\n"
            "Reminder: You have an interview scheduled for tomorrow.\n\n"
            "Candidate: Priya Sharma\n"
            "Position: Backend Engineer (Platform Team)\n"
            "Time: March 25, 2025 at 11:00 AM PDT\n"
            "Duration: 45 minutes\n"
            "Type: Technical — System Design\n"
            "Location: Zoom (link below)\n\n"
            "Zoom link: https://zoom.us/j/987654321\n\n"
            "Interview kit: https://greenhouse.io/interview-kit/12345\n\n"
            "Please review the candidate's resume and the interview kit before the session.\n\n"
            "Thanks,\nRecruiting Team"
        ),
        "timestamp": "2025-03-24 08:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "Interview reminder for tomorrow, needs prep but not urgent right now",
    },
    {
        "id": "email_032",
        "from": "noreply@medium.com",
        "from_name": "Medium Daily Digest",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Today's top picks for you: Platform Engineering, Distributed Systems",
        "body": (
            "Good morning, Alex!\n\n"
            "Here are today's recommended reads based on your interests:\n\n"
            "1. 'How We Migrated 50TB of Data with Zero Downtime' — by Uber Engineering\n"
            "   A deep dive into Uber's database migration strategy...\n"
            "   ⭐ 2.4K claps · 8 min read\n\n"
            "2. 'The Manager's Guide to Technical Debt' — by Will Larson\n"
            "   Why technical debt is a leadership problem, not just a code problem...\n"
            "   ⭐ 1.8K claps · 12 min read\n\n"
            "3. 'Kubernetes at Scale: Lessons from Running 10,000 Pods' — by Shopify\n"
            "   Practical lessons from Shopify's platform team...\n"
            "   ⭐ 3.1K claps · 15 min read\n\n"
            "Read more on Medium: https://medium.com/feed/alex-chen\n\n"
            "Unsubscribe: https://medium.com/settings/notifications"
        ),
        "timestamp": "2025-03-24 05:30:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "Medium content digest, purely informational reading material",
    },
    {
        "id": "email_033",
        "from": "expenses@techcorp.com",
        "from_name": "Expense System (Automated)",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Action needed: 2 expense reports from your team awaiting approval",
        "body": (
            "Hi Alex,\n\n"
            "You have pending expense reports to approve:\n\n"
            "1. Lisa Zhang — $342.00\n"
            "   Description: AWS re:Invent conference travel (booked in advance)\n"
            "   Submitted: March 22, 2025\n\n"
            "2. James Park — $89.50\n"
            "   Description: Team lunch (March 20)\n"
            "   Submitted: March 23, 2025\n\n"
            "Please approve or reject within 5 business days.\n\n"
            "Approve expenses: https://expenses.techcorp.com/pending\n\n"
            "This is an automated notification from the expense management system."
        ),
        "timestamp": "2025-03-24 07:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "later",
        "expected_reason": "Expense approvals from direct reports, should be done within 5 days but not urgent today",
    },
    {
        "id": "email_034",
        "from": "noreply@google.com",
        "from_name": "Google Workspace",
        "to": ["alex.chen@techcorp.com"],
        "cc": [],
        "subject": "Your Google Workspace storage is 85% full",
        "body": (
            "Hi Alex,\n\n"
            "Your Google Workspace storage is almost full.\n\n"
            "Used: 12.8 GB of 15 GB (85%)\n\n"
            "Breakdown:\n"
            "- Google Drive: 8.2 GB\n"
            "- Gmail: 3.9 GB\n"
            "- Google Photos: 0.7 GB\n\n"
            "What you can do:\n"
            "- Delete large files in Google Drive\n"
            "- Empty your Gmail trash and spam\n"
            "- Request a storage upgrade from IT\n\n"
            "Manage storage: https://one.google.com/storage\n\n"
            "Google Workspace Team"
        ),
        "timestamp": "2025-03-24 04:00:00",
        "is_reply": False,
        "thread_length": 1,
        "expected_priority": "ignore",
        "expected_reason": "Automated storage warning, not urgent, can address anytime",
    },
]

LONG_THREAD_EXAMPLE = {
    "id": "thread_001",
    "subject": "Re: Q2 Platform Migration — Timeline Discussion",
    "participants": [
        "alex.chen@techcorp.com",
        "lisa.zhang@techcorp.com",
        "ryan.ma@techcorp.com",
        "david.kim@techcorp.com",
        "sarah.wong@techcorp.com",
    ],
    "messages": [
        {
            "from": "david.kim@techcorp.com",
            "timestamp": "2025-03-20 10:00:00",
            "body": "Team, we need to finalize the Q2 platform migration timeline. Current plan is to start April 1 and complete by April 30. Any concerns?"
        },
        {
            "from": "lisa.zhang@techcorp.com",
            "timestamp": "2025-03-20 10:30:00",
            "body": "April 1 start is doable, but April 30 completion is tight. The database migration alone needs 2 weeks of testing. I'd suggest we push completion to May 15."
        },
        {
            "from": "ryan.ma@techcorp.com",
            "timestamp": "2025-03-20 11:00:00",
            "body": "Agree with Lisa. Also, we haven't accounted for the API versioning work. That's another week. May 15 seems more realistic."
        },
        {
            "from": "alex.chen@techcorp.com",
            "timestamp": "2025-03-20 14:00:00",
            "body": "I hear the concerns. Let me check with Sarah on whether May 15 works for the broader Q2 timeline. If it does, let's go with that."
        },
        {
            "from": "sarah.wong@techcorp.com",
            "timestamp": "2025-03-21 09:00:00",
            "body": "May 15 is acceptable for the migration itself, but the customer-facing features that depend on it need to ship by May 31. So we have zero buffer. Make sure the rollback plan is solid."
        },
        {
            "from": "alex.chen@techcorp.com",
            "timestamp": "2025-03-21 10:00:00",
            "body": "Understood. Lisa, can you own the rollback plan? Target: have it reviewed before the Go/No-Go meeting on March 24 (Monday)."
        },
        {
            "from": "lisa.zhang@techcorp.com",
            "timestamp": "2025-03-21 11:00:00",
            "body": "On it. I'll have a draft ready by Friday EOD for review over the weekend."
        },
        {
            "from": "david.kim@techcorp.com",
            "timestamp": "2025-03-22 15:00:00",
            "body": "Update: I just heard from the mobile team that they need the new API endpoints by May 10, not May 31. This changes things — if migration doesn't finish by May 10, mobile launch slips to Q3."
        },
        {
            "from": "alex.chen@techcorp.com",
            "timestamp": "2025-03-22 16:00:00",
            "body": "That's a significant change. We need to either: (1) accelerate the migration by adding 2 contractors, or (2) provide a partial API migration that gives mobile what they need by May 10 while we complete the full migration by May 15."
        },
        {
            "from": "sarah.wong@techcorp.com",
            "timestamp": "2025-03-23 09:00:00",
            "body": "Option 2 (partial API first) sounds more pragmatic. Alex, can you scope what 'partial API migration' looks like and present it at Monday's Go/No-Go? I want to make a decision there."
        },
        {
            "from": "alex.chen@techcorp.com",
            "timestamp": "2025-03-23 10:00:00",
            "body": "Will do. Lisa and Ryan, let's sync at 3pm today to figure out which API endpoints mobile needs first and what it takes to migrate those separately."
        },
        {
            "from": "lisa.zhang@techcorp.com",
            "timestamp": "2025-03-23 18:00:00",
            "body": "Just finished the sync with Ryan. Here's what we found:\n\n- Mobile needs 4 endpoints: /users, /payments, /notifications, /auth\n- These 4 can be migrated independently in ~1 week\n- Full migration still needs the May 15 timeline\n- Rollback plan draft is ready for review: [link]\n\nRecommendation: Go with Option 2. Start partial migration April 1, target completion April 8. Then proceed with full migration through May 15."
        },
    ]
}
