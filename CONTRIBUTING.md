# Contributing to JARVIS

First off, thank you for considering contributing to JARVIS! It's people like you who make JARVIS a powerful tool for computer automation.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [harshitashwani@gmail.com].

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include as many details as possible using our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

**Good bug reports include:**
- Clear, descriptive title
- Exact steps to reproduce
- Expected vs actual behavior
- Debug logs from `debug_logs/` folder
- System information (Windows version, Python version)
- Screenshots or videos (especially for vision pipeline issues)

### Suggesting Features

Feature suggestions are tracked as GitHub issues. Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- Clear use case and problem statement
- Proposed solution with examples
- How it fits into JARVIS's multi-plane architecture
- Potential impact on performance/stability

### Improving Documentation

Documentation improvements are always welcome:
- Fix typos or clarify confusing sections
- Add examples or tutorials
- Improve installation instructions
- Document undocumented features
- Translate documentation (future)

### Code Contributions

We welcome contributions in these areas:

**High Priority:**
- Bug fixes (especially in vision pipeline)
- Performance optimizations
- Test coverage improvements
- Error handling enhancements

**Feature Development:**
- New execution step types
- Additional automation modes
- Cross-platform support (Mac/Linux)
- Voice activation
- Multi-monitor support

**Architecture Improvements:**
- Code refactoring for maintainability
- Better error messages
- Improved logging
- Configuration management

## Development Setup

### Prerequisites

- Windows 10/11 (64-bit)
- Python 3.10+
- Node.js 18+
- Git
- Tesseract OCR
- Gemini API key

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```cmd
   git clone https://github.com/YOUR_USERNAME/Jarvis.git
   cd Jarvis
   ```

3. Add upstream remote:
   ```cmd
   git remote add upstream https://github.com/Bada-Don/Jarvis.git
   ```

### Backend Setup

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```env
GEMINI_API_KEY=your_key_here
```

Download FastSAM weights to `backend/weights/FastSAM-s.pt`

### Local Client Setup

```cmd
cd local_client
python -m venv venv
venv\Scripts\activate
pip install -r ..\backend\requirements.txt
pip install pywin32 comtypes
```

Configure `config.py` with your paths.

### Mobile App Setup

```cmd
cd ChatInterface
npm install
```

Update backend URL in `src/config.js`

### Verify Installation

Start all three components:

```cmd
# Terminal 1
cd backend
venv\Scripts\activate
python server.py

# Terminal 2
cd local_client
venv\Scripts\activate
python client.py

# Terminal 3
cd ChatInterface
npx expo start
```

Test with: "Open Notepad"

## Contribution Workflow

### 1. Create a Branch

```cmd
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/changes
- `perf/` - Performance improvements

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed
- Add tests for new features

### 3. Test Your Changes

```cmd
# Run existing tests
cd backend
pytest test_*.py

# Test manually with various commands
# Check debug logs for errors
```

### 4. Commit Your Changes

```cmd
git add .
git commit -m "feat: add voice activation support"
```

See [Commit Message Guidelines](#commit-message-guidelines) below.

### 5. Keep Your Branch Updated

```cmd
git fetch upstream
git rebase upstream/main
```

### 6. Push to Your Fork

```cmd
git push origin feature/your-feature-name
```

### 7. Create Pull Request

- Go to your fork on GitHub
- Click "New Pull Request"
- Fill out the PR template
- Link related issues

## Coding Standards

### Python Style Guide

Follow PEP 8 with these specifics:

```python
# Use descriptive variable names
screenshot_path = "screenshot.png"  # Good
sp = "screenshot.png"  # Bad

# Add docstrings to functions
def execute_shell_command(command: str) -> dict:
    """
    Execute a shell command and return the result.
    
    Args:
        command: The shell command to execute
        
    Returns:
        dict: Contains 'success', 'output', and 'error' keys
    """
    pass

# Use type hints
def map_targets(image_path: str, targets: list[str]) -> dict[str, int]:
    pass

# Handle errors gracefully
try:
    result = execute_command(cmd)
except Exception as e:
    logger.error(f"Command failed: {e}")
    return {"success": False, "error": str(e)}
```

### JavaScript/React Native Style

```javascript
// Use const/let, not var
const serverUrl = 'http://localhost:5000';

// Use arrow functions
const handleSend = (message) => {
  socket.emit('execute_command', { command: message });
};

// Destructure props
const ChatMessage = ({ text, timestamp, isUser }) => {
  return <View>...</View>;
};
```

### Architecture Principles

**Respect the Execution Priority:**
```
1. Shell commands (fastest)
2. File operations (fast)
3. Keyboard actions (medium)
4. Vision pipeline (slowest)
```

**Always prefer faster methods:**
```python
# Good: Use shell command
{"type": "shell_command", "command": "mkdir folder"}

