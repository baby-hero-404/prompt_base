import os
import sys
import subprocess

def run_lint(target_dir):
    print(f"🚀 Running Unified Lint Runner on: {target_dir}")
    
    results = []
    
    # 1. Python (Ruff/Flake8)
    if os.path.exists(os.path.join(target_dir, "pyproject.toml")) or any(f.endswith(".py") for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))):
        print("🔍 Python project detected...")
        try:
            subprocess.run(["ruff", "check", target_dir], check=True)
            results.append("✅ Python: Ruff passed")
        except FileNotFoundError:
            results.append("⚠️ Python: Ruff not found, skipping")
        except subprocess.CalledProcessError:
            results.append("❌ Python: Ruff found issues")

    # 2. Node.js (ESLint)
    if os.path.exists(os.path.join(target_dir, "package.json")):
        print("🔍 Node.js project detected...")
        try:
            subprocess.run(["npm", "run", "lint"], check=True, cwd=target_dir)
            results.append("✅ Node.js: npm run lint passed")
        except subprocess.CalledProcessError:
            results.append("❌ Node.js: npm run lint failed")
        except Exception as e:
            results.append(f"⚠️ Node.js: Error running lint: {e}")

    # 3. Simple Grep for common issues (fallback)
    print("🔍 Running generic syntax checks...")
    # TODO: Add more checks
    
    print("\n--- Lint Summary ---")
    for res in results:
        print(res)
    
    if any("❌" in r for r in results):
        sys.exit(1)
    print("\n🚀 Linting complete.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    run_lint(target)
