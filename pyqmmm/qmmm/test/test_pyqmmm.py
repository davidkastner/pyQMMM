"""
Unit and regression test for the pyqmmm package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import pyqmmm


def test_pyqmmm_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "pyqmmm" in sys.modules
