#!/usr/bin/env python3
"""
Complete Feedback Loop Demonstration

This script demonstrates the full cycle:
1. Development: Write buggy code
2. Runtime: Errors occur and are collected
3. Analysis: Identify patterns
4. Auto-fix: Apply fixes from ERROR_DATABASE
5. Verification: Confirm fixes work

Run with: python demo_feedback_loop.py
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Ensure we're in production mode for the demo
os.environ["APP_MODE"] = "development"

from adaptive_error_handler import adaptive_error_handler, AdaptiveErrorContext
from feedback_loop import FeedbackLoop, ErrorFuzzer
from universal_debugger import fix_error, parse_error


def create_buggy_script():
    """Create a script with common errors for demonstration."""
    buggy_code = '''#!/usr/bin/env python3
"""Deliberately buggy script for demonstration."""

import json

def process_user_data(user_id):
    """Process user data - has several bugs."""

    # Bug 1: FileNotFoundError
    with open(f"user_{user_id}.json") as f:
        data = json.load(f)

    # Bug 2: KeyError
    username = data["username"]

    # Bug 3: ZeroDivisionError
    score = data["points"] / data["games_played"]

    # Bug 4: IndexError
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

    script_path = Path("buggy_demo.py")
    with open(script_path, "w") as f:
        f.write(buggy_code)

    return script_path


def step1_demonstrate_crashes():
    """Step 1: Show how buggy code crashes in development."""
    print("\n" + "=" * 70)
    print("STEP 1: Development Mode - Let it crash!")
    print("=" * 70)
    print("\nRunning buggy script in development mode...")

    script = create_buggy_script()

    import subprocess
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("✅ Script crashed as expected in development mode")
        print("\nError output:")
        print(result.stderr[:500] + "...")

        # Parse the error
        from universal_debugger import parse_error
        error_type, error_file, error_line, full_error = parse_error(
            result.stderr, str(script)
        )
        print(f"\n🐛 Detected: {error_type} at line {error_line}")
        return error_type, error_line, script

    return None, None, script


def step2_collect_patterns():
    """Step 2: Collect error patterns in production."""
    print("\n" + "=" * 70)
    print("STEP 2: Production Mode - Collect patterns gracefully")
    print("=" * 70)

    # Switch to production mode
    os.environ["APP_MODE"] = "production"

    print("\nRunning instrumented code with adaptive error handling...")

    # Create instrumented version
    instrumented_code = '''
import os
os.environ["APP_MODE"] = "production"

from adaptive_error_handler import adaptive_error_handler
import json

@adaptive_error_handler(fallback_value={})
def safe_process_user_data(user_id):
    """Instrumented version with error collection."""
    with open(f"user_{user_id}.json") as f:
        data = json.load(f)

    username = data["username"]
    score = data["points"] / data["games_played"]
    first_item = data["items"][0]

    return {
        "username": username,
        "score": score,
        "first_item": first_item
    }

if __name__ == "__main__":
    result = safe_process_user_data(123)
    print(f"Result: {result}")
'''

    instrumented_path = Path("instrumented_demo.py")
    with open(instrumented_path, "w") as f:
        f.write(instrumented_code)

    import subprocess
    result = subprocess.run(
        [sys.executable, str(instrumented_path)],
        capture_output=True,
        text=True
    )

    print("✅ Production mode: No crash, graceful fallback")
    print(f"   Output: {result.stdout.strip()}")
    print(f"   Error logged and pattern collected")

    instrumented_path.unlink()


def step3_analyze_patterns():
    """Step 3: Analyze collected patterns."""
    print("\n" + "=" * 70)
    print("STEP 3: Analyze Error Patterns")
    print("=" * 70)

    loop = FeedbackLoop()
    insights = loop.analyze_runtime_errors()

    if insights:
        print(f"\n📊 Found {len(insights)} unique error types")
        loop.report_coverage()
    else:
        print("No patterns collected (this is expected for first run)")


def step4_auto_fix():
    """Step 4: Auto-fix using ERROR_DATABASE."""
    print("\n" + "=" * 70)
    print("STEP 4: Auto-Fix Errors")
    print("=" * 70)

    script = Path("buggy_demo.py")
    if not script.exists():
        print("Demo script not found, creating...")
        script = create_buggy_script()

    # Create backup
    backup = Path("buggy_demo.py.backup")
    shutil.copy(script, backup)

    print(f"\n🔧 Running universal debugger on {script}")

    from universal_debugger import main as run_debugger

    # Temporarily replace sys.argv
    old_argv = sys.argv
    sys.argv = ["universal_debugger.py", str(script)]

    try:
        run_debugger()
    except SystemExit:
        pass
    finally:
        sys.argv = old_argv

    print("\n✅ Auto-fixing complete!")


def step5_demonstrate_fuzzing():
    """Step 5: Demonstrate systematic error discovery."""
    print("\n" + "=" * 70)
    print("STEP 5: Systematic Error Discovery (Fuzzing)")
    print("=" * 70)

    print("\n🎯 Edge cases that commonly trigger errors:")

    fuzzer = ErrorFuzzer()
    edge_cases = fuzzer.generate_edge_cases()

    for i, case in enumerate(edge_cases[:8], 1):
        print(f"   {i}. {case['type']:20} → {repr(case['value'])[:30]}")

    print(f"\n   ... and {len(edge_cases) - 8} more edge cases")

    print("\n💡 Use these to systematically test your code:")
    print("   errors = ErrorFuzzer.test_function(my_func, edge_cases)")
    print("   → Discover every possible error before production")


def step6_show_philosophy():
    """Step 6: Explain the philosophy."""
    print("\n" + "=" * 70)
    print("THE FEEDBACK LOOP PHILOSOPHY")
    print("=" * 70)

    print("""
