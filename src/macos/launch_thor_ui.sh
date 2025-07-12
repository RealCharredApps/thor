#!/bin/bash
# src/macos/launch_thor_ui.sh

echo "🚀 Launching THOR UI..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THOR_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate Python environment
cd "$THOR_ROOT"
source thor_env/bin/activate

# Start the UI bridge in background
echo "🔌 Starting UI Bridge..."
python -m src.core.ui_bridge &
UI_BRIDGE_PID=$!

# Wait for bridge to start
sleep 2

# Launch the macOS UI
echo "🖥️  Launching macOS UI..."
open "$SCRIPT_DIR/ThorUI.app"

# Wait for UI to close
wait $UI_BRIDGE_PID

echo "👋 THOR UI closed"