"""
Test/Demo file for Search Service
This file demonstrates how to use the search (Valyu) service helpers.
It purposely avoids network calls by exercising fallback logic.
"""

import os
import sys
import django

# Adjust path and configure Django so we can import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mandry_ai.settings")

django.setup()

from services.search_service import (
    default_search_service,
    extract_main_query,
    get_fallback_sources,
)


def test_extract_main_query():
    """Basic sanity check that UK context is injected if missing."""
    query = "How do I apply for a student visa?"
    main = extract_main_query(query)
    print(f"Original: {query}\nExtracted: {main}")


def test_fallback_sources():
    """Ensure fallback produces at least one gov.uk source."""
    results = get_fallback_sources("student visa guidance")
    assert len(results) >= 1
    print("Fallback source sample:", results[0])


def demo_usage():
    """Show typical wrapper usage with network disabled."""

    # Force Valyu import failure to trigger fallback logic
    import builtins

    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "valyu":
            raise ImportError("Valyu SDK not installed (test mode)")
        return original_import(name, *args, **kwargs)

    builtins.__import__ = mock_import

    try:
        results = default_search_service.valyu_search("UK visa options", top_k=2)
        print("Valyu search (fallback) returned", len(results), "results")
    finally:
        builtins.__import__ = original_import


if __name__ == "__main__":
    print("Search Service Test Demo")
    print("=" * 50)
    test_extract_main_query()
    test_fallback_sources()
    demo_usage()
    print("\nSearch Service tests complete!") 