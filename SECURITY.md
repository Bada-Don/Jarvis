# Security Policy

## Overview

JARVIS is an AI-powered computer automation system that executes commands on your local machine. Security is paramount because JARVIS has the ability to:

- Execute shell commands
- Read and write files
- Control mouse and keyboard
- Access system resources
- Interact with applications

This document outlines our security practices, how to report vulnerabilities, and best practices for users.

## Supported Versions

We provide security updates for the following versions:

| Version | Supported |
| ------- | --------- |
| main    | Yes       |
| < 1.0   | No        |

**Note:** JARVIS is currently in active development. We recommend always using the latest version from the `main` branch.

## Security Architecture

### Multi-Layer Security Model

```
┌─────────────────────────────────────────┐
│         User Authentication             │
│    (Mobile App → Backend Server)        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       Command Validation Layer          │
│   (Planner Model + Input Sanitization)  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Local Client Execution Layer       │
│  (Sandboxed execution with permissions) │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         System-Level Controls           │
│    (Windows permissions, file access)   │
└─────────────────────────────────────────┘
```

### Current Security Measures

1. **Local Execution**: Local client runs on your machine, not in the cloud
2. **API Key Protection**: Gemini/OpenAI keys stored in `.env` files (not committed)
3. **WebSocket Authentication**: Server-client communication over local network
4. **Command Logging**: All commands logged in `debug_logs/` for audit trails
5. **File Path Validation**: Paths sanitized to prevent directory traversal
6. **No Remote Code Execution**: Code is generated locally, not fetched from external sources

## Known Security Considerations

### Current Limitations

WARNING: JARVIS is designed for trusted, single-user environments. The following security features are NOT yet implemented:

- **No user authentication**: Anyone with network access can send commands
- **No command whitelisting**: All commands are executed without restriction
- **No rate limiting**: No protection against command flooding
- **No sandboxing**: Commands run with full user privileges
- **No encryption**: WebSocket communication is not encrypted (local network only)

### Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Malicious commands | High | Use on trusted networks only |
| API key exposure | Medium | Store in `.env`, never commit |
| Unauthorized access | High | Restrict network access to localhost |
| File system access | Medium | Run with limited user privileges |
| Vision pipeline manipulation | Low | Screenshots are local only |

## Best Practices for Users

### Secure Configuration

1. Protect Your API Keys

```env
# backend/.env
GEMINI_API_KEY=your_key_here  # Never commit this file!
```

Add to `.gitignore`:
```
.env
.env.local
.env.backup
```

2. Restrict Network Access

Configure backend to listen on localhost only:

```python
# backend/server.py
if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000)  # Localhost only
```

For mobile app access, use firewall rules to restrict connections.

3. Run with Limited Privileges

- Don't run JARVIS as Administrator unless necessary
- Create a dedicated user account with restricted permissions
- Use Windows User Account Control (UAC)

4. Monitor Command Execution

Regularly review debug logs:

```cmd
cd debug_logs
dir /od  # List by date
```

Check for suspicious commands:
- Unexpected file deletions
- Network requests to unknown hosts
- System configuration changes

5. Secure Your Mobile App

- Use strong device PIN/biometric lock
- Don't install on shared devices
- Keep Expo Go / app updated

### Network Security

Local Network Only (Recommended)

```javascript
// ChatInterface/src/config.js
export const BACKEND_URL = 'http://127.0.0.1:5000';  // Localhost only
```

Trusted Network (If needed)

If using on local network:
1. Use static IP for backend server
2. Configure firewall to allow only trusted devices
3. Consider VPN for remote access

Never expose to public internet without:
- Authentication system
- HTTPS/WSS encryption
- Rate limiting
- Command whitelisting

### Audit and Monitoring

Enable Comprehensive Logging

```python
# local_client/config.py
DEBUG_ENABLED = True
LOG_LEVEL = 'DEBUG'
```

Review Logs Regularly

```cmd
# Check recent sessions
cd debug_logs
type latest_session\execution_log.txt
```

Monitor System Changes

- Check for unexpected files in Desktop/Documents
- Review installed applications
- Monitor network connections

## Reporting a Vulnerability

### What to Report

Please report any security vulnerabilities, including:

- **Authentication bypass**: Ways to execute commands without authorization
- **Privilege escalation**: Methods to gain elevated permissions
- **Code injection**: Ability to inject malicious code into execution plans
- **API key exposure**: Ways to extract API keys from the system
- **Path traversal**: Accessing files outside intended directories
- **Denial of service**: Crashing or hanging the system
- **Data leakage**: Exposing sensitive information in logs or responses

### How to Report

DO NOT create public GitHub issues for security vulnerabilities!

Instead:

1. **Email**: Send details to [harshitashwani@gmail.com]
   - Subject: "JARVIS Security Vulnerability Report"
   - Include "CONFIDENTIAL" in the subject line

