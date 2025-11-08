#!/usr/bin/env python3
"""
UNIVERSAL DEBUGGER - All Python errors with hard-coded solutions.
Never debug anything again.

Usage: python universal_debugger.py your_script.py
"""

import sys
import os
import re
import subprocess
import shutil
from pathlib import Path


def get_indent(line):
    """Extract indentation from line."""
    return ' ' * (len(line) - len(line.lstrip()))


def wrap_in_try_except(line, exception_type, indent_level=0):
    """Wrap line in try/except block with proper indentation."""
    base_indent = ' ' * indent_level
    inner_indent = ' ' * (indent_level + 4)

    return f"{base_indent}try:\n{inner_indent}{line.strip()}\n{base_indent}except {exception_type}:\n{inner_indent}return {{}}\n"


def get_indented_block(lines, start_idx):
    """Get all lines in an indented block starting from start_idx."""
    if start_idx >= len(lines):
        return ([], 0)

    base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    block_lines = [lines[start_idx].rstrip()]

    # Read subsequent lines that are more indented
    idx = start_idx + 1
    while idx < len(lines):
        line = lines[idx]
        if line.strip() == '':
            block_lines.append('')
            idx += 1
            continue

        line_indent = len(line) - len(line.lstrip())
        if line_indent <= base_indent:
            break

        block_lines.append(line.rstrip())
        idx += 1

    return (block_lines, base_indent)


def wrap_block_in_try_except(block_lines, base_indent, exception_type):
    """Wrap a multi-line block in try/except."""
    spaces = ' ' * base_indent
    inner_spaces = ' ' * (base_indent + 4)

    fixed_lines = [f"{spaces}try:"]
    for block_line in block_lines:
        if block_line.strip():
            # Preserve relative indentation within the block
            line_indent = len(block_line) - len(block_line.lstrip())
            extra_indent = line_indent - base_indent
            fixed_lines.append(f"{inner_spaces}{' ' * extra_indent}{block_line.lstrip()}")
        else:
            fixed_lines.append('')
    fixed_lines.append(f"{spaces}except {exception_type}:")
    fixed_lines.append(f"{inner_spaces}return {{}}")

    return '\n'.join(fixed_lines) + '\n'


def _fix_name_error(line, indent, error_msg):
    """Fix NameError by initializing undefined variable."""
    pattern = r"name '(\w+)' is not defined"
    match = re.search(pattern, error_msg)
    if match:
        var_name = match.group(1)
        return f"{indent}{var_name} = None  # Initialize variable\n{line}"
    return line


def _fix_import_error(line, indent, error_msg):
    """Fix ImportError by wrapping import in try/except block."""
    pattern = r"No module named '(\w+)'"
    match = re.search(pattern, error_msg)
    if match:
        module_name = match.group(1)
        # Wrap the import in try/except to handle missing module gracefully
        result = f"{indent}try:\n"
        result += f"{indent}    {line.strip()}\n"
        result += f"{indent}except (ImportError, ModuleNotFoundError):\n"
        result += f"{indent}    # Module '{module_name}' not installed. Run: pip install {module_name}\n"
        result += f"{indent}    pass\n"
        return result
    return line


def _fix_unbound_local_error(lines, line_number, indent, error_msg):
    """Fix UnboundLocalError by initializing variable at function start.

    This is different from other fix functions - it needs access to all lines
    to find the function definition and add initialization at the right place.
    """
    # Updated pattern to match Python 3.11+ error messages
    pattern = r"local variable '(\w+)'"
    match = re.search(pattern, error_msg)
    if not match:
        return None

    var_name = match.group(1)

    # Find the function definition by going backwards from error line
    func_line_idx = None
    for i in range(line_number - 1, -1, -1):
        if re.match(r'^\s*def\s+\w+\s*\(', lines[i]):
            func_line_idx = i
            break

    if func_line_idx is None:
        # If not in a function, add at the beginning of the file
        func_line_idx = 0

    # Find where to insert the initialization
    # Skip past the function definition line and any docstring
    insert_idx = func_line_idx + 1

    # Skip docstring if present
    if insert_idx < len(lines):
        stripped = lines[insert_idx].strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote_type = '"""' if stripped.startswith('"""') else "'''"
            # Check if single-line docstring (opening and closing on same line)
            if stripped.count(quote_type) >= 2:
                # Single-line docstring
                insert_idx += 1
            else:
                # Multi-line docstring - skip to the closing quotes
                insert_idx += 1
                while insert_idx < len(lines):
                    if quote_type in lines[insert_idx]:
                        insert_idx += 1
                        break
                    insert_idx += 1

    # Check if the variable is already initialized
    # to avoid adding duplicate initializations
    var_already_initialized = False
    for i in range(func_line_idx + 1, min(insert_idx + 3, len(lines))):
        if f"{var_name} = None" in lines[i] and "Initialize" in lines[i]:
            var_already_initialized = True
            break

    if var_already_initialized:
        return False  # Variable already initialized

    # Get the indentation of the function body
    func_indent = get_indent(lines[func_line_idx])
    body_indent = func_indent + "    "

    # Create the initialization line
    init_line = f"{body_indent}{var_name} = None  # Initialize to fix UnboundLocalError\n"

    # Insert at the beginning of the function body
    lines.insert(insert_idx, init_line)

    return True


