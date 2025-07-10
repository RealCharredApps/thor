#!/bin/bash
# THOR Quick Start Script

echo "🔨 THOR Quick Start"
echo "=================="

# Set project directory
PROJECT_DIR=${1:-"./my-thor-project"}

# Create project directory
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Setup THOR
echo "Setting up THOR for project: $PROJECT_DIR"
python3 ../src/thor_main.py setup "$PROJECT_DIR"

# Start interactive chat
echo "Starting THOR chat..."
python3 ../src/thor_main.py chat "$PROJECT_DIR"
