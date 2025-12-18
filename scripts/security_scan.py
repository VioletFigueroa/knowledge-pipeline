import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Set

# --- Configuration ---

# Regex patterns for PII and Secrets
PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone_us": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "api_key_generic": r"(?i)(api_key|apikey|secret|token|password|passwd|pwd)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{8,}['\"]",
    "private_key_header": r"-----BEGIN [A-Z]+ PRIVATE KEY-----",
    "social_security": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d{4}[- ]?){3}\d{4}\b",
}

# Keywords that might indicate sensitive content
KEYWORDS = [
    "confidential",
    "private",
    "do not share",
    "internal use only",
    "personal",
    "diary",
    "journal",
    "login",
    "credentials",
]

# Files and directories to always ignore during scan
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    "node_modules",
    ".idea",
    ".vscode",
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
}

class SecurityScanner:
    def __init__(self, root_dir: str, verbose: bool = False):
        self.root_dir = Path(root_dir)
        self.verbose = verbose
        self.issues_found = 0
        self.files_scanned = 0

    def scan(self):
        print(f"🔒 Starting Security Scan on: {self.root_dir}")
        print("-" * 50)

        results: Dict[str, List[str]] = {}

        for root, dirs, files in os.walk(self.root_dir):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                file_path = Path(root) / file
                
                if file_path.suffix.lower() in IGNORE_EXTENSIONS:
                    continue

                # Skip the scanner script itself
                if file_path.name == "security_scan.py":
                    continue

                self.files_scanned += 1
                file_issues = self._scan_file(file_path)
                
                if file_issues:
                    results[str(file_path)] = file_issues
                    self.issues_found += 1

        self._print_report(results)

    def _scan_file(self, file_path: Path) -> List[str]:
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check Regex Patterns
                for name, pattern in PATTERNS.items():
                    matches = re.findall(pattern, content)
                    if matches:
                        # Obfuscate match in report
                        sample = matches[0][:4] + "***" 
                        issues.append(f"Pattern Match [{name}]: Found {len(matches)} instance(s) (e.g., {sample})")

                # Check Keywords
                content_lower = content.lower()
                for keyword in KEYWORDS:
                    if keyword in content_lower:
                        issues.append(f"Keyword Match: '{keyword}' found")

        except Exception as e:
            if self.verbose:
                print(f"⚠️ Could not read {file_path}: {e}")
        
        return issues

    def _print_report(self, results: Dict[str, List[str]]):
        print(f"\n📊 Scan Complete.")
        print(f"Files Scanned: {self.files_scanned}")
        print(f"Files with Issues: {self.issues_found}")
        print("-" * 50)

        if not results:
            print("✅ No PII or secrets detected in scanned files.")
            print("   (Note: This is a heuristic scan. Always manually review before publishing.)")
        else:
            print("⚠️  POTENTIAL ISSUES FOUND:")
            for file_path, issues in results.items():
                print(f"\n📄 {file_path}")
                for issue in issues:
                    print(f"   - {issue}")
            
            print("\n❌ Please review these files before committing to GitHub.")

def main():
    parser = argparse.ArgumentParser(description="Scan files for PII and secrets.")
    parser.add_argument("--dir", type=str, default=".", help="Directory to scan (default: current dir)")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    scanner = SecurityScanner(args.dir, args.verbose)
    scanner.scan()

if __name__ == "__main__":
    main()
