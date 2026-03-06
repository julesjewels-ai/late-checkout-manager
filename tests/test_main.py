from fastapi.testclient import TestClient
from late_checkout.main import app

client = TestClient(app)


def test_read_main() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Late Checkout"}