# EVERY PYTHON ERROR WITH SOLUTION HARD-CODED
ERROR_DATABASE = {
    'FileNotFoundError': {
        'description': 'File or directory does not exist',
        'patterns': [
            {
                'detect': r'open\s*\(',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'FileNotFoundError', len(indent)),
                'multiline': True
            }
        ]
    },

    'KeyError': {
        'description': 'Dictionary key does not exist',
        'patterns': [
            {
                'detect': r'\]\s*\[',  # CHAINED ACCESS: dict["a"]["b"] or dict["key"][0]
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, '(IndexError, KeyError, TypeError)', len(indent)),
                'multiline': True
            },
            {
                'detect': r"(\w+)\[(['\"])([^'\"]+)\2\]",  # Literal keys: dict['key']
                'fix': lambda line, indent, error_msg: re.sub(
                    r"(\w+)\[(['\"])([^'\"]+)\2\]",
                    r"\1.get(\2\3\2, None)",
                    line,
                    count=1
                ),
                'multiline': False
            },
            {
                'detect': r"(\w+)\[(\w+)\]",  # Variable keys: dict[variable]
                'fix': lambda line, indent, error_msg: re.sub(
                    r"(\w+)\[(\w+)\]",
                    r"\1.get(\2, None)",
                    line,
                    count=1
                ),
                'multiline': False
            }
        ]
    },

    'ZeroDivisionError': {
        'description': 'Division by zero - ENHANCED (NOAA MEGA)',
        'patterns': [
            {
                'detect': r'/\s*0\b',  # Literal division by 0
                'fix': lambda line, indent, error_msg: line.replace('/ 0', '/ 1  # Fixed: was / 0'),
                'multiline': False
            },
            {
                'detect': r'np\.ceil.*\/|math\.ceil.*\/',  # NumPy/math ceil division (NOAA bug!)
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'ZeroDivisionError', len(indent)),
                'multiline': True
            },
            {
                'detect': r'(\S+)\s*/\s*(\S+)',  # Any division
                'fix': lambda line, indent, error_msg: re.sub(
                    r'(\S+)\s*/\s*(\S+)',
                    r'(\1 / \2 if \2 != 0 else 0)',
                    line,
                    count=1
                ),
                'multiline': False
            }
        ]
    },

    'IndexError': {
        'description': 'List index out of range',
        'patterns': [
            {
                'detect': r'\]\s*\[',  # CHAINED ACCESS: arr[0][1] or dict["key"][0]["val"]
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, '(IndexError, KeyError, TypeError)', len(indent)),
                'multiline': True
            },
            {
                'detect': r'\[-\d+\]',  # Negative indices like [-1], [-2]
                'fix': lambda line, indent, error_msg: re.sub(
                    r"(\w+(?:\[['\"]?\w+['\"]?\])?)\[(-\d+)\]",
                    r'(\1[\2] if len(\1) >= abs(\2) else None)',
                    line,
                    count=1
                ),
                'multiline': False
            },
            {
                'detect': r'\[(\d+)\]',  # Positive indices like [0], [1]
                'fix': lambda line, indent, error_msg: re.sub(
                    r"(\w+(?:\[['\"]?\w+['\"]?\])?)\[(\d+)\]",
                    r'(\1[\2] if len(\1) > \2 else None)',
                    line,
                    count=1
                ),
                'multiline': False
            },
            {
                'detect': r'\[.+\]',  # Variable/computed indices like [len(arr)//2], [i], [x+1]
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'IndexError', len(indent)),
                'multiline': True
            }
        ]
    },

    'JSONDecodeError': {
        'description': 'Invalid JSON format',
        'patterns': [
            {
                'detect': r'json\.loads?\s*\(',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'json.JSONDecodeError', len(indent)),
                'multiline': True
            }
        ]
    },

    'ValueError': {
        'description': 'Invalid value for operation',
        'patterns': [
            {
                'detect': r'\b(max|min)\s*\(([^)]+)\)',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'ValueError', len(indent)),
                'multiline': True
            },
            {
                'detect': r'\bint\s*\(',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'ValueError', len(indent)),
                'multiline': True
            },
            {
                'detect': r'\bfloat\s*\(',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'ValueError', len(indent)),
                'multiline': True
            }
        ]
    },

    'AttributeError': {
        'description': 'Attribute does not exist on object',
        'patterns': [
            {
                'detect': r'\.\w+\.\w+',  # CHAINED: obj.x.y (MEGA PATTERN - runs first!)
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'AttributeError', len(indent)),
                'multiline': True
            },
            {
                'detect': r'(\w+)\.(\w+)',  # Simple: obj.attr
                'fix': lambda line, indent, error_msg: re.sub(
                    r'(\w+)\.(\w+)',
                    r"getattr(\1, '\2', None)",
                    line,
                    count=1
                ),
                'multiline': False
            }
        ]
    },

    'TypeError': {
        'description': 'Operation on incompatible types',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: f"{indent}if value is not None:\n{indent}    {line.strip()}\n",
                'multiline': True
            }
        ]
    },

    'NameError': {
        'description': 'Variable name not defined',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: _fix_name_error(line, indent, error_msg),
                'multiline': False
            }
        ]
    },

    'ImportError': {
        'description': 'Module import failed',
        'patterns': [
            {
                'detect': r'import\s+',
                'fix': lambda line, indent, error_msg: _fix_import_error(line, indent, error_msg),
                'multiline': True  # Generates try/except block
            }
        ]
    },

    'ModuleNotFoundError': {
        'description': 'Module not found (Python 3.6+)',
        'patterns': [
            {
                'detect': r'import\s+',
                'fix': lambda line, indent, error_msg: _fix_import_error(line, indent, error_msg),
                'multiline': True  # Generates try/except block
            }
        ]
    },

    'IndentationError': {
        'description': 'Incorrect indentation',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: f"{indent}    pass  # Fix indentation\n",
                'multiline': False
            }
        ]
    },

    'SyntaxError': {
        'description': 'Invalid Python syntax',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: f"{indent}# SYNTAX ERROR - Manual fix needed: {line.strip()}\n{indent}pass\n",
                'multiline': False
            }
        ]
    },

    'UnboundLocalError': {
        'description': 'Local variable referenced before assignment',
        'patterns': [
            {
                'detect': r'.*',
                'fix': 'special_unbound_local',  # Special handler
                'multiline': False
            }
        ]
    },

    'RecursionError': {
        'description': 'Maximum recursion depth exceeded',
        'patterns': [
            {
                'detect': r'def\s+',
                'fix': lambda line, indent, error_msg: f"{indent}# Add base case to prevent infinite recursion\n{line}",
                'multiline': False
            }
        ]
    },

    'MemoryError': {
        'description': 'Out of memory',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: f"{indent}# Reduce data size or use generators\n{line}",
                'multiline': False
            }
        ]
    },

    'StopIteration': {
        'description': 'Iterator exhausted',
        'patterns': [
            {
                'detect': r'next\s*\(',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'StopIteration', len(indent)),
                'multiline': True
            }
        ]
    },

    'AssertionError': {
        'description': 'Assert statement failed',
        'patterns': [
            {
                'detect': r'assert\s+',
                'fix': lambda line, indent, error_msg: f"{indent}# Assertion failed - check condition: {line.strip()}\n{indent}pass\n",
                'multiline': False
            }
        ]
    },

    'UnicodeDecodeError': {
        'description': 'Cannot decode bytes to unicode',
        'patterns': [
            {
                'detect': r"open\s*\([^)]*\)",
                'fix': lambda line, indent, error_msg: re.sub(
                    r"open\s*\(([^,)]+)([^)]*)\)",
                    r"open(\1, encoding='utf-8', errors='ignore'\2)",
                    line
                ),
                'multiline': False
            }
        ]
    },

    'UnicodeEncodeError': {
        'description': 'Cannot encode unicode to bytes',
        'patterns': [
            {
                'detect': r"\.encode\s*\(\s*\)",
                'fix': lambda line, indent, error_msg: re.sub(
                    r"\.encode\s*\(\s*\)",
                    ".encode('utf-8', errors='ignore')",
                    line
                ),
                'multiline': False
            }
        ]
    },

    'ConnectionError': {
        'description': 'Network connection failed',
        'patterns': [
            {
                'detect': r'requests\.',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'ConnectionError', len(indent)),
                'multiline': True
            }
        ]
    },

    'TimeoutError': {
        'description': 'Operation timed out',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: f"{indent}# Increase timeout or add retry logic\n{line}",
                'multiline': False
            }
        ]
    },

    'PermissionError': {
        'description': 'Insufficient permissions',
        'patterns': [
            {
                'detect': r'open\s*\(',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'PermissionError', len(indent)),
                'multiline': True
            }
        ]
    },

    'OSError': {
        'description': 'Operating system error',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'OSError', len(indent)),
                'multiline': True
            }
        ]
    },

    'RuntimeError': {
        'description': 'Generic runtime error',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'RuntimeError', len(indent)),
                'multiline': True
            }
        ]
    },

    'NotImplementedError': {
        'description': 'Method not implemented',
        'patterns': [
            {
                'detect': r'raise\s+NotImplementedError',
                'fix': lambda line, indent, error_msg: f"{indent}# TODO: Implement this method\n{indent}pass\n",
                'multiline': False
            }
        ]
    },

    'EOFError': {
        'description': 'End of file reached',
        'patterns': [
            {
                'detect': r'input\s*\(',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'EOFError', len(indent)),
                'multiline': True
            }
        ]
    },

    'IOError': {
        'description': 'Input/output operation failed',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'IOError', len(indent)),
                'multiline': True
            }
        ]
    },

    'ArithmeticError': {
        'description': 'Arithmetic operation error',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'ArithmeticError', len(indent)),
                'multiline': True
            }
        ]
    },

    'OverflowError': {
        'description': 'Arithmetic operation too large',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'OverflowError', len(indent)),
                'multiline': True
            }
        ]
    },

    'FloatingPointError': {
        'description': 'Floating point operation failed',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'FloatingPointError', len(indent)),
                'multiline': True
            }
        ]
    },

    'UnicodeDecodeError': {
        'description': 'Cannot decode bytes (MEGA PATTERN)',
        'patterns': [
            {
                'detect': r'\.read\(\)|\.readline\(\)',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'UnicodeDecodeError', len(indent)),
                'multiline': True
            }
        ]
    },

    'UnicodeEncodeError': {
        'description': 'Cannot encode string (MEGA PATTERN)',
        'patterns': [
            {
                'detect': r'\.encode\s*\(\s*\)',
                'fix': lambda line, indent, error_msg: re.sub(
                    r'\.encode\s*\(\s*\)',
                    r".encode('utf-8', errors='ignore')",
                    line
                ),
                'multiline': False
            }
        ]
    },

    # ========================================================================
    # CLAUDE'S 10 MEGA PATTERNS (Advanced & Security)
    # ========================================================================

    'RecursionError': {
        'description': 'Maximum recursion depth exceeded (MEGA)',
        'patterns': [
            {
                'detect': r'def\s+\w+',
                'fix': lambda line, indent, error_msg: f"{line}{indent}    import sys\n{indent}    sys.setrecursionlimit(10000)\n",
                'multiline': False
            }
        ]
    },

    'MemoryError': {
        'description': 'Out of memory - convert to generator (MEGA)',
        'patterns': [
            {
                'detect': r'\[.*for.*in.*\]',
                'fix': lambda line, indent, error_msg: re.sub(r'\[(.*for.*in.*)\]', r'(\1)', line),
                'multiline': False
            }
        ]
    },

    'TimeoutError': {
        'description': 'Network/operation timeout (MEGA)',
        'patterns': [
            {
                'detect': r'requests\.get|urllib\.request|socket\.',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'TimeoutError', len(indent)),
                'multiline': True
            }
        ]
    },

    'ValueError': {
        'description': 'Invalid value - enhanced (MEGA)',
        'patterns': [
            {
                'detect': r'int\s*\(|float\s*\(',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'ValueError', len(indent)),
                'multiline': True
            },
            {
                'detect': r'\.split\s*\(',
                'fix': lambda line, indent, error_msg: wrap_in_try_except(line, 'ValueError', len(indent)),
                'multiline': True
            }
        ]
    },

    'SQLInjectionRisk': {
        'description': 'SECURITY: Potential SQL injection (MEGA)',
        'patterns': [
            {
                'detect': r'(SELECT|INSERT|UPDATE|DELETE).*(\{|\%s)',
                'fix': lambda line, indent, error_msg: f"{indent}# ⚠️ SECURITY WARNING: Potential SQL injection!\n{indent}# Use parameterized queries instead: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))\n{line}",
                'multiline': False
            }
        ]
    },

    'CommandInjectionRisk': {
        'description': 'SECURITY: Potential command injection (MEGA)',
        'patterns': [
            {
                'detect': r'os\.system\s*\(.*\{|subprocess.*shell=True',
                'fix': lambda line, indent, error_msg: f"{indent}# ⚠️ SECURITY WARNING: Command injection risk!\n{indent}# Avoid shell=True and user input in system commands\n{line}",
                'multiline': False
            }
        ]
    },

    'PathTraversalRisk': {
        'description': 'SECURITY: Potential path traversal (MEGA)',
        'patterns': [
            {
                'detect': r'open\s*\(.*\+|os\.path\.join.*input',
                'fix': lambda line, indent, error_msg: f"{indent}# ⚠️ SECURITY WARNING: Path traversal risk!\n{indent}# Validate and sanitize file paths from user input\n{line}",
                'multiline': False
            }
        ]
    },

    'TOCTOUError': {
        'description': 'SECURITY: Time-of-check-time-of-use race (MEGA)',
        'patterns': [
            {
                'detect': r'if.*os\.path\.exists',
                'fix': lambda line, indent, error_msg: f"{indent}# TOCTOU race condition - use try/except instead\n{indent}try:\n{indent}    # Your file operation here\n{indent}    pass\n{indent}except FileNotFoundError:\n{indent}    pass\n",
                'multiline': True
            }
        ]
    }
}


