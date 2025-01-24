from sqlalchemy.orm import declarative_base

def test_base_model():
    Base = declarative_base()
    assert Base.metadata is not None
