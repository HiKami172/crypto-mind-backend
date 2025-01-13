import uuid
from app.schemas.users import UserRead, UserCreate, UserUpdate

def test_user_read_schema():
    user_data = {
        "id": uuid.uuid4(),
        "email": "testuser@example.com",
        "is_active": True,
        "is_superuser": False,
        "full_name": "Test User",
    }

    schema = UserRead(**user_data)

    assert schema.id == user_data["id"]
    assert schema.email == user_data["email"]
    assert schema.is_active == user_data["is_active"]
    assert schema.is_superuser == user_data["is_superuser"]
    assert schema.full_name == user_data["full_name"]

def test_user_create_schema():
    user_data = {
        "email": "testuser@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
    }

    schema = UserCreate(**user_data)

    assert schema.email == user_data["email"]
    assert schema.password == user_data["password"]
    assert schema.full_name == user_data["full_name"]

def test_user_update_schema():
    user_data = {
        "email": "updateduser@example.com",
        "password": "newsecurepassword123",
        "full_name": "Updated User",
    }

    schema = UserUpdate(**user_data)

    assert schema.email == user_data["email"]
    assert schema.password == user_data["password"]
    assert schema.full_name == user_data["full_name"]