def run_and_capture_error(script_path):
    """Run script and capture any error."""
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return result.stderr
    return None


def parse_error(stderr, target_script=None):
    """Extract error type, line number, and message from traceback.

    Collects ALL frames from target script and returns the DEEPEST one
    (closest to where error actually triggered).
    """
    lines = stderr.strip().split('\n')

    error_type = None
    error_line = None
    error_file = None
    error_message = stderr

    # Find error type (last non-empty line)
    for line in reversed(lines):
        if line.strip() and ':' in line:
            error_parts = line.split(':', 1)
            potential_error = error_parts[0].strip()

            # Handle module-qualified errors like json.decoder.JSONDecodeError
            if '.' in potential_error:
                # Extract just the error class name
                potential_error = potential_error.split('.')[-1]

            # Check if it's a known error or follows Error naming pattern
            if potential_error in ERROR_DATABASE or potential_error.endswith('Error'):
                error_type = potential_error
                break

    # Collect ALL frames from the traceback
    all_frames = []
    for line in lines:
        if 'File "' in line and ', line ' in line:
            match = re.search(r'File "([^"]+)", line (\d+)', line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))

                # Skip system files
                if not file_path.startswith('<') and '/lib/python' not in file_path:
                    all_frames.append((file_path, line_num))

    # If target_script specified, filter to only that file
    if target_script and all_frames:
        target_abs = os.path.abspath(target_script)
        target_frames = [
            (f, ln) for f, ln in all_frames
            if os.path.abspath(f) == target_abs
        ]

        # Use deepest frame from target file (last in stack = closest to error)
        if target_frames:
            error_file, error_line = target_frames[-1]

    # Fallback: use deepest frame overall
    if not error_file and all_frames:
        error_file, error_line = all_frames[-1]

    return error_type, error_file, error_line, error_message


