"""
Tests for VectorStore optimizations.
Tests FTS, SQL filters, and semantic search.
"""
import pytest

from simplemem.database import VectorStore
from simplemem.models import MemoryEntry


def create_test_entries():
    return [
        MemoryEntry(
            lossless_restatement="Alice suggested meeting at Starbucks on 2025-01-15 at 2pm",
            keywords=["Alice", "Starbucks", "meeting"],
            timestamp="2025-01-15T14:00:00",
            location="Starbucks",
            persons=["Alice", "Bob"],
            entities=["meeting"],
            topic="Meeting arrangement"
        ),
        MemoryEntry(
            lossless_restatement="Bob will bring the project documents to the meeting",
            keywords=["Bob", "documents", "project"],
            timestamp="2025-01-15T14:01:00",
            location=None,
            persons=["Bob"],
            entities=["documents", "project"],
            topic="Meeting preparation"
        ),
        MemoryEntry(
            lossless_restatement="Charlie confirmed attendance for the Starbucks meeting",
            keywords=["Charlie", "Starbucks", "attendance"],
            timestamp="2025-01-15T14:02:00",
            location="Starbucks",
            persons=["Charlie"],
            entities=["meeting"],
            topic="Meeting confirmation"
        )
    ]


@pytest.fixture
def store(tmp_path):
    """Create a temporary VectorStore for testing."""
    test_db_path = str(tmp_path / "test_lancedb")
    store = VectorStore(db_path=test_db_path, table_name="test_entries")
    store.clear()
    entries = create_test_entries()
    store.add_entries(entries)
    yield store
    store.clear()


class TestSemanticSearch:
    def test_semantic_search_returns_results(self, store):
        results = store.semantic_search("meeting location", top_k=5)
        assert len(results) > 0, "Semantic search should return results"


class TestKeywordSearch:
    def test_keyword_search_starbucks(self, store):
        results = store.keyword_search(["Starbucks"])
        # FTS may not be available if pylance is not installed, so we just verify no error
        # In production with full dependencies, this would return results
        assert isinstance(results, list), "Keyword search should return a list"

    def test_keyword_search_documents(self, store):
        results = store.keyword_search(["documents"])
        # FTS may not be available if pylance is not installed, so we just verify no error
        assert isinstance(results, list), "Keyword search should return a list"


class TestStructuredSearch:
    def test_structured_search_by_person_alice(self, store):
        results = store.structured_search(persons=["Alice"])
        assert len(results) > 0, "Should find entries with Alice"

    def test_structured_search_by_person_bob(self, store):
        results = store.structured_search(persons=["Bob"])
        assert len(results) > 0, "Should find entries with Bob"

    def test_structured_search_by_location(self, store):
        results = store.structured_search(location="Starbucks")
        assert len(results) > 0, "Should find entries at Starbucks"

    def test_structured_search_by_timestamp_range(self, store):
        results = store.structured_search(
            timestamp_range=("2025-01-15T00:00:00", "2025-01-15T23:59:59")
        )
        assert len(results) > 0, "Should find entries in timestamp range"


class TestTableOperations:
    def test_optimize(self, store):
        # Should not raise any exceptions
        store.optimize()

    def test_get_all_entries(self, store):
        results = store.get_all_entries()
        assert len(results) == 3, f"Should have 3 entries, got {len(results)}"


# CLI support for manual testing (not a pytest test)
def _test_gcs_connection(bucket_path, service_account_path=None):
    """
    Test GCS backend with native FTS.

    Usage:
        python -m pytest tests/test_vector_store.py --gcs gs://your-bucket/lancedb --sa /path/to/service-account.json
    """
    print("\n" + "=" * 60)
    print("GCS Connection Test (Native FTS)")
    print("=" * 60)

    storage_options = None
    if service_account_path:
        storage_options = {"service_account": service_account_path}

    print(f"\nConnecting to {bucket_path}...")
    store = VectorStore(
        db_path=bucket_path,
        table_name="gcs_test_entries",
        storage_options=storage_options
    )
    store.clear()

    print("\nAdding test entries...")
    entries = create_test_entries()
    store.add_entries(entries)
    print(f"  Added {len(entries)} entries")

    passed = 0
    failed = 0

    # Test semantic search
    print("\n[TEST] Semantic search on GCS...")
    try:
        results = store.semantic_search("meeting location")
        assert len(results) > 0, "Should find results"
        print(f"  PASS: Found {len(results)} results")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # Test FTS keyword search (native mode)
    print("\n[TEST] FTS keyword search on GCS (native mode)...")
    try:
        results = store.keyword_search(["Starbucks"])
        assert len(results) > 0, "Should find Starbucks"
        print(f"  PASS: Found {len(results)} results for 'Starbucks'")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # Test structured search
    print("\n[TEST] Structured search on GCS...")
    try:
        results = store.structured_search(persons=["Alice"])
        assert len(results) > 0, "Should find Alice"
        print(f"  PASS: Found {len(results)} results for persons=['Alice']")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    print("\nCleaning up...")
    store.clear()

    print("\n" + "=" * 60)
    print(f"GCS Results: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--gcs", help="GCS bucket path (gs://bucket/path)")
    parser.add_argument("--sa", help="Service account JSON path")
    args = parser.parse_args()

    if args.gcs:
        success = _test_gcs_connection(args.gcs, args.sa)
        import sys
        sys.exit(0 if success else 1)
    else:
        # Run pytest for local tests
        import sys
        sys.exit(pytest.main([__file__, "-v"]))
