# Mode-Aware Universal Debugger

> **Key Insight**: "Auto-fixing everything is wrong for learning. Different contexts need different error handling behaviors."

## The Problem

Traditional debuggers either:
1. **Always crash** - Good for learning, bad for production
2. **Always auto-fix** - Good for production, bad for learning

Neither approach works well across all contexts.

## The Solution: Three Modes

### 🎓 Development Mode - **LEARN**
Shows errors and solutions without applying fixes.

**Goal**: Help developers understand what's wrong and how to fix it.

```bash
DEBUG_MODE=development python mode_aware_debugger.py script.py
```

**Output**:
```
🎓 DEVELOPMENT MODE - Learning
======================================================================
📍 Error: KeyError
📂 Location: script.py:42

❓ What's wrong:
   Dictionary key does not exist

💡 How to fix:
   Confidence: 90%

   The fix would change:
   - Original: user = data['user']
   + Fixed:    user = data.get('user', None)

   → Uses .get() for safe dictionary access

💻 To apply fixes:
   DEBUG_MODE=review python mode_aware_debugger.py script.py
```

**Behavior**:
- ✅ Shows error with educational context
- ✅ Explains what's wrong
- ✅ Shows how to fix
- ✅ Suggests next steps
- ❌ Does NOT modify code
- 🛑 Stops after first error (focus on learning)

**Use For**:
- Learning Python error patterns
- Understanding why code fails
- Teaching/mentoring scenarios
- Code reviews with juniors

---

### 🔍 Review Mode - **CONTROL**
Shows fixes and asks for confirmation before applying.

**Goal**: Give developers control while making fixes easy.

```bash
DEBUG_MODE=review python mode_aware_debugger.py script.py
```

**Output**:
```
🔍 REVIEW MODE
======================================================================
📍 KeyError at script.py:42
📝 Dictionary key does not exist
🎯 Confidence: 90%

   - user = data['user']
   + user = data.get('user', None)
======================================================================

❓ Apply this fix? [y/n/a=all/s=skip all]:
```

**Behavior**:
- ✅ Shows each fix before applying
- ✅ User confirms each change
- ✅ Can switch to production mode mid-session (`a` = apply all)
- ✅ Can switch to development mode mid-session (`s` = skip all)
- ✅ Continues through all errors (if confirming)

**Use For**:
- Reviewing unfamiliar code
- Careful refactoring
- Learning while fixing
- When you want visibility + automation

---

### 🚀 Production Mode - **AUTOMATE**
Auto-fixes everything silently with detailed logging.

**Goal**: Keep application running, never crash.

```bash
DEBUG_MODE=production python mode_aware_debugger.py script.py
```

**Output**:
```
[FIX] KeyError at line 42
[FIX] ZeroDivisionError at line 58
[FIX] IndexError at line 103

🚀 PRODUCTION SESSION SUMMARY
======================================================================
Fixes applied: 3

✅ Auto-fixed errors:
   KeyError: 1x
   ZeroDivisionError: 1x
   IndexError: 1x

📋 See debugger_fixes.log for details
```

**Behavior**:
- ✅ Auto-applies all fixes from ERROR_DATABASE
- ✅ Minimal console output
- ✅ Detailed logging to `debugger_fixes.log`
- ✅ JSON report for monitoring: `debugger_report.json`
- ✅ Continues until all errors fixed or max iterations
- ❌ No user interaction required

**Use For**:
- CI/CD pipelines
- Automated deployments
- Legacy code cleanup
- Batch fixing

---

## Quick Start

### 1. Installation

No installation needed! Just ensure you have:
- `mode_aware_debugger.py`
- `universal_debugger.py` (for ERROR_DATABASE)

### 2. Create a Buggy Script

```python
# buggy.py
def calculate(data):
    total = data["total"]  # KeyError if key missing
    count = data["count"]
    average = total / count  # ZeroDivisionError if count = 0
    return average

result = calculate({"total": 100})  # Missing "count" key
print(result)
```

### 3. Learn (Development Mode)

```bash
DEBUG_MODE=development python mode_aware_debugger.py buggy.py
```

See the error, understand the fix, don't modify code.

### 4. Review (Safe Mode)

```bash
DEBUG_MODE=review python mode_aware_debugger.py buggy.py
```

Review each fix, approve or skip.

### 5. Deploy (Production Mode)

