"""
Simple test to verify pytest is working.
"""


def test_dummy():
    """Simple test that always passes"""
    assert True


def test_imports():
    """Test that imports work"""
    import sys
    print("\nPython path:")
    for p in sys.path[:5]:
        print(f"  - {p}")
    assert True
