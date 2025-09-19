#!/bin/bash
# Setup script for OpenCode Agents configuration generators

echo "Setting up OpenCode Agents configuration generators..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To use the generators:"
echo "  source .venv/bin/activate"
echo "  python3 ogc/control/commands/scripts/commit.py"
echo "  python3 ogc/control/commands/scripts/worktrees.py"
