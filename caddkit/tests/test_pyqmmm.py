"""
Unit and regression test for the caddkit package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import caddkit


def test_caddkit_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "caddkit" in sys.modules