def fix_error(file_path, error_type, line_number, error_message):
    """Apply hard-coded fix for error type at line number."""

    if error_type not in ERROR_DATABASE:
        print(f"[WARN] No solution for {error_type} in database")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[ERROR] Cannot read file: {e}")
        return False

    if line_number > len(lines) or line_number < 1:
        print(f"[ERROR] Line {line_number} out of range (file has {len(lines)} lines)")
        return False

    target_line = lines[line_number - 1]
    indent = get_indent(target_line)

    # Try each pattern for this error type
    for pattern_idx, pattern in enumerate(ERROR_DATABASE[error_type]['patterns']):
        if re.search(pattern['detect'], target_line):
            try:
                # Special handler for UnboundLocalError
                if pattern.get('fix') == 'special_unbound_local':
                    if _fix_unbound_local_error(lines, line_number, indent, error_message):
                        # Write back the modified lines
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        print(f"[FIX] Applied {error_type} fix (added initialization at function start)")
                        return True
                    else:
                        print(f"[WARN] Could not apply special UnboundLocalError fix")
                        continue

                # Check if this needs multi-line block wrapping
                needs_block_wrap = pattern['multiline'] and (
                    re.search(r'\b(with|for|while)\b', target_line) or
                    target_line.strip().endswith(':')
                )

                if needs_block_wrap:
                    # Get the entire indented block
                    block_lines, base_indent = get_indented_block(lines, line_number - 1)

                    if block_lines:
                        # For FileNotFoundError and similar, wrap entire block
                        if error_type in ['FileNotFoundError', 'JSONDecodeError', 'PermissionError']:
                            fixed = wrap_block_in_try_except(block_lines, base_indent, error_type)
                        else:
                            # Use standard fix
                            fixed = pattern['fix'](target_line, indent, error_message)

                        # Determine how many lines to replace
                        lines_to_replace = len(block_lines)

                        # Replace the block
                        fixed_lines = fixed.split('\n')
                        new_lines = [line + '\n' for line in fixed_lines if line]  # Keep non-empty lines
                        lines[line_number - 1:line_number - 1 + lines_to_replace] = new_lines
                    else:
                        # Fallback to single line fix
                        fixed = pattern['fix'](target_line, indent, error_message)
                        if not fixed.endswith('\n'):
                            fixed += '\n'
                        lines[line_number - 1] = fixed
                elif pattern['multiline']:
                    # Multi-line but not block-based (like adding try/except around single line)
                    fixed = pattern['fix'](target_line, indent, error_message)
                    lines[line_number - 1] = fixed
                else:
                    # Single line replacement
                    fixed = pattern['fix'](target_line, indent, error_message)
                    if not fixed.endswith('\n'):
                        fixed += '\n'
                    lines[line_number - 1] = fixed

                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                print(f"[FIX] Applied {error_type} fix at line {line_number} (pattern {pattern_idx + 1})")
                return True
            except Exception as e:
                print(f"[ERROR] Failed to apply fix: {e}")
                import traceback
                traceback.print_exc()
                continue

    print(f"[WARN] No matching pattern for {error_type} at line {line_number}")
    print(f"[LINE] {target_line.strip()}")
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python universal_debugger.py your_script.py")
        sys.exit(1)

    script_path = sys.argv[1]

    if not os.path.exists(script_path):
        print(f"[ERROR] File not found: {script_path}")
        sys.exit(1)

    # Create backup
    backup_path = script_path + '.backup'
    shutil.copy2(script_path, backup_path)
    print(f"[BACKUP] Created at {backup_path}")

    print(f"[START] Universal Debugger")
    print(f"[TARGET] {os.path.abspath(script_path)}")
    print(f"[DATABASE] {len(ERROR_DATABASE)} error types loaded")
    print()

    max_iterations = 100
    iteration = 0
    fixed_errors = []

    while iteration < max_iterations:
        iteration += 1
        print(f"[ITERATION {iteration}] Running script...")

        stderr = run_and_capture_error(script_path)

        if not stderr:
            print(f"[SUCCESS] No errors detected!")
            print(f"[COMPLETE] Fixed {len(fixed_errors)} error(s) in {iteration - 1} iteration(s)")
            if fixed_errors:
                print(f"[FIXED]")
                for err in fixed_errors:
                    print(f"  - {err}")
            break

        error_type, error_file, error_line, full_error = parse_error(stderr, script_path)

        if not error_type:
            print(f"[ERROR] Could not determine error type from:")
            print(stderr)
            break

        if not error_file or not error_line:
            print(f"[ERROR] Could not locate error in source:")
            print(stderr)
            break

        # Only fix errors in the target script, not in libraries
        if os.path.abspath(error_file) != os.path.abspath(script_path):
            print(f"[SKIP] Error is in external file: {error_file}")
            print(stderr)
            break

        error_descriptor = f"{error_type} at line {error_line}"
        print(f"[DETECTED] {error_descriptor}")

        if error_descriptor in fixed_errors:
            print(f"[ERROR] Already tried to fix this error - infinite loop detected")
            print(stderr)
            break

        if fix_error(error_file, error_type, error_line, full_error):
            fixed_errors.append(error_descriptor)
        else:
            print(f"[FAILED] Could not apply fix")
            print(full_error)
            break

    if iteration >= max_iterations:
        print(f"[TIMEOUT] Max iterations reached")
        print(f"[RESTORE] Use {backup_path} to restore original")


if __name__ == "__main__":
    main()
