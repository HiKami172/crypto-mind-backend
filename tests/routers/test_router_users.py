from fastapi.testclient import TestClient
from app.main import app  # Import your FastAPI app instance

client = TestClient(app)

def test_users_endpoint():
    """Test the /users endpoint."""
    response = client.get("/users")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
