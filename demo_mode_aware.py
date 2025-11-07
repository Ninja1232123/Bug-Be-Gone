#!/usr/bin/env python3
"""
Comprehensive demonstration of Mode-Aware Universal Debugger.

Shows all three modes in action and their different behaviors.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def create_demo_script():
    """Create a script with multiple fixable errors."""
    code = '''#!/usr/bin/env python3
"""Demo script with common errors."""

import json

def process_user_data(user_id):
    """Process user data - has multiple bugs."""

    # Bug 1: FileNotFoundError - missing file
    with open(f"user_{user_id}.json") as f:
        data = json.load(f)

    # Bug 2: KeyError - key might not exist
    username = data["username"]

    # Bug 3: ZeroDivisionError - games_played might be 0
    score = data["points"] / data["games_played"]

    # Bug 4: IndexError - items list might be empty
    first_item = data["items"][0]

    return {
        "username": username,
        "score": score,
        "first_item": first_item
    }


if __name__ == "__main__":
    result = process_user_data(123)
    print(f"Result: {result}")
'''

    path = Path("demo_buggy.py")
    with open(path, "w") as f:
        f.write(code)

    return path


def demo_development_mode():
    """Demonstrate development mode - learning without fixing."""
    print("\n" + "="*70)
    print("DEMO 1: DEVELOPMENT MODE - Learning")
    print("="*70)
    print("\n🎓 Use Case: You're learning Python and want to understand errors")
    print("   Goal: See errors, understand fixes, don't modify code\n")

    input("Press Enter to run in DEVELOPMENT mode...")

    # Create fresh copy
    script = create_demo_script()

    # Run in development mode
    result = subprocess.run(
        ["python", "mode_aware_debugger.py", str(script)],
        env={**os.environ, "DEBUG_MODE": "development"},
        capture_output=False
    )

    print("\n✅ Development Mode Key Points:")
    print("   - Showed the error with educational context")
    print("   - Explained what's wrong and how to fix")
    print("   - Did NOT modify the code")
    print("   - Stopped after first error (focus on learning)")

    # Clean up
    if script.exists():
        script.unlink()
    backup = Path(f"{script}.backup")
    if backup.exists():
        backup.unlink()


def demo_production_mode():
    """Demonstrate production mode - auto-fix everything."""
    print("\n" + "="*70)
    print("DEMO 2: PRODUCTION MODE - Automation")
    print("="*70)
    print("\n🚀 Use Case: Deploying to production, need reliable code")
    print("   Goal: Auto-fix all known errors, log everything\n")

    input("Press Enter to run in PRODUCTION mode...")

    # Create fresh copy
    script = create_demo_script()

    # Show original code
    print("\n📄 Original code:")
    print("-" * 70)
    with open(script) as f:
        lines = f.readlines()
        for i, line in enumerate(lines[9:14], start=10):
            print(f"{i:3}| {line}", end='')
    print("-" * 70)

    # Run in production mode
    result = subprocess.run(
        ["python", "mode_aware_debugger.py", str(script)],
        env={**os.environ, "DEBUG_MODE": "production"},
        capture_output=False
    )

    # Show fixed code
    print("\n📄 Fixed code:")
    print("-" * 70)
    with open(script) as f:
        lines = f.readlines()
        for i, line in enumerate(lines[9:18], start=10):
            print(f"{i:3}| {line}", end='')
    print("-" * 70)

    print("\n✅ Production Mode Key Points:")
    print("   - Auto-fixed the error without asking")
    print("   - Added try/except block for safety")
    print("   - Logged to debugger_fixes.log")
    print("   - Generated JSON report")
    print("   - Would continue to fix ALL errors (iteration 2, 3, etc.)")

    # Show the log
    if Path("debugger_fixes.log").exists():
        print("\n📋 Log file contents:")
        with open("debugger_fixes.log") as f:
            for line in f.readlines()[-3:]:
                print(f"   {line.strip()}")

    # Clean up
    if script.exists():
        script.unlink()
    backup = Path(f"{script}.backup")
    if backup.exists():
        backup.unlink()


def demo_review_mode():
    """Demonstrate review mode - interactive fixing."""
    print("\n" + "="*70)
    print("DEMO 3: REVIEW MODE - Safe Interactive Fixing")
    print("="*70)
    print("\n🔍 Use Case: Reviewing legacy code, want control over changes")
    print("   Goal: See each fix, decide whether to apply\n")
    print("⚠️  Note: This demo would normally be interactive")
    print("   In review mode, you'd press 'y' to apply or 'n' to skip each fix")
    print("   You can also press:")
    print("   - 'a' to switch to production mode (auto-apply remaining)")
    print("   - 's' to switch to development mode (skip remaining)\n")

    input("Press Enter to simulate REVIEW mode output...")

    script = create_demo_script()

    print("\n" + "="*70)
    print("🔍 REVIEW MODE")
    print("="*70)
    print("📍 FileNotFoundError at demo_buggy.py:10")
    print("📝 File or directory does not exist")
    print("🎯 Confidence: 80%")
    print()
    print("   - with open(f\"user_{user_id}.json\") as f:")
    print("   + try:")
    print("       with open(f\"user_{user_id}.json\") as f:")
    print("     except FileNotFoundError:")
    print("       return {}")
    print("="*70)
    print()
    print("❓ Apply this fix? [y/n/a=all/s=skip all]: _")
    print()
    print("   (In real usage, you'd type 'y', 'n', 'a', or 's')")

    print("\n✅ Review Mode Key Points:")
    print("   - Shows each fix before applying")
    print("   - User decides: apply, skip, or change mode")
    print("   - Best of both worlds: visibility + convenience")
    print("   - Can switch modes mid-session")

    # Clean up
    if script.exists():
        script.unlink()
    backup = Path(f"{script}.backup")
    if backup.exists():
        backup.unlink()


def demo_unknown_error():
    """Demonstrate unknown error capture."""
    print("\n" + "="*70)
    print("DEMO 4: UNKNOWN ERROR DISCOVERY")
    print("="*70)
    print("\n🔬 Use Case: Encountering an error not in ERROR_DATABASE")
    print("   Goal: Capture pattern for future database expansion\n")

    print("When the debugger encounters an unknown error:")
    print()
    print("="*70)
    print("❌ UNKNOWN ERROR - Not in database yet")
    print("="*70)
    print("Error Type: CustomBusinessError")
    print("Location: script.py:42")
    print("Message: Invalid state transition from PENDING to COMPLETED")
    print("Problematic line: order.transition_to('COMPLETED')")
    print()
    print("✅ Pattern logged to unknown_errors.json")
    print("   This helps improve the database!")
    print()
    print("📝 To add this fix to ERROR_DATABASE:")
    print("   'CustomBusinessError': {")
    print("       'description': 'Invalid state transition',")
    print("       'patterns': [{")
    print("           'detect': r'\.transition_to\\(',")
    print("           'fix': lambda line, indent, error_msg: ...,")
    print("           'multiline': False,")
    print("           'confidence': 0.85")
    print("       }]")
    print("   }")
    print("="*70)

    print("\n✅ Unknown Error Capture:")
    print("   - Logs error details to unknown_errors.json")
    print("   - Shows template for adding to ERROR_DATABASE")
    print("   - Creates feedback loop for database growth")
    print("   - Every error captured = one less error to debug manually")


def demo_comparison():
    """Show side-by-side comparison of modes."""
    print("\n" + "="*70)
    print("MODE COMPARISON SUMMARY")
    print("="*70)

    print("""
