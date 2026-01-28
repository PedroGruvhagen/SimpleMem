# SimpleMem MCP Server - OpenAI Setup Guide

This guide explains how to set up SimpleMem MCP Server with OpenAI API for use with Claude Desktop.

## Prerequisites

1. **Python 3.9+** installed
2. **OpenAI API Key** - Get one at https://platform.openai.com/api-keys
3. **Claude Desktop** installed

## Quick Start

### 1. Install Dependencies

```bash
cd /path/to/SimpleMem/MCP
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set OpenAI API Key (Optional)

```bash
# Add to ~/.zshrc or ~/.bash_profile
export OPENAI_API_KEY="sk-your-key-here"
```

### 3. Start the Server

```bash
./start_server.sh
```

Or manually:

```bash
source .venv/bin/activate
python run.py --host 127.0.0.1 --port 8000
```

### 4. Get Your Bearer Token

1. Open http://127.0.0.1:8000/ in your browser
2. Enter your OpenAI API Key
3. Click "Register" or "Get Token"
4. Copy the generated token

### 5. Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "simplemem": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    }
  }
}
```

### 6. Restart Claude Desktop

Fully quit Claude Desktop (right-click dock icon → Quit) and relaunch it.

## Verify Installation

After restart, try asking Claude Desktop:

> "Remember that I have a meeting with Bob tomorrow at 2pm"

Claude should use the `memory_add` tool. Then ask:

> "When is my meeting with Bob?"

Claude should use `memory_query` and respond with the correct information.

## Configuration

### Models Used

| Purpose | Model | Dimensions |
|---------|-------|------------|
| LLM | gpt-4.1-mini | - |
| Embeddings | text-embedding-3-small | 1536 |

### Data Storage

- **Vector Database**: `./data/lancedb/`
- **User Database**: `./data/users.db`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Fallback API key for single-user mode | (none) |
| `JWT_SECRET_KEY` | Secret for JWT tokens | (auto-generated) |
| `ENCRYPTION_KEY` | Key for API key encryption | (auto-generated) |

## Troubleshooting

### "MCP tools don't appear in Claude Desktop"

1. Verify the server is running: `curl http://127.0.0.1:8000/api/health`
2. Check the config JSON syntax
3. Fully quit and restart Claude Desktop (not just close window)

### "Invalid API key error"

1. Verify your OpenAI API key starts with `sk-`
2. Test it directly: `curl https://api.openai.com/v1/models -H "Authorization: Bearer sk-your-key"`

### "Embedding dimension error"

If you're upgrading from an older version with different embedding dimensions:

```bash
rm -rf ./data/lancedb/
# Restart server - fresh database will be created
```

### "Connection refused"

1. Ensure server is running on port 8000
2. Check if another process is using port 8000: `lsof -i :8000`
3. Try a different port: `./start_server.sh --port 8001`

## Security Notes

- The bearer token is valid for 30 days
- API keys are encrypted before storage
- All data is stored locally on your machine
- The server only listens on localhost (127.0.0.1)

## Support

For issues, check the [GitHub repository](https://github.com/your-repo/SimpleMem) or create an issue.
