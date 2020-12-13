import pytest
from main import app
import asyncio

@pytest.fixture(name='test_app')
def _test_app():
  return app

@pytest.mark.asyncio
async def test_main(test_app):
  client = test_app.test_client()
  response = await client.get("/")
  assert response.status_code == 200
