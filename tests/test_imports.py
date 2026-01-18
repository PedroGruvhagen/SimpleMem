"""
Test that all main imports work correctly.
These tests don't require API keys.
"""
import pytest


def test_import_main_module():
    """Test importing the main simplemem module."""
    import simplemem
    assert hasattr(simplemem, "__version__")
    assert hasattr(simplemem, "SimpleMemSystem")
    assert hasattr(simplemem, "create_system")


def test_import_classes():
    """Test importing main classes."""
    from simplemem import SimpleMemSystem, MemoryEntry, Dialogue
    assert SimpleMemSystem is not None
    assert MemoryEntry is not None
    assert Dialogue is not None


def test_import_config():
    """Test importing config classes."""
    from simplemem import SimpleMemConfig, get_config, set_config
    assert SimpleMemConfig is not None
    assert get_config is not None
    assert set_config is not None


def test_version_format():
    """Test version string format."""
    from simplemem import __version__
    # Version should be in format X.Y.Z
    parts = __version__.split(".")
    assert len(parts) >= 2
    assert all(p.isdigit() for p in parts[:2])


def test_config_defaults():
    """Test config has sensible defaults."""
    from simplemem import get_config, SimpleMemConfig
    from simplemem.config import reset_config
    
    # Reset to ensure clean state
    reset_config()
    
    config = get_config()
    assert isinstance(config, SimpleMemConfig)
    assert config.llm_model == "gpt-4.1-mini"
    assert config.embedding_model == "Qwen/Qwen3-Embedding-0.6B"
    assert config.window_size == 40
    assert config.semantic_top_k == 25


def test_memory_entry_creation():
    """Test creating a MemoryEntry."""
    from simplemem import MemoryEntry
    
    entry = MemoryEntry(
        lossless_restatement="Test entry",
        keywords=["test", "entry"],
        persons=["Alice"],
    )
    
    assert entry.lossless_restatement == "Test entry"
    assert "test" in entry.keywords
    assert "Alice" in entry.persons
    assert entry.entry_id is not None  # Auto-generated UUID


def test_dialogue_creation():
    """Test creating a Dialogue."""
    from simplemem import Dialogue
    
    dialogue = Dialogue(
        dialogue_id=1,
        speaker="Alice",
        content="Hello, world!",
        timestamp="2025-01-15T10:00:00"
    )
    
    assert dialogue.speaker == "Alice"
    assert dialogue.content == "Hello, world!"
    assert dialogue.timestamp == "2025-01-15T10:00:00"
    
    # Test string representation
    str_repr = str(dialogue)
    assert "Alice" in str_repr
    assert "Hello, world!" in str_repr


def test_dialogue_without_timestamp():
    """Test creating a Dialogue without timestamp."""
    from simplemem import Dialogue
    
    dialogue = Dialogue(
        dialogue_id=2,
        speaker="Bob",
        content="Hi there!"
    )
    
    assert dialogue.timestamp is None
    str_repr = str(dialogue)
    assert "Bob: Hi there!" in str_repr
