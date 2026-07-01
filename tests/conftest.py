"""Test conftest for pytest"""
import pytest
import os
from pathlib import Path

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["TESTING"] = "true"

# Add src to path
src_path = Path(__file__).parent.parent
os.sys.path.insert(0, str(src_path))
