#!/bin/bash
# src/macos/launch_thor_ui_connected.sh

echo "🚀 Launching THOR UI with Backend..."

# Get directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THOR_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to THOR root
cd "$THOR_ROOT"

# Check if virtual environment exists
if [ ! -d "thor_env" ]; then
    echo "❌ Virtual environment not found. Please run installation first."
    exit 1
fi

# Activate environment
echo "🐍 Activating Python environment..."
source thor_env/bin/activate

# Start WebSocket bridge
echo "🔌 Starting THOR WebSocket Bridge..."
python -m src.core.websocket_bridge &
BRIDGE_PID=$!

# Wait for bridge
echo "⏳ Waiting for bridge to start..."
sleep 2

# Launch UI
echo "🖥️  Launching THOR UI..."
open "$SCRIPT_DIR/ThorUI.app"

echo "✅ THOR UI launched!"
echo "💡 If API key error: Open Settings in UI and enter your Anthropic API key"
echo "🔌 Bridge PID: $BRIDGE_PID"
echo "🛑 Press Ctrl+C to stop"

# Wait for interrupt
trap "echo '🛑 Shutting down...'; kill $BRIDGE_PID 2>/dev/null; exit" INT
wait $BRIDGE_PID