```bash
DEBUG_MODE=production python mode_aware_debugger.py buggy.py
```

Auto-fix everything, log results.

---

## Unknown Error Discovery

When the debugger encounters an error NOT in the ERROR_DATABASE:

### Development/Review Mode
```
❌ UNKNOWN ERROR - Not in database yet
======================================================================
Error Type: socket.gaierror
Location: script.py:15
Message: [Errno -3] Temporary failure in name resolution
Problematic line: sock.connect(("invalid.host", 9999))

✅ Pattern logged to unknown_errors.json
   This helps improve the database!

📝 To add this fix to ERROR_DATABASE:
   'gaierror': {
       'description': '<what this error means>',
       'patterns': [{
           'detect': r'<regex to match>',
           'fix': lambda line, indent, error_msg: '<your fix>',
           'multiline': False,
           'confidence': 0.85
       }]
   }
```

**This creates a feedback loop for database growth!**

### Production Mode
```
[SKIP] No fix available for socket.gaierror
```

Logs to file, continues execution.

---

## ERROR_DATABASE Coverage

Currently supports **31 error types**:

### File Operations
- FileNotFoundError
- PermissionError
- IOError
- OSError

### Data Access
- KeyError
- IndexError
- AttributeError

### Type Errors
- TypeError
- ValueError
- ZeroDivisionError

### Network
- ConnectionError
- TimeoutError

### Imports
- ImportError
- ModuleNotFoundError

### Encoding
- UnicodeDecodeError
- UnicodeEncodeError

### JSON
- JSONDecodeError

### And 14 more...

---

## Mode Comparison

| Feature | Development | Review | Production |
|---------|------------|--------|------------|
| Shows errors | ✅ | ✅ | ❌ |
| Explains fixes | ✅ | ✅ | ❌ |
| Applies fixes | ❌ | 🤔 Ask | ✅ Auto |
| Modifies code | ❌ | Sometimes | ✅ |
| User interaction | ❌ None | ✅ Required | ❌ None |
| Logging | ✅ Basic | ✅ Basic | ✅ Detailed |
| Stops after first error | ✅ | ❌ | ❌ |
| Unknown error capture | ✅ Detailed | ✅ Detailed | ⚠️  Log only |
| Use case | Learning | Safe fixing | Automation |

---

## Advanced Features

### Mode Switching Mid-Session

In **review mode**, you can dynamically switch:

- Press `a` → Switch to production mode (auto-apply remaining)
- Press `s` → Switch to development mode (skip remaining)
- Press `y` → Apply this fix
- Press `n` → Skip this fix

### Backup and Safety

Every run creates a backup:
```
script.py → script.py.backup
```

If something goes wrong, restore with:
```bash
mv script.py.backup script.py
```

### Session Reports

Each mode generates appropriate reports:

**Development**: Shows what you could fix
**Review**: Shows what you did fix
**Production**: Generates JSON for monitoring

### Logging

All modes log to `debugger_fixes.log`:
```
2025-11-07 14:23:15,234 - INFO - Auto-fixed KeyError at script.py:42
2025-11-07 14:23:16,891 - INFO - Auto-fixed ZeroDivisionError at script.py:58
```

---

## Integration with Feedback Loop

Works seamlessly with `adaptive_error_handler.py` and `feedback_loop.py`:

```
Development-time debugging:
  mode_aware_debugger.py → Fix bugs before they reach runtime

Runtime error handling:
  adaptive_error_handler.py → Handle errors during execution

Pattern learning:
  feedback_loop.py → Analyze and enhance ERROR_DATABASE
```

Complete error handling ecosystem!

---

## Real-World Workflows

### Beginner Learning Workflow
```bash
# 1. See errors and learn
DEBUG_MODE=development python mode_aware_debugger.py my_code.py

# 2. Manually fix based on suggestions
vim my_code.py

# 3. Repeat until you understand the patterns
```

### Code Review Workflow
```bash
# 1. Review each fix carefully
DEBUG_MODE=review python mode_aware_debugger.py legacy_code.py

# 2. Approve good fixes, skip questionable ones
# 3. Manually fix skipped issues
```

### CI/CD Workflow
```bash
# In your .gitlab-ci.yml or .github/workflows/
script:
  - DEBUG_MODE=production python mode_aware_debugger.py src/*.py
  - cat debugger_report.json  # Check results
```

