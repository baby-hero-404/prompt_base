import os
import sys
import json
import shutil
import fnmatch

def load_manifest(manifest_path):
    with open(manifest_path, 'r') as f:
        return json.load(f)

def is_excluded(name, rel_path, is_dir, excludes):
    for ex in excludes:
        if ex.endswith('/'):
            ex_name = ex[:-1]
            # Directory excludes are root-relative only, so a top-level dir
            # like "references/" doesn't also strip nested skills/*/references/.
            if is_dir and fnmatch.fnmatch(rel_path, ex_name):
                return True
        else:
            if fnmatch.fnmatch(name, ex) or fnmatch.fnmatch(rel_path, ex):
                return True
    return False

def force_copy(src, dst, target_prefix=""):
    if os.path.exists(dst):
        try:
            os.chmod(dst, 0o666)
        except OSError:
            pass

    if src.endswith('.md'):
        with open(src, 'r', encoding='utf-8') as f:
            content = f.read()
        if target_prefix:
            content = content.replace('`tools/', f'`{target_prefix}/tools/')
            content = content.replace('python tools/', f'python {target_prefix}/tools/')
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(content)
        shutil.copystat(src, dst)
    else:
        shutil.copy2(src, dst)

def copy_tree_filtered(src_root, dst_root, excludes, target_prefix=""):
    for root, dirs, files in os.walk(src_root):
        rel_root = os.path.relpath(root, src_root)
        if rel_root == '.':
            rel_root = ''
        
        # filter dirs in place
        new_dirs = []
        for d in dirs:
            rel_path = os.path.join(rel_root, d) if rel_root else d
            if not is_excluded(d, rel_path, True, excludes):
                new_dirs.append(d)
        dirs[:] = new_dirs

        for file in files:
            rel_path = os.path.join(rel_root, file) if rel_root else file
            if not is_excluded(file, rel_path, False, excludes):
                src_path = os.path.join(root, file)
                dst_path = os.path.join(dst_root, rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                force_copy(src_path, dst_path, target_prefix)

def main():
    if len(sys.argv) < 2:
        print("Usage: install_manifest.py <target_dir>")
        sys.exit(1)
        
    target_prefix = sys.argv[1]
    target = os.path.expanduser(target_prefix)
    
    manifest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "install.manifest.json")
    if not os.path.exists(manifest_path):
        manifest_path = "install.manifest.json"
        
    manifest = load_manifest(manifest_path)
    excludes = manifest.get("excludes", [])
    
    # Source is current working directory where make is run
    copy_tree_filtered(".", target, excludes, target_prefix)
    
    # Post-install assertions
    required = ["registry.min.json", "agents", "skills"]
    for req in required:
        if not os.path.exists(os.path.join(target, req)):
            print(f"Error: Required path {req} missing from target {target}")
            sys.exit(1)

    print(f"Manifest copy to {target} completed successfully.")

if __name__ == "__main__":
    main()
