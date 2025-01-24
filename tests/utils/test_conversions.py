from enum import Enum

import pytest
from app.utils.conversions import alchemy_to_dict  # Correct import


# Enum for the test
class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# Dummy SQLAlchemy model class
class DummyModel:
    def __init__(self, name, status):
        self.name = name
        self.status = status
        self._sa_instance_state = None  # Mock the SQLAlchemy instance state


# Test the alchemy_to_dict function
def test_alchemy_to_dict():
    # Create an instance of DummyModel
    obj = DummyModel(name="Test Object", status=Status.ACTIVE)

    # Call alchemy_to_dict with the instance
    result = alchemy_to_dict(obj)

    # Check if the dictionary is correctly generated
    assert result == {"name": "Test Object", "status": "ACTIVE"}
