#!/bin/bash

# Ensure we're in the project root by resolving the script path
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$PROJECT_ROOT/references"
cd "$PROJECT_ROOT/references" || exit

clone_repo() {
    local url=$1
    local name=$(basename "$url" .git)
    if [ ! -d "$name" ]; then
        echo "Cloning $name..."
        git clone "$url"
    else
        echo "Repository $name already exists. Fetching latest changes..."
        git -C "$name" pull
    fi
}

clone_repo "https://github.com/JuliusBrussee/caveman.git"
clone_repo "https://github.com/Mauriciog87/flutter-agent-skill.git"
clone_repo "https://github.com/flutter/agent-plugins.git"
clone_repo "https://github.com/vercel-labs/agent-skills.git"
clone_repo "https://github.com/cexll/golang-base-practices-skills.git"