# Bad: Use visual click to create folder via GUI
{"type": "visual_click", "target": "new_folder_button"}
```

**Add comprehensive logging:**
```python
logger.info(f"Executing step {step['order']}: {step['desc']}")
logger.debug(f"Command: {step['command']}")
# ... execute ...
logger.info(f"Step {step['order']} completed successfully")
```

## Testing Guidelines

### Unit Tests

Add tests for new functions:

```python
# test_file_operations.py
def test_write_file():
    """Test file writing functionality"""
    result = write_file("test.txt", "Hello World")
    assert result["success"] == True
    assert os.path.exists("test.txt")
    os.remove("test.txt")
```

### Integration Tests

Test complete workflows:

```python
def test_create_and_run_python_file():
    """Test creating and executing a Python file"""
    plan = {
        "sequence": [
            {"type": "write_file", "path": "test.py", "content": "print('test')"},
            {"type": "shell_command", "command": "python test.py"}
        ]
    }
    result = execute_plan(plan)
    assert result["success"] == True
```

### Manual Testing Checklist

Before submitting a PR, test:

- [ ] Basic commands work (open app, create file)
- [ ] File operations work correctly
- [ ] Shell commands execute properly
- [ ] Vision pipeline works (if modified)
- [ ] Error handling works (invalid commands)
- [ ] Debug logs are generated
- [ ] No crashes or exceptions

## Documentation

### Code Comments

```python
# Good: Explain WHY, not WHAT
# Use shell command instead of GUI to avoid vision pipeline overhead
result = subprocess.run(command, shell=True)

# Bad: Obvious comment
# Run the command
result = subprocess.run(command, shell=True)
```

### README Updates

If your change affects:
- Installation process → Update installation section
- New features → Add to features list
- Configuration → Update configuration section
- Architecture → Update architecture diagrams

### API Documentation

Document new functions:

```python
def execute_plan(plan: dict, debug_folder: str = None) -> dict:
    """
    Execute a multi-step automation plan.
    
    This function processes each step in the plan according to the
    multi-plane execution architecture, prioritizing faster methods.
    
    Args:
        plan: Dictionary containing 'mode' and 'sequence' keys
        debug_folder: Optional path for debug logs
        
    Returns:
        dict: Execution result with 'success', 'message', and 'steps_completed'
        
    Raises:
        ValueError: If plan format is invalid
        RuntimeError: If critical step fails
        
    Example:
        >>> plan = {"mode": "general", "sequence": [...]}
        >>> result = execute_plan(plan)
        >>> print(result['success'])
        True
    """
```

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(planner): add voice activation support

Implemented voice command recognition using speech-to-text API.
Commands can now be triggered by saying "Hey JARVIS".

Closes #123
```

```
fix(vision): improve FastSAM detection accuracy

- Adjusted confidence threshold to 0.7
- Added preprocessing for low-light screenshots
- Fixed bounding box overlap issues

Fixes #456
```

```
docs(readme): update installation instructions

Added troubleshooting section for Tesseract installation issues.
```

### Rules

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor" not "moves cursor")
- First line max 72 characters
- Reference issues and PRs in footer

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No merge conflicts
- [ ] Commit messages follow guidelines

### PR Template

Your PR should include:

1. **Description**: What does this PR do?
2. **Motivation**: Why is this change needed?
3. **Changes**: List of specific changes made
4. **Testing**: How was this tested?
5. **Screenshots**: For UI changes
6. **Checklist**: Completed items from above

### Review Process

1. **Automated checks**: CI/CD runs tests
2. **Code review**: Maintainer reviews code
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves PR
5. **Merge**: PR is merged to main

### After Merge

- Delete your branch
- Update your fork:
  ```cmd
  git checkout main
  git pull upstream main
  git push origin main
  ```

## Getting Help

### Questions?

- **General questions**: Open a [discussion](https://github.com/Bada-Don/Jarvis/discussions)
- **Bug reports**: Use [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- **Feature ideas**: Use [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- **Security issues**: See [SECURITY.md](SECURITY.md)

### Resources

- [README.md](README.md) - Project overview
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Community guidelines
- [SECURITY.md](SECURITY.md) - Security policy
- Debug logs - Check `debug_logs/` folder

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in commit history

Thank you for making JARVIS better!

---

*"No amount of money ever bought a second of time."* – Tony Stark

Let's make every contribution count.
