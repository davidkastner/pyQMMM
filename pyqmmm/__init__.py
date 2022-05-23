"""Python package for manipulating QM and MD trajectories"""

# Add imports here
from pyqmmm import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
