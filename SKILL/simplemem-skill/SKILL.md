---
name: simplemem-skill
description: Store and retrieve conversation memories across sessions. Use when asked to 'remember this', 'save conversation', 'add to memory', 'what did we discuss about...', 'query memories', or 'import chat history'. Also use proactively to preserve important dialogue context and decisions.
---

# SimpleMem Skill

Persistent conversational memory across sessions.

## Proactive Usage

Save memories when discovering valuable dialogue:
- Important decisions or commitments made in conversation
- Complex information that may be referenced later
- Context from long discussions worth preserving
- Solutions to problems that took effort to uncover

Check memories before:
- Answering questions about past conversations
- Resuming work from previous sessions
- Building on earlier discussion topics

## Quick Start

```bash
# Add a dialogue
~/.claude/skills/simplemem-skill/venv/bin/python ~/.claude/skills/simplemem-skill/scripts/cli_persistent_memory.py add --speaker "Alice" --content "Meet Bob tomorrow at 2pm"

# Query memories
~/.claude/skills/simplemem-skill/venv/bin/python ~/.claude/skills/simplemem-skill/scripts/cli_persistent_memory.py query --question "When should Alice meet Bob?"
```

## Operations

### Save

Add single dialogue:

```bash
~/.claude/skills/simplemem-skill/venv/bin/python ~/.claude/skills/simplemem-skill/scripts/cli_persistent_memory.py add --speaker "User" --content "Your message here"
```

With timestamp (ISO 8601):

```bash
~/.claude/skills/simplemem-skill/venv/bin/python ~/.claude/skills/simplemem-skill/scripts/cli_persistent_memory.py add --speaker "Alice" --content "Message" --timestamp "2026-01-17T14:00:00Z"
```

### Query

Semantic query with answer:

```bash
~/.claude/skills/simplemem-skill/venv/bin/python ~/.claude/skills/simplemem-skill/scripts/cli_persistent_memory.py query --question "What did Alice say about meetings?"
```

With reflection for deeper analysis:

```bash
~/.claude/skills/simplemem-skill/venv/bin/python ~/.claude/skills/simplemem-skill/scripts/cli_persistent_memory.py query --question "Your question" --enable-reflection
```

Raw retrieval:

```bash
~/.claude/skills/simplemem-skill/venv/bin/python ~/.claude/skills/simplemem-skill/scripts/cli_persistent_memory.py retrieve --query "Alice meetings" --top-k 5
```

### Maintain

View statistics:

```bash
~/.claude/skills/simplemem-skill/venv/bin/python ~/.claude/skills/simplemem-skill/scripts/cli_persistent_memory.py stats
```

Clear all memories:

```bash
# Use with caution - irreversible
~/.claude/skills/simplemem-skill/venv/bin/python ~/.claude/skills/simplemem-skill/scripts/cli_persistent_memory.py clear --yes
```

## Batch Import

For importing conversation histories from JSONL files, see [references/import-guide.md](references/import-guide.md).

## Custom Table Names

Use different tables to organize conversation contexts:

```bash
~/.claude/skills/simplemem-skill/venv/bin/python ~/.claude/skills/simplemem-skill/scripts/cli_persistent_memory.py --table-name my_custom_table add --speaker "User" --content "Message"
```

## Data Format

All dialogues are stored with:
- `speaker`: Who said it (string)
- `content`: What was said (string)
- `timestamp`: When it was said (ISO 8601 datetime, auto-generated if omitted)

## API Provider Configuration

This skill supports both OpenAI and OpenRouter APIs with **automatic provider detection**.

The provider is selected based on which environment variable is set:
- `OPENAI_API_KEY` → Uses OpenAI (preferred, lower latency)
- `OPENROUTER_API_KEY` → Uses OpenRouter (fallback)

**OpenAI** (recommended):
- Direct API access, lower latency
- Uses `text-embedding-3-small` (1536 dims)
- Uses `gpt-4.1-mini` for LLM

**OpenRouter**:
- Unified gateway for multiple models
- Uses `qwen/qwen3-embedding-8b` (4096 dims)
- Uses `openai/gpt-4.1-mini` for LLM

See [references/openai-migration.md](references/openai-migration.md) for detailed provider documentation.

## Advanced Usage

For detailed information:
- **OpenAI migration guide**: [references/openai-migration.md](references/openai-migration.md)
- **OpenRouter setup and model selection**: [references/openrouter-guide.md](references/openrouter-guide.md)
- **JSONL import format and batch operations**: [references/import-guide.md](references/import-guide.md)
- **CLI command reference**: [references/cli-reference.md](references/cli-reference.md)
- **System architecture and configuration**: [references/architecture.md](references/architecture.md)

## Setup

**Create virtual environment and install dependencies**:

```bash
cd ~/.claude/skills/simplemem-skill
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

**Configure API** (choose one):

Option A - OpenAI (recommended):
```bash
export OPENAI_API_KEY="your-openai-key"
```

Option B - OpenRouter:
```bash
export OPENROUTER_API_KEY="your-openrouter-key"
```

For advanced configuration, see [references/openai-migration.md](references/openai-migration.md) or [references/openrouter-guide.md](references/openrouter-guide.md).

**Data storage**: Memories persist in `data/lancedb/` (auto-created).
