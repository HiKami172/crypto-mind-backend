from enum import Enum


def alchemy_to_dict(obj):
    """Converts a SQLAlchemy model instance to a dictionary, handling enums."""
    result = {}
    for key, value in obj.__dict__.items():
        if key == "_sa_instance_state":
            continue
        if isinstance(value, Enum):
            result[key] = value.name
        else:
            result[key] = value
    return result