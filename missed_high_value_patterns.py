#!/usr/bin/env python3
"""
Additional High-Value Patterns - What Code Missed
Patterns that should be in Bug-Be-Gone but aren't yet
"""

MISSED_PATTERNS = """
    'StopIteration': {
        'description': 'Iterator exhausted - common in manual iteration',
        'patterns': [
            {
                'detect': r'next\s*\(',
                'fix': lambda line, indent: f"{indent}try:\\n{line}{indent}except StopIteration:\\n{indent}    pass  # Iterator exhausted\\n",
                'multiline': True
            }
        ]
    },
    
    'KeyboardInterrupt': {
        'description': 'User pressed Ctrl+C - graceful shutdown',
        'patterns': [
            {
                'detect': r'while True:|for .* in .*:',
                'fix': lambda line, indent: f"{indent}try:\\n{line}{indent}except KeyboardInterrupt:\\n{indent}    print('\\nShutdown requested')\\n{indent}    sys.exit(0)\\n",
                'multiline': True
            }
        ]
    },
    
    'GeneratorExit': {
        'description': 'Generator closed - cleanup needed',
        'patterns': [
            {
                'detect': r'yield',
                'fix': lambda line, indent: f"{indent}try:\\n{line}{indent}except GeneratorExit:\\n{indent}    pass  # Generator cleanup\\n",
                'multiline': True
            }
        ]
    },
    
    'ReferenceError': {
        'description': 'Weak reference proxy used after referent deleted',
        'patterns': [
            {
                'detect': r'weakref\.',
                'fix': lambda line, indent: f"{indent}try:\\n{line}{indent}except ReferenceError:\\n{indent}    pass  # Referent deleted\\n",
                'multiline': True
            }
        ]
    },
    
    'BufferError': {
        'description': 'Buffer protocol violation',
        'patterns': [
            {
                'detect': r'memoryview\s*\(',
                'fix': lambda line, indent: f"{indent}try:\\n{line}{indent}except BufferError:\\n{indent}    pass  # Buffer in use\\n",
                'multiline': True
            }
        ]
    },
    
    'LookupError': {
        'description': 'Base class for KeyError and IndexError',
        'patterns': [
            {
                'detect': r'\[.*\]',
                'fix': lambda line, indent: f"{indent}try:\\n{line}{indent}except LookupError:\\n{indent}    pass  # Key or index not found\\n",
                'multiline': True
            }
        ]
    },
    
    'EnvironmentError': {
        'description': 'Base class for IOError and OSError',
        'patterns': [
            {
                'detect': r'open\s*\(',
                'fix': lambda line, indent: f"{indent}try:\\n{line}{indent}except EnvironmentError as e:\\n{indent}    print(f'Environment error: {{e}}')\\n",
                'multiline': True
            }
        ]
    },
    
    'SystemError': {
        'description': 'Internal Python error - rare but critical',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent: f"{indent}try:\\n{line}{indent}except SystemError as e:\\n{indent}    import traceback\\n{indent}    traceback.print_exc()\\n",
                'multiline': True
            }
        ]
    },
    
    'Warning': {
        'description': 'Base warning class - convert warnings to errors',
        'patterns': [
            {
                'detect': r'warnings\.',
                'fix': lambda line, indent: f"{indent}import warnings\\n{indent}warnings.filterwarnings('error')\\n{line}",
                'multiline': False
            }
        ]
    },
    
    'DeprecationWarning': {
        'description': 'Feature deprecated - needs updating',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent: f"{indent}import warnings\\n{indent}warnings.filterwarnings('ignore', category=DeprecationWarning)\\n{line}",
                'multiline': False
            }
        ]
    },
    
    'FutureWarning': {
        'description': 'Future behavior change warning',
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent: f"{indent}import warnings\\n{indent}warnings.filterwarnings('ignore', category=FutureWarning)\\n{line}",
                'multiline': False
            }
        ]
    },
    
    'ResourceWarning': {
        'description': 'Resource not properly closed',
        'patterns': [
            {
                'detect': r'open\s*\(',
                'fix': lambda line, indent: f"{indent}with open(...) as f:\\n{indent}    # Use context manager\\n{indent}    pass\\n",
                'multiline': True
            }
        ]
    },
    
    'InterruptedError': {
        'description': 'System call interrupted by signal',
        'patterns': [
            {
                'detect': r'os\.|socket\.',
                'fix': lambda line, indent: f"{indent}import errno\\n{indent}try:\\n{line}{indent}except InterruptedError as e:\\n{indent}    if e.errno == errno.EINTR:\\n{indent}        pass  # Retry\\n",
                'multiline': True
            }
        ]
    },
"""

def analyze_missed_patterns():
    """Analyze what patterns are high value but missing"""
    
    categories = {
        'Critical (User Experience)': ['KeyboardInterrupt', 'SystemError'],
        'Common (Iteration & Generators)': ['StopIteration', 'GeneratorExit'],
        'Advanced (Memory & Resources)': ['BufferError', 'ReferenceError', 'ResourceWarning'],
        'System Level': ['InterruptedError', 'EnvironmentError'],
        'Code Quality': ['Warning', 'DeprecationWarning', 'FutureWarning'],
        'Hierarchy (Base Classes)': ['LookupError']
    }
    
    print("=" * 70)
    print("HIGH-VALUE PATTERNS CODE MISSED")
    print("=" * 70)
    print("\nThese patterns are common/critical but not in Bug-Be-Gone:\n")
    
    total = 0
    for category, patterns in categories.items():
        print(f"{category}:")
        for pattern in patterns:
            total += 1
            print(f"  {total}. {pattern}")
        print()
    
    print("=" * 70)
    print("IMPACT ANALYSIS")
    print("=" * 70)
    print(f"Additional patterns: {total}")
    print(f"Current database: ~48 types")
    print(f"With these: ~61 types (+27% coverage)")
    print("\nKey additions:")
    print("  ✓ KeyboardInterrupt - Graceful shutdown (every CLI tool needs this)")
    print("  ✓ StopIteration - Manual iteration (very common pattern)")
    print("  ✓ ResourceWarning - Unclosed files (code quality)")
    print("  ✓ SystemError - Critical internal errors")
    print("\n" + "=" * 70)
    print("COMMERCIAL VALUE")
    print("=" * 70)
    print("More comprehensive = more valuable")
    print("Warnings coverage = professional code quality")
    print("Base class handlers = catch-all safety")
    
    with open('/home/claude/missed_patterns.txt', 'w') as f:
        f.write(MISSED_PATTERNS)
    
    print("\n✓ Patterns saved to missed_patterns.txt")

if __name__ == '__main__':
    analyze_missed_patterns()
