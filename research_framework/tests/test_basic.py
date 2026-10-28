import sys
import os

# Ensure the root directory is in the path for pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import DATA_DIR, RAW_DATA_PATH

def test_environment_setup():
    """Test that configuration and paths load correctly."""
    assert DATA_DIR is not None
    assert 'data' in DATA_DIR
    assert 'amazon_search_dataset.csv' in RAW_DATA_PATH