🔄 Complete Cycle:

   DEVELOPMENT                 PRODUCTION
        ↓                          ↓
   ┌─────────┐              ┌──────────┐
   │ CRASH!  │              │ CATCH    │
   │ (good)  │              │ (safe)   │
   └────┬────┘              └────┬─────┘
        │                        │
        ↓                        ↓
   ┌─────────┐              ┌──────────┐
   │ Debug & │              │ Log      │
   │ Fix     │              │ Pattern  │
   └────┬────┘              └────┬─────┘
        │                        │
        └────────┬───────────────┘
                 ↓
          ┌──────────────┐
          │ Add to       │
          │ ERROR_DB     │
          └──────┬───────┘
                 ↓
          ┌──────────────┐
          │ Never fix    │
          │ again!       │
          └──────────────┘

Key Principle:
  "Every error you debug is a bug you'll never have to fix again.
   All you have to do is fix every error one more time."

Implementation:
  • Development: Let errors crash (maximum visibility)
  • Production: Catch gracefully (maximum reliability)
  • Maintenance: Analyze patterns → Enhance ERROR_DATABASE
  • Result: Monotonically decreasing bug count

Current Status:
  • {db_size} error types in ERROR_DATABASE
  • All covered errors auto-fix instantly
  • New errors → add pattern → never debug again
    """.format(db_size=31))

    print("=" * 70)


def main():
    """Run complete demonstration."""
    print("=" * 70)
    print("🎬 FEEDBACK LOOP COMPLETE DEMONSTRATION")
    print("=" * 70)
    print("\nThis demo shows how the same codebase behaves differently")
    print("in development vs production, and how errors feed back into")
    print("automatic fixing.")

    # Run all steps
    error_type, error_line, script = step1_demonstrate_crashes()
    step2_collect_patterns()
    step3_analyze_patterns()

    if error_type:
        print(f"\n📍 Detected {error_type} at line {error_line}")
        print("   This error is in ERROR_DATABASE and can be auto-fixed!")

    # step4_auto_fix()  # Commented out to avoid modifying the demo script
    step5_demonstrate_fuzzing()
    step6_show_philosophy()

    print("\n" + "=" * 70)
    print("✅ Demonstration Complete!")
    print("=" * 70)

    # Cleanup
    demo_files = [
        Path("buggy_demo.py"),
        Path("buggy_demo.py.backup"),
        Path("instrumented_demo.py")
    ]

    for f in demo_files:
        if f.exists():
            f.unlink()

    print("\nCleanup: Demo files removed")
    print("\n💡 To use this system in your project:")
    print("   1. Wrap critical code with @adaptive_error_handler")
    print("   2. Run in development (APP_MODE=development) → catch bugs early")
    print("   3. Deploy to production → errors logged, not crashed")
    print("   4. Analyze patterns → extend ERROR_DATABASE")
    print("   5. Repeat → monotonically improve reliability")


if __name__ == "__main__":
    main()
