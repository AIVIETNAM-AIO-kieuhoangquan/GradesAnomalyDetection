import os
import sys
import pytest

# Thêm project root vào sys.path để pytest tìm thấy modules/ và config.py
sys.path.insert(0, os.path.dirname(__file__))

from app import app as flask_app


@pytest.fixture
def client():
    """Tạo test client cho Flask app."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client
