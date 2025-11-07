# The Feedback Loop: Development vs Production Error Handling

> **Philosophy**: "Every error you debug is a bug you'll never have to fix again. All you have to do is fix every error one more time."

## Overview

This system implements **environment-aware error handling** that adapts behavior based on whether code is running in development or production:

- **Development Mode**: Crashes are *good* — they make bugs visible so you can fix them
- **Production Mode**: Robustness is *critical* — graceful degradation without exposing internals
- **Maintenance Mode**: Patterns collected from both modes feed back into automatic fixing

The key insight: **Error handling should be separate from application logic**, allowing the same codebase to behave differently based on environment without compromising either development visibility or production reliability.

## The Three Pillars

### 1. Adaptive Error Handler (`adaptive_error_handler.py`)

Environment-aware error handling that changes behavior based on `APP_MODE`:

```python
import os
from adaptive_error_handler import adaptive_error_handler

# Automatically adapts to APP_MODE environment variable
@adaptive_error_handler(fallback_value={})
def risky_operation():
    with open("config.json") as f:
        return json.load(f)

# Development (APP_MODE=development):
#   → Crashes with full stack trace
#   → Logs error pattern for analysis
#   → Maximum visibility for debugging

# Production (APP_MODE=production):
#   → Returns fallback value ({})
#   → Logs securely (no sensitive data)
#   → Notifies developers
#   → Continues execution
```

**Features**:
- Decorator syntax: `@adaptive_error_handler(fallback_value=None)`
- Context manager: `with AdaptiveErrorContext("operation")`
- Automatic error pattern collection
- Secure logging (sanitizes sensitive data in production)
- Developer notification hooks

### 2. Universal Debugger (`universal_debugger.py`)

Automatic error fixing using a database of 31+ error patterns:

```python
python universal_debugger.py your_script.py
```

Iteratively:
1. Runs your script
2. Detects errors
3. Applies fixes from `ERROR_DATABASE`
4. Repeats until no errors or max iterations

**Supported Errors** (31+ types):
- `FileNotFoundError`, `KeyError`, `IndexError`, `ZeroDivisionError`
- `TypeError`, `ValueError`, `AttributeError`, `NameError`
- `ImportError`, `JSONDecodeError`, `ConnectionError`, `PermissionError`
- And 20+ more...

Each error has **hard-coded fix patterns** — no AI needed, just proven solutions.

### 3. Feedback Loop System (`feedback_loop.py`)

Connects error collection → analysis → auto-fixing:

```python
from feedback_loop import FeedbackLoop

loop = FeedbackLoop()

# Analyze errors collected during runtime
insights = loop.analyze_runtime_errors()

# Report on ERROR_DATABASE coverage
loop.report_coverage()
# → Shows what % of errors can be auto-fixed

# Get suggestions for missing patterns
loop.suggest_missing_patterns()
# → Generates ERROR_DATABASE entries for new errors
```

**Components**:
- **Error Analysis**: Identifies which runtime errors need database patterns
- **Coverage Reporting**: Shows auto-fix capability vs. real-world errors
- **Pattern Suggestions**: Generates template code for ERROR_DATABASE
- **Error Fuzzer**: Systematic edge case generation for error discovery

## The Complete Cycle

```
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
```

## Quick Start

### 1. Set Environment Mode

```bash
# Development
export APP_MODE=development

# Production
export APP_MODE=production
```

### 2. Instrument Your Code

**Option A: Decorator (recommended for functions)**
```python
from adaptive_error_handler import adaptive_error_handler

@adaptive_error_handler(fallback_value=None)
def my_function():
    # Your code here
    risky_operation()
```

**Option B: Context Manager (recommended for code blocks)**
```python
from adaptive_error_handler import AdaptiveErrorContext

def my_function():
    with AdaptiveErrorContext("database_query", fallback_value=[]):
        return execute_query()
```

**Option C: Top-level Handler (recommended for CLIs)**
```python
import sys
from adaptive_error_handler import IS_DEV

def my_cli():
    # Application logic
    pass

if __name__ == '__main__':
    try:
        my_cli()
    except Exception as error:
        if IS_DEV:
            raise  # Crash in dev
        else:
            print(f"Error occurred: {error}")
            sys.exit(1)
```

### 3. Run and Collect Patterns

```bash
# Development: Fix bugs as they crash
APP_MODE=development python my_app.py

# Production: Collect error patterns
APP_MODE=production python my_app.py
```

### 4. Analyze and Enhance

```python
python feedback_loop.py
# Shows:
# - Error coverage (% auto-fixable)
# - Frequent errors
# - Suggested ERROR_DATABASE additions
```

### 5. Auto-Fix Scripts

```bash
python universal_debugger.py buggy_script.py
# Automatically fixes errors iteratively
```

## Demonstration

```bash
python demo_feedback_loop.py
```

This shows:
1. ✅ Development mode crash behavior
2. ✅ Production mode graceful handling
3. ✅ Error pattern collection
4. ✅ Coverage analysis
5. ✅ Auto-fixing capability
6. ✅ Error discovery fuzzing

## Architecture

```
adaptive_error_handler.py
├── @adaptive_error_handler      # Decorator
├── AdaptiveErrorContext         # Context manager
├── DevelopmentErrorHandler      # Crash + log pattern
├── ProductionErrorHandler       # Catch + sanitize + notify
└── analyze_error_patterns()     # Pattern analysis

universal_debugger.py
├── ERROR_DATABASE               # 31+ error fix patterns
├── run_and_capture_error()      # Execute and detect
├── parse_error()                # Extract error details
└── fix_error()                  # Apply database fix

feedback_loop.py
├── FeedbackLoop
│   ├── analyze_runtime_errors() # Analyze collected patterns
│   ├── report_coverage()        # Coverage metrics
│   └── suggest_missing_patterns() # Generate additions
└── ErrorFuzzer
    ├── generate_edge_cases()    # Common error triggers
    └── test_function()          # Systematic testing
```

## Key Benefits

### 1. Separation of Concerns
Application logic doesn't know about dev vs prod differences — error handling is centralized.

### 2. Maximum Visibility in Development
Crashes expose bugs immediately, making them impossible to ignore.

### 3. Maximum Reliability in Production
Graceful degradation keeps systems running, with secure logging and notifications.

### 4. Monotonically Improving Reliability
Each error fixed once → added to ERROR_DATABASE → never needs manual fixing again.

### 5. Systematic Error Discovery
Fuzzing and edge case generation find errors *before* production.

## Error Pattern Collection

Errors are logged to `logs/error_patterns.jsonl`:

```json
{
  "error_type": "FileNotFoundError",
  "message": "[Errno 2] No such file or directory: 'config.json'",
  "traceback": "...",
  "context": {"function": "load_config"},
  "timestamp": "2025-11-07T13:47:33.741"
}
```

Analyze with:
```python
from feedback_loop import FeedbackLoop
loop = FeedbackLoop()
loop.analyze_runtime_errors()
```

## Extending ERROR_DATABASE

When `feedback_loop.py` identifies uncovered errors, it suggests additions:

```python
'NewErrorType': {
    'description': 'NewErrorType (add description)',
    'patterns': [
        {
            'detect': r'.*',  # Regex to detect error in code
            'fix': lambda line, indent, error_msg: line,  # Fix function
            'multiline': False,
            'confidence': 0.5
        }
    ]
}
```

Add this to `ERROR_DATABASE` in `universal_debugger.py`.

## Philosophy in Practice

> **"Every error you debug is a bug you'll never have to fix again."**

This isn't just about catching errors — it's about **systematically eliminating entire classes of bugs**:

1. **Development**: Encounter error → Debug → Fix manually
2. **Maintenance**: Add pattern to ERROR_DATABASE
3. **Future**: All instances auto-fix instantly
4. **Result**: Bug count decreases monotonically

The feedback loop ensures that every debugging session *permanently* improves your tooling.

## Real-World Usage

### CLI Application
```python
import sys
from adaptive_error_handler import IS_DEV

def my_cli():
    # Your application
    pass

if __name__ == '__main__':
    try:
        my_cli()
    except Exception as error:
        if IS_DEV:
            raise
        else:
            print(f"Unexpected error occurred")
            sys.exit(1)
```

### Web API
```python
from adaptive_error_handler import adaptive_error_handler

@app.route('/api/users/<user_id>')
@adaptive_error_handler(fallback_value={"error": "User not found"})
def get_user(user_id):
    return database.get_user(user_id)
```

### Data Pipeline
```python
from adaptive_error_handler import AdaptiveErrorContext

def process_batch(batch):
    with AdaptiveErrorContext("batch_processing"):
        transform(batch)
        validate(batch)
        load(batch)
```

## Testing

The system includes comprehensive testing via `demo_feedback_loop.py`:

```bash
# Run full demonstration
python demo_feedback_loop.py

# Test development mode only
APP_MODE=development python adaptive_error_handler.py

# Test production mode only
APP_MODE=production python adaptive_error_handler.py

# Analyze current patterns
python feedback_loop.py
```

## Files

- `adaptive_error_handler.py` — Environment-aware error handling
- `universal_debugger.py` — Auto-fixing with ERROR_DATABASE
- `feedback_loop.py` — Pattern analysis and coverage reporting
- `demo_feedback_loop.py` — Complete system demonstration
- `logs/` — Error patterns and logs
  - `error_patterns.jsonl` — Collected error patterns
  - `errors_YYYYMMDD.log` — Daily error logs

## Environment Variables

- `APP_MODE` — Set to `development`, `dev`, `debug` for dev mode, anything else for production
- Default: `production` (fail-safe)

## Summary

This system embodies a simple but powerful principle:

**Let it crash in development. Stay solid in production. Learn from both.**

The same codebase adapts its error handling to the environment, ensuring:
- Developers see every bug immediately
- Users never see internal errors
- Every error contributes to improving the system
- Bug fixing becomes progressively less necessary

The result: **Software that becomes more reliable with every error encountered.**

---

*Built with the philosophy that error handling should be environment-aware, systematic, and learning.*
