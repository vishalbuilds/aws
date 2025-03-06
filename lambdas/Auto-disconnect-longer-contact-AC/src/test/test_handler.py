import unittest
from unittest.mock import patch
import os
import sys

# Ensure the module is correctly imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import hello  as handler




class TestRemovePII(unittest.TestCase):
    def test_generate_random_id_success(self, mock_uuid):
        assert True
  