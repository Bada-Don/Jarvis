# JARVIS FunctionGemma Integration - Documentation Index

## Quick Navigation

This index helps you find the right documentation for your needs.

---

## I want to...

### Use JARVIS with the new function calling interface

→ **[USER_GUIDE.md](USER_GUIDE.md)**

Topics covered:
- Getting started and installation
- Using the function calling interface
- Available functions (25+ functions)
- Common tasks and examples
- Migration from legacy mode
- Troubleshooting common issues

---

### Understand the architecture and design

→ **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**

Topics covered:
- Architecture overview
- Core components and their responsibilities
- Design decisions and rationale
- Data models and interfaces
- Code examples
- Best practices

---

### Add new functions to JARVIS

→ **[EXTENSIBILITY_GUIDE.md](EXTENSIBILITY_GUIDE.md)**

Topics covered:
- Step-by-step guide to adding functions
- Function schema format
- Registration process
- Testing requirements
- Complete examples
- Common patterns
- Checklist

---

### Fix issues or debug problems

→ **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

Topics covered:
- Quick diagnostics
- Common issues and solutions
- Advanced troubleshooting techniques
- Error messages reference
- Performance optimization
- Getting help

---

### Get a quick overview

→ **[README.md](README.md)**

Topics covered:
- Project overview
- Quick start guide
- Available functions list
- Architecture diagram
- Examples
- Project structure

---

## Documentation by Role

### For End Users

1. **[README.md](README.md)** - Start here for overview
2. **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user guide
3. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - When things go wrong

### For Developers

1. **[README.md](README.md)** - Start here for overview
2. **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Architecture and design
3. **[EXTENSIBILITY_GUIDE.md](EXTENSIBILITY_GUIDE.md)** - Adding new functions
4. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Debugging and optimization

### For Contributors

1. **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Understand the codebase
2. **[EXTENSIBILITY_GUIDE.md](EXTENSIBILITY_GUIDE.md)** - How to contribute
3. **[Requirements](.kiro/specs/functiongemma-integration/requirements.md)** - Formal requirements
4. **[Design](.kiro/specs/functiongemma-integration/design.md)** - Detailed design
5. **[Tasks](.kiro/specs/functiongemma-integration/tasks.md)** - Implementation plan

---

## Documentation by Topic

### Getting Started

- [README.md](README.md) - Quick start
- [USER_GUIDE.md](USER_GUIDE.md) - Installation and first command

### Using Functions

- [USER_GUIDE.md](USER_GUIDE.md) - Available functions and examples
- [README.md](README.md) - Function categories overview

### Architecture

- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Complete architecture
- [Design Document](.kiro/specs/functiongemma-integration/design.md) - Detailed design

### Adding Functions

- [EXTENSIBILITY_GUIDE.md](EXTENSIBILITY_GUIDE.md) - Step-by-step guide
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Function schema format

### Testing

- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Testing requirements
- [EXTENSIBILITY_GUIDE.md](EXTENSIBILITY_GUIDE.md) - Writing tests

### Troubleshooting

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [USER_GUIDE.md](USER_GUIDE.md) - User troubleshooting section

---

## Specification Documents

Located in `.kiro/specs/functiongemma-integration/`:

### [requirements.md](.kiro/specs/functiongemma-integration/requirements.md)
Formal requirements using EARS patterns and INCOSE quality rules.

**Contents**:
- 12 main requirements
- Acceptance criteria for each requirement
- Glossary of terms
- User stories

### [design.md](.kiro/specs/functiongemma-integration/design.md)
Detailed design document with architecture and correctness properties.

**Contents**:
- Architecture overview
- Component specifications
- Data models
- 39 correctness properties
- Error handling strategy
- Testing strategy
- Migration plan

### [tasks.md](.kiro/specs/functiongemma-integration/tasks.md)
Implementation plan with discrete tasks.

**Contents**:
- 24 main tasks
- Sub-tasks for each main task
- Requirements references
- Checkpoints
- Testing tasks

---

## Code Examples

### Demo Files

- **[demo_functiongemma_service.py](demo_functiongemma_service.py)** - Service usage examples
- **[extensibility_example.py](extensibility_example.py)** - Adding functions example

### Test Files

All test files follow the pattern `test_*.py`:

- `test_folder_operations.py` - Folder operation tests
- `test_file_operations.py` - File operation tests
- `test_keyboard_operations.py` - Keyboard operation tests
- `test_mouse_operations.py` - Mouse operation tests
- `test_window_management.py` - Window management tests
- `test_function_registry.py` - Registry tests
- `test_function_parser.py` - Parser tests
- `test_function_executor_basic.py` - Executor tests
- `test_functiongemma_service.py` - Service tests

---

## Quick Reference

### Common Tasks

| Task | Documentation |
|------|---------------|
| Install JARVIS | [USER_GUIDE.md](USER_GUIDE.md) → Getting Started |
| Execute a command | [USER_GUIDE.md](USER_GUIDE.md) → Using the Function Calling Interface |
| Add a new function | [EXTENSIBILITY_GUIDE.md](EXTENSIBILITY_GUIDE.md) → Step-by-Step Guide |
| Fix an error | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) → Common Issues |
| Understand architecture | [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) → Architecture Overview |
| Write tests | [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) → Testing Requirements |
| Migrate from legacy | [USER_GUIDE.md](USER_GUIDE.md) → Migration from Legacy Mode |

### Common Questions

| Question | Answer |
|----------|--------|
| How do I use JARVIS? | [USER_GUIDE.md](USER_GUIDE.md) |
| What functions are available? | [USER_GUIDE.md](USER_GUIDE.md) → Available Functions |
| How do I add a function? | [EXTENSIBILITY_GUIDE.md](EXTENSIBILITY_GUIDE.md) |
| Why is it slow? | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) → Slow Performance |
| How does it work? | [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) → Architecture |
| Where are the tests? | `test_*.py` files in backend/ |

---

## Documentation Standards

All documentation follows these standards:

### Structure
- Clear table of contents
- Logical section organization
- Progressive disclosure (simple → complex)
- Cross-references between documents

### Content
- Clear, concise language
- Code examples for concepts
- Step-by-step instructions
- Troubleshooting tips
- Best practices

### Format
- Markdown format
- Code blocks with syntax highlighting
- Tables for reference information
- Diagrams where helpful

---

## Contributing to Documentation

### Improving Documentation

1. Identify what's unclear or missing
2. Create or update the relevant document
3. Follow the documentation standards
4. Test examples and instructions
5. Submit pull request

### Documentation Checklist

- [ ] Clear and concise
- [ ] Code examples work
- [ ] Cross-references are correct
- [ ] Follows markdown standards
- [ ] Spell-checked
- [ ] Reviewed by another person

---

## Getting Help

### Can't Find What You Need?

1. Check this index for the right document
2. Use Ctrl+F to search within documents
3. Check the troubleshooting guide
4. Look at code examples
5. Ask for help (see below)

### Still Need Help?

- **Questions**: Open a discussion
- **Issues**: Report with details
- **Suggestions**: Propose improvements
- **Contributions**: Submit pull requests

---

## Document Versions

| Document | Version | Last Updated |
|----------|---------|--------------|
| README.md | 1.0.0 | December 2025 |
| USER_GUIDE.md | 1.0.0 | December 2025 |
| DEVELOPER_GUIDE.md | 1.0.0 | December 2025 |
| EXTENSIBILITY_GUIDE.md | 1.0.0 | December 2025 |
| TROUBLESHOOTING.md | 1.0.0 | December 2025 |
| DOCUMENTATION_INDEX.md | 1.0.0 | December 2025 |

---

**Happy coding!**
