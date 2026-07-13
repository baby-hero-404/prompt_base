import os
import sys
import re

def security_scan(target_dir):
    print(f"🛡️ Running Security Scan on: {target_dir}")
    
    issues = []
    
    # 1. Search for Secrets (Hardcoded Keys)
    secret_patterns = [
        (r'API_KEY\s*=\s*["\'][^"\']{10,}["\']', "Potential hardcoded API Key"),
        (r'PASSWORD\s*=\s*["\'][^"\']{5,}["\']', "Potential hardcoded Password"),
        (r'SECRET\s*=\s*["\'][^"\']{10,}["\']', "Potential hardcoded Secret"),
        (r'ssh-rsa\s+[A-Za-z0-0+/=]{10,}', "Potential Private Key/Public Key"),
    ]
    
    # 2. Search for Unsafe Functions
    unsafe_patterns = [
        (r'eval\(', "Use of eval() detected (Insecure)"),
        (r'exec\(', "Use of exec() detected (Insecure)"),
        (r'dangerouslySetInnerHTML', "React: dangerouslySetInnerHTML detected (XSS risk)"),
        (r'shell=True', "Python: subprocess with shell=True detected (Injections)"),
    ]

    for root, _, files in os.walk(target_dir):
        if ".git" in root or "node_modules" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith((".py", ".js", ".ts", ".tsx", ".env", ".yaml", ".yml")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        
                        for pattern, msg in secret_patterns + unsafe_patterns:
                            if re.search(pattern, content, re.IGNORE_CASE):
                                issues.append(f"❌ {path}: {msg}")
                except Exception as e:
                    print(f"⚠️ Could not read {path}: {e}")

    print("\n--- Security Scan Summary ---")
    if not issues:
        print("✅ No immediate security issues found.")
        sys.exit(0)
    else:
        print(f"Found {len(issues)} potential issues:")
        for issue in issues:
            print(issue)
        sys.exit(1)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    security_scan(target)
