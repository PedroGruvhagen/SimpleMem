#!/bin/bash
# SimpleMem MCP Server Startup Script
#
# Usage: ./start_server.sh [--port PORT]
#
# This script starts the SimpleMem MCP server for Claude Desktop.
# Make sure the server is running before using SimpleMem tools in Claude Desktop.

cd "$(dirname "$0")"

# Default port
PORT=8000

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--port PORT]"
            exit 1
            ;;
    esac
done

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: No virtual environment found."
    echo "Please run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY is not set."
    echo "Users will need to register with their own API key via http://127.0.0.1:$PORT/"
fi

echo "============================================================"
echo "  SimpleMem MCP Server"
echo "  Multi-tenant Memory Service for LLM Agents"
echo "============================================================"
echo ""
echo "  Web UI:     http://127.0.0.1:$PORT/"
echo "  REST API:   http://127.0.0.1:$PORT/api/"
echo "  MCP:        http://127.0.0.1:$PORT/mcp"
echo ""
echo "  Press Ctrl+C to stop"
echo "------------------------------------------------------------"

# Start the server
python run.py --host 127.0.0.1 --port $PORT