2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
   - Your contact information

3. **Encryption** (Optional):
   - For highly sensitive reports, request PGP key via email

### What to Expect

| Timeline | Action |
|----------|--------|
| 24-48 hours | Initial acknowledgment |
| 7 days | Preliminary assessment |
| 30 days | Fix developed and tested |
| 45 days | Security patch released |
| 60 days | Public disclosure (if appropriate) |

### Responsible Disclosure

We follow responsible disclosure practices:

1. **Private reporting**: Report privately first
2. **Coordinated disclosure**: We'll work with you on timing
3. **Credit**: You'll be credited in release notes (if desired)
4. **No retaliation**: We won't take legal action against good-faith researchers

### Bug Bounty

Currently, JARVIS does not offer a bug bounty program. However:

- Security researchers will be credited in CONTRIBUTORS.md
- Significant findings will be acknowledged in release notes
- We may offer recognition/swag for critical discoveries (future)

## Security Roadmap

### Planned Security Enhancements

**Phase 1: Authentication & Authorization (Q2 2026)**
- [ ] User authentication system
- [ ] API key management
- [ ] Session management
- [ ] Role-based access control

**Phase 2: Command Security (Q3 2026)**
- [ ] Command whitelisting
- [ ] Dangerous command warnings
- [ ] User confirmation for destructive actions
- [ ] Rate limiting

**Phase 3: Network Security (Q4 2026)**
- [ ] HTTPS/WSS encryption
- [ ] Certificate pinning
- [ ] Network access controls
- [ ] VPN support

**Phase 4: Advanced Security (2027)**
- [ ] Sandboxed execution environment
- [ ] Command auditing dashboard
- [ ] Anomaly detection
- [ ] Multi-factor authentication

## Security Best Practices for Developers

### Code Review Checklist

When contributing code, ensure:

- [ ] No hardcoded API keys or credentials
- [ ] Input validation for all user inputs
- [ ] Path sanitization for file operations
- [ ] Error messages don't leak sensitive info
- [ ] Logging doesn't include API keys or passwords
- [ ] Dependencies are up-to-date
- [ ] No use of `eval()` or `exec()` with user input

### Secure Coding Examples

BAD: Command Injection Vulnerability
```python
# DON'T DO THIS
command = f"del {user_input}"
os.system(command)  # Vulnerable to injection
```

GOOD: Sanitized Input
```python
# DO THIS
import shlex
safe_path = shlex.quote(user_input)
command = f"del {safe_path}"
subprocess.run(command, shell=True)
```

BAD: Path Traversal
```python
# DON'T DO THIS
file_path = f"uploads/{user_filename}"
with open(file_path, 'r') as f:  # Can access ../../../etc/passwd
    content = f.read()
```

GOOD: Path Validation
```python
# DO THIS
import os
safe_path = os.path.normpath(f"uploads/{user_filename}")
if not safe_path.startswith("uploads/"):
    raise ValueError("Invalid path")
with open(safe_path, 'r') as f:
    content = f.read()
```

### Dependency Security

**Check for vulnerabilities:**
```cmd
pip install safety
safety check -r requirements.txt
```

**Keep dependencies updated:**
```cmd
pip list --outdated
pip install --upgrade package_name
```

## Incident Response

### If You Suspect a Security Breach

1. **Stop JARVIS immediately**
   - Close local client
   - Stop backend server
   - Disconnect from network (if needed)

2. **Assess the damage**
   - Check debug logs for suspicious activity
   - Review recent file changes
   - Check for unauthorized access

3. **Contain the issue**
   - Change API keys
   - Update passwords
   - Revoke access tokens

4. **Report the incident**
   - Email security team
   - Provide logs and evidence
   - Document timeline

5. **Recover**
   - Update to latest version
   - Apply security patches
   - Restore from backup (if needed)

## Compliance

### Data Privacy

JARVIS processes data locally:
- **No cloud storage**: All data stays on your machine
- **No telemetry**: We don't collect usage data
- **No tracking**: No analytics or tracking scripts

### API Usage

When using Gemini/OpenAI APIs:
- Review their privacy policies
- Understand data retention policies
- Consider using local models (future feature)

## Contact

For security-related questions:
- **Email**: [harshitashwani@gmail.com]
- **Subject**: "JARVIS Security Inquiry"

For general questions:
- **GitHub Issues**: https://github.com/Bada-Don/Jarvis/issues
- **Discussions**: https://github.com/Bada-Don/Jarvis/discussions

---

**Remember**: Security is a shared responsibility. Use JARVIS responsibly and report vulnerabilities promptly.

*"I am Iron Man. The suit and I are one."* – Tony Stark

Let's keep JARVIS secure together.
