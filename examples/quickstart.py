"""
SimpleMem Quick Start Example

This example demonstrates basic usage of SimpleMem for dialogue memory.

Prerequisites:
    1. Install simplemem: pip install simplemem
    2. Set OPENAI_API_KEY environment variable

Usage:
    export OPENAI_API_KEY="your-api-key"
    python quickstart.py
"""
import os

# Check for API key
if not os.environ.get("OPENAI_API_KEY"):
    print("Error: Please set OPENAI_API_KEY environment variable")
    print("Example: export OPENAI_API_KEY='your-api-key'")
    exit(1)

from simplemem import SimpleMemSystem

def main():
    # Initialize SimpleMem system
    print("Initializing SimpleMem...")
    system = SimpleMemSystem(clear_db=True)

    # Add some dialogues
    print("\nAdding dialogues...")
    system.add_dialogue(
        "Alice",
        "Bob, let's meet at Starbucks tomorrow at 2pm to discuss the new product",
        "2025-11-15T14:30:00"
    )
    system.add_dialogue(
        "Bob",
        "Okay, I'll prepare the materials",
        "2025-11-15T14:31:00"
    )
    system.add_dialogue(
        "Alice",
        "Remember to bring the market research report from last time",
        "2025-11-15T14:32:00"
    )

    # Finalize processing
    print("\nFinalizing memory processing...")
    system.finalize()

    # View all memories (optional debugging)
    print("\nMemory entries created:")
    system.print_memories()

    # Ask questions
    print("\n" + "=" * 60)
    print("Testing Q&A")
    print("=" * 60)

    questions = [
        "When will Alice and Bob meet?",
        "Where will they meet?",
        "What should Bob prepare?",
    ]

    for q in questions:
        print(f"\nQ: {q}")
        answer = system.ask(q)
        print(f"A: {answer}")

    print("\n" + "=" * 60)
    print("Quick start completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