### Legacy Code Cleanup
```bash
# Auto-fix obvious errors
DEBUG_MODE=production python mode_aware_debugger.py old_code.py

# Review the changes
git diff

# Commit if good
git commit -m "Auto-fix common errors"
```

---

## Philosophy

### Why Three Modes?

**One size doesn't fit all.** Different contexts need different behaviors:

1. **Learning** requires visibility and explanation
2. **Safe fixing** requires control and confirmation
3. **Production** requires automation and reliability

### Educational Value

Traditional tools either:
- Show stack traces (overwhelming for beginners)
- Auto-fix (no learning happens)

Mode-aware debugging **teaches while fixing**:
- See the error
- Understand the problem
- Learn the solution
- Decide whether to apply

### Professional Patterns

Matches industry-standard workflows:
- Flask/Django: `DEBUG = True/False`
- Rails: `development/production` environments
- Node.js: `NODE_ENV=development/production`

Familiar pattern, applied to debugging.

---

## Examples

### Example 1: KeyError

**Buggy Code**:
```python
user = data['username']  # KeyError if key missing
```

**Development Mode Output**:
```
❓ What's wrong:
   Dictionary key does not exist

💡 How to fix:
   - Original: user = data['username']
   + Fixed:    user = data.get('username', None)

   → Uses .get() for safe dictionary access
```

**Fixed Code** (after production mode):
```python
user = data.get('username', None)
```

### Example 2: ZeroDivisionError

**Buggy Code**:
```python
average = total / count  # ZeroDivisionError if count = 0
```

**Development Mode Output**:
```
❓ What's wrong:
   Division by zero

💡 How to fix:
   - Original: average = total / count
   + Fixed:    average = (total / count if count != 0 else 0)

   → Adds zero-division check
```

### Example 3: FileNotFoundError

**Buggy Code**:
```python
with open("config.json") as f:
    config = json.load(f)
```

**Fixed Code** (auto-wrapped in try/except):
```python
try:
    with open("config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    return {}
```

---

## Comparison with Other Tools

| Tool | Auto-Fix | Educational | Interactive | Production-Ready |
|------|----------|------------|-------------|------------------|
| pylint | ❌ | ✅ | ❌ | ❌ |
| autopep8 | ✅ | ❌ | ❌ | ✅ |
| **Mode-Aware Debugger** | 🎯 | ✅ | ✅ | ✅ |

**pylint**: Finds issues, but doesn't fix
**autopep8**: Fixes formatting, not logic errors
**Mode-Aware Debugger**: Fixes logic errors with learning options

---

## Contributing New Error Patterns

Found an error not in the database? Add it!

1. Run in development mode to capture pattern:
```bash
DEBUG_MODE=development python mode_aware_debugger.py your_code.py
```

2. Check `unknown_errors.json` for the pattern

3. Add to `ERROR_DATABASE` in `universal_debugger.py`:
```python
'NewErrorType': {
    'description': 'What this error means',
    'patterns': [
        {
            'detect': r'<regex pattern>',
            'fix': lambda line, indent, error_msg: '<fixed line>',
            'multiline': False,
            'confidence': 0.85
        }
    ]
}
```

4. Test it:
```bash
DEBUG_MODE=production python mode_aware_debugger.py your_code.py
```

---

## Files Generated

- `script.py.backup` - Backup of original file
- `debugger_fixes.log` - Detailed log of all fixes
- `debugger_report.json` - Machine-readable report (production mode)
- `unknown_errors.json` - Unknown errors for database expansion

---

## Tips

### For Beginners
Start with **development mode** - see errors, learn patterns, gain confidence.

### For Intermediate Developers
Use **review mode** - stay in control, learn edge cases, build trust.

### For Production
Use **production mode** - automate fixes, log everything, monitor with JSON reports.

### For Teaching
Use **development mode** with students - it's a learning tool, not just a fixer.

---

## Summary

**Mode-Aware Universal Debugger** solves a fundamental problem:

> You can't optimize for both learning and automation with a single approach.

By providing **three modes** with **distinct behaviors**, it serves:
- 🎓 Learners who need to understand errors
- 🔍 Developers who want control
- 🚀 Production systems that need reliability

**Same tool, different contexts, zero compromise.**

---

*Built with the philosophy that debugging should adapt to the developer, not the other way around.*