┌─────────────────┬──────────────┬─────────┬────────────┐
│ Feature         │ Development  │ Review  │ Production │
├─────────────────┼──────────────┼─────────┼────────────┤
│ Shows errors    │ ✅ Yes       │ ✅ Yes  │ ❌ No      │
│ Explains fixes  │ ✅ Yes       │ ✅ Yes  │ ❌ No      │
│ Applies fixes   │ ❌ No        │ 🤔 Ask  │ ✅ Auto    │
│ Modifies code   │ ❌ Never     │ 🤔 Maybe│ ✅ Always  │
│ User input      │ ❌ None      │ ✅ Yes  │ ❌ None    │
│ Logging         │ ✅ Basic     │ ✅ Basic│ ✅ Detailed│
│ Stop on error   │ ✅ First     │ ❌ No   │ ❌ No      │
│ Unknown errors  │ ✅ Capture   │ ✅ Log  │ ⚠️  Skip   │
│ Best for        │ 🎓 Learning │ 🔍 Safe │ 🚀 Deploy  │
└─────────────────┴──────────────┴─────────┴────────────┘

🎓 DEVELOPMENT: "Show me errors, teach me fixes"
   → Perfect for learning and understanding

🔍 REVIEW: "Let me decide what to fix"
   → Perfect for careful refactoring

🚀 PRODUCTION: "Fix everything automatically"
   → Perfect for deployment and automation
""")


def demo_workflow():
    """Show recommended workflow."""
    print("\n" + "="*70)
    print("RECOMMENDED WORKFLOW")
    print("="*70)

    print("""
1️⃣  LEARN (Development Mode)
   $ DEBUG_MODE=development python mode_aware_debugger.py my_code.py
   → Understand what's wrong
   → Learn fix patterns
   → No code changes

2️⃣  REVIEW (Review Mode)
   $ DEBUG_MODE=review python mode_aware_debugger.py my_code.py
   → Apply fixes you understand
   → Skip ones you're unsure about
   → Build confidence

3️⃣  AUTOMATE (Production Mode)
   $ DEBUG_MODE=production python mode_aware_debugger.py my_code.py
   → Auto-fix everything
   → Deploy with confidence
   → Monitor logs

This progression builds skill while ensuring safety!
""")


def main():
    """Run comprehensive demonstration."""
    print("="*70)
    print("MODE-AWARE UNIVERSAL DEBUGGER")
    print("Comprehensive Demonstration")
    print("="*70)

    print("""
This demo shows how the SAME tool behaves differently based on mode,
serving different needs without compromise.

Key Insight:
  "Auto-fixing everything is wrong for learning.
   Different contexts need different behaviors."

We'll demonstrate:
  1. Development Mode - Learning without modifying code
  2. Production Mode - Automated fixing with logging
  3. Review Mode - Interactive safe fixing
  4. Unknown Error Discovery - Database expansion
  5. Mode Comparison - When to use each
  6. Recommended Workflow - How to progress
""")

    input("\nPress Enter to start the demonstration...")

    # Run demos
    demo_development_mode()
    demo_production_mode()
    demo_review_mode()
    demo_unknown_error()
    demo_comparison()
    demo_workflow()

    print("\n" + "="*70)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*70)

    print("""
🎯 Key Takeaways:

1. Development mode TEACHES - See errors, understand fixes, learn
2. Review mode gives CONTROL - Approve each change, stay safe
3. Production mode AUTOMATES - Fix everything, log details, deploy

4. Unknown errors are CAPTURED - Helps grow ERROR_DATABASE
5. Same tool, different behaviors - No compromise needed

💡 Try it yourself:
   $ DEBUG_MODE=development python mode_aware_debugger.py your_script.py
   $ DEBUG_MODE=review python mode_aware_debugger.py your_script.py
   $ DEBUG_MODE=production python mode_aware_debugger.py your_script.py

📚 Full documentation: MODE_AWARE_DEBUGGER_README.md
""")

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
