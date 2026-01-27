# API Provider Guide

SimpleMem supports both OpenAI and OpenRouter APIs with automatic provider detection.

## Auto-Detection

The skill automatically selects the provider based on which environment variable is set:

| Environment Variable | Provider | Priority |
|---------------------|----------|----------|
| `OPENAI_API_KEY` | OpenAI (direct) | 1st (preferred) |
| `OPENROUTER_API_KEY` | OpenRouter | 2nd (fallback) |

If both are set, OpenAI takes precedence.

## OpenAI Configuration

When `OPENAI_API_KEY` is detected:
- **LLM**: `gpt-4.1-mini`
- **Embeddings**: `text-embedding-3-small` (1536 dimensions)
- **Base URL**: `https://api.openai.com/v1`

### Setup

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

Get your key from: https://platform.openai.com/api-keys

### Cost Estimates

- **text-embedding-3-small**: $0.00002 per 1K tokens
- **gpt-4.1-mini**: $0.150 per 1M input, $0.600 per 1M output tokens

Typical costs for 1000 conversational turns:
- Embedding: ~$0.10
- Memory building: ~$2.00
- Query answering: ~$0.50/query

## OpenRouter Configuration

When `OPENROUTER_API_KEY` is detected (and no OpenAI key):
- **LLM**: `openai/gpt-4.1-mini`
- **Embeddings**: `qwen/qwen3-embedding-8b` (4096 dimensions)
- **Base URL**: `https://openrouter.ai/api/v1`

### Setup

```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

Get your key from: https://openrouter.ai/keys

## Switching Providers

Simply change which environment variable is set:

```bash
# Use OpenAI
export OPENAI_API_KEY="your-key"
unset OPENROUTER_API_KEY

# Use OpenRouter
export OPENROUTER_API_KEY="your-key"
unset OPENAI_API_KEY
```

**IMPORTANT**: Different providers use different embedding dimensions (1536 vs 4096). When switching providers, you should use a fresh database or clear existing data to avoid dimension mismatch errors.

## Troubleshooting

**"Invalid API key"**:
- Check environment variable: `echo $OPENAI_API_KEY` or `echo $OPENROUTER_API_KEY`
- Verify key at provider's website
- Ensure key has API access (not just ChatGPT Plus for OpenAI)

**"Embedding dimension mismatch"**:
- You switched providers without clearing the database
- Solution: Clear data with `cli_persistent_memory.py clear --yes` or use a fresh table name

**"Model not found"**:
- Your account lacks access to the model
- For OpenAI: Try `gpt-4o-mini` instead of `gpt-4.1-mini`
- For OpenRouter: Check model availability at openrouter.ai/models

**"Rate limit exceeded"**:
- Provider rate limits reached
- Wait and retry, or upgrade your tier

## Security Notes

- **Never hardcode API keys** in config files or commit them to version control
- The skill reads keys from environment variables only
- Add `.env` files to `.gitignore` if using them
