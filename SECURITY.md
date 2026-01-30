# Security Policy

## Scope

This is a portfolio project demonstrating Python automation, knowledge management system architecture, and secure development practices for personal productivity tools.

## Supported Versions

This project is maintained as a personal tool and portfolio demonstration.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

I appreciate security feedback and use it to improve the tool:

- **Email:** violet@violetfigueroa.com
- **Response Time:** Best effort (typically 2-7 days)
- **Recognition:** Security findings will be acknowledged in this SECURITY.md file

## Security Features Implemented

This project demonstrates understanding of the following security concepts:

### File System Security
- **Path validation** prevents directory traversal attacks
- **Input sanitization** for file names and paths
- **Safe file operations** with proper error handling
- **Permission verification** before file operations
- **Secure temp file handling** during processing

### Input Validation & Sanitization
- **File type validation** for supported formats (.md, .pdf, .txt)
- **Metadata validation** for tagging and organization
- **Path normalization** to prevent injection attacks
- **Size limits** to prevent resource exhaustion
- **Content validation** before processing

### Data Security
- **No external network calls** - Operates entirely offline
- **Local-only processing** - Data never leaves your machine
- **No telemetry or tracking** - Privacy-first design
- **Transparent operations** - All actions logged clearly
- **User data control** - Complete ownership of processed files

### Secure Development Practices
- **Dependency management** with requirements.txt
- **Virtual environment isolation** recommended
- **Error handling** without exposing sensitive paths
- **Code organization** separates critical from general code
- **Logging practices** don't expose sensitive information

### Testing & Quality
- **Pytest integration** for security-relevant code paths
- **Integration tests** validate file operations safely
- **Edge case handling** for malformed inputs
- **Error recovery** prevents data loss
- **Dry-run mode** for safe testing

## Security Considerations for Users

When using this tool:

1. **Review file operations** - Always check what files will be modified
2. **Backup your data** - Keep backups before bulk operations
3. **Use virtual environments** - Isolate Python dependencies
4. **Keep dependencies updated** - Run `pip list --outdated` regularly
5. **Review processed output** - Verify results meet expectations
6. **Don't process untrusted files** - Designed for your own notes only

## Known Limitations

As a personal automation tool:

- **No authentication/authorization** - Designed for local single-user use
- **No encryption** - Relies on filesystem permissions
- **No audit logging** - Not designed for compliance requirements
- **Basic malware checking** - Assumes trusted input files
- **No sandboxing** - Processes files directly

This tool is **not designed for**:
- Multi-user environments
- Web deployment or remote access
- Processing untrusted or malicious files
- Enterprise compliance requirements
- Shared hosting environments

## Security Mindset

This project demonstrates security principles even in a personal tool:

1. **Secure by design** - Safety mechanisms from day one
2. **Defense in depth** - Multiple validation layers
3. **Fail securely** - Errors don't corrupt data
4. **Privacy-first** - No external data transmission
5. **Transparent operations** - User always knows what's happening

## Dependencies Security

Key dependencies and their security considerations:

- **Python 3.11+** - Modern Python with security patches
- **pytest** - Testing framework
- **bandit** - Security linting (if configured)
- **safety** - Dependency vulnerability checking (if configured)

Check for vulnerabilities:
```bash
pip install safety
safety check
```

## Security Testing

Recommended security testing before major updates:

```bash
# Check for known vulnerabilities in dependencies
pip install safety
safety check

# Run security linter
pip install bandit
bandit -r src/

# Run all tests including edge cases
pytest tests/ -v
```

## Security Acknowledgments

None at this time. Be the first to provide constructive security feedback!

---

**Last Updated:** January 30, 2026  
**Project Status:** Active Personal Tool / Portfolio Demonstration  
**Privacy:** No telemetry, no network calls, completely local operation
