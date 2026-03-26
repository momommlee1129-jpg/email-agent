"""
Evaluation dry-run: Run 10 test cases against the prototype and record results.
Usage: python -m eval.run_eval
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mock_emails import MOCK_EMAILS, LONG_THREAD_EXAMPLE, USER_CONTEXT
from src.agent import classify_priority, extract_action_items, summarize_thread


def run_priority_eval():
    print("=" * 70)
    print("EVALUATION: Priority Classification")
    print("=" * 70)

    results = []
    for email in MOCK_EMAILS:
        print(f"\nClassifying: {email['subject'][:60]}...")
        result = classify_priority(email, USER_CONTEXT)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
            results.append({"email_id": email["id"], "error": result["error"]})
            continue

        predicted = result.get("priority", "unknown")
        expected = email.get("expected_priority", "unknown")
        correct = predicted == expected

        print(f"  Expected: {expected} | Predicted: {predicted} | {'✅' if correct else '❌'}")
        print(f"  Confidence: {result.get('confidence', 'N/A')}")
        print(f"  Reasons: {result.get('reasons', [])}")

        results.append({
            "email_id": email["id"],
            "subject": email["subject"],
            "expected": expected,
            "predicted": predicted,
            "confidence": result.get("confidence"),
            "correct": correct,
            "reasons": result.get("reasons", []),
        })

    correct_count = sum(1 for r in results if r.get("correct", False))
    total = len(results)
    error_count = sum(1 for r in results if "error" in r and "correct" not in r)

    print("\n" + "=" * 70)
    print(f"RESULTS: {correct_count}/{total - error_count} correct ({correct_count/(total-error_count)*100:.0f}% accuracy)")
    print(f"Errors: {error_count}")

    act_now_expected = [e for e in MOCK_EMAILS if e.get("expected_priority") == "act_now"]
    critical_misses = 0
    for e in act_now_expected:
        r = next((x for x in results if x.get("email_id") == e["id"]), None)
        if r and r.get("predicted") == "ignore":
            critical_misses += 1
    print(f"Critical Miss Rate (Act Now → Ignore): {critical_misses}/{len(act_now_expected)}")

    return results


def run_action_item_eval():
    print("\n" + "=" * 70)
    print("EVALUATION: Action Item Extraction")
    print("=" * 70)

    test_emails = [e for e in MOCK_EMAILS if e.get("expected_priority") == "act_now"][:3]

    for email in test_emails:
        print(f"\nExtracting from: {email['subject'][:60]}...")
        result = extract_action_items(email, USER_CONTEXT)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
            continue

        items = result.get("action_items", [])
        print(f"  Found {len(items)} action item(s):")
        for item in items:
            print(f"    - [{item.get('urgency', '?')}] {item['task']} (Due: {item.get('due', '?')})")
        print(f"  Summary: {result.get('summary', 'N/A')}")


def run_thread_summary_eval():
    print("\n" + "=" * 70)
    print("EVALUATION: Thread Summary")
    print("=" * 70)

    print(f"\nSummarizing thread: {LONG_THREAD_EXAMPLE['subject']}")
    print(f"Messages: {len(LONG_THREAD_EXAMPLE['messages'])}")

    result = summarize_thread(LONG_THREAD_EXAMPLE, USER_CONTEXT)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        return

    print(f"\nTopic: {result.get('topic', 'N/A')}")
    print(f"\nKey Points:")
    for p in result.get("key_points", []):
        print(f"  - {p}")
    print(f"\nDirection Changes:")
    for c in result.get("direction_changes", []):
        print(f"  ⚠️ {c}")
    print(f"\nCurrent Status: {result.get('current_status', 'N/A')}")
    print(f"\nAction Required:")
    for a in result.get("action_required", []):
        print(f"  🎯 {a}")


if __name__ == "__main__":
    print("Email Processing Agent — Evaluation Dry-Run")
    print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    print()

    run_priority_eval()
    run_action_item_eval()
    run_thread_summary_eval()

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)
