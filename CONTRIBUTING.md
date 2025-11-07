# Contributing to Bug-Be-Gone

Thank you for considering contributing! 🎉

## How to Contribute

### Adding New Error Patterns

Found an error type not in ERROR_DATABASE? Here's how to add it:

1. **Capture the Error Pattern**
   ```bash
   DEBUG_MODE=development python mode_aware_debugger.py your_script.py
   ```
   This logs unknown errors to `unknown_errors.json`

2. **Add to ERROR_DATABASE**
   Edit `universal_debugger.py`:
   ```python
   'YourErrorType': {
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

3. **Test It**
   ```bash
   DEBUG_MODE=production python mode_aware_debugger.py your_script.py
   ```
   Verify the error is fixed correctly.

4. **Submit PR**
   - Fork the repo
   - Create branch: `git checkout -b add-error-type-XYZ`
   - Commit: `git commit -m "Add XYZ error pattern"`
   - Push: `git push origin add-error-type-XYZ`
   - Open Pull Request

### Improving Documentation

- Fix typos → Open PR
- Add examples → Open PR
- Clarify confusing sections → Open Issue first

### Reporting Bugs

Use GitHub Issues with:
- Python version
- Operating system
- Error message
- Minimal reproducible example

### Code Style

- Follow existing style
- Keep functions small and focused
- Add docstrings
- Test thoroughly

## Development Setup

```bash
git clone https://github.com/Ninja1232123/Bug-Be-Gone
cd Bug-Be-Gone

# Test everything works
python demo_wow.py
```

## Questions?

Open an issue or discussion on GitHub.

---

**Thank you for making Bug-Be-Gone better!** 🚀
