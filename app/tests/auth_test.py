import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.src.schemas.response.access_token import AccessToken
from main import app

class TestExchangeCodeComplete(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("app.src.routers.owner_router.OwnerService")
    @patch("app.src.orm.database.database.get_session")
    @patch("app.src.utils.redis.redis_client.get_redis")
    async def test_exchange_code_no_real_requests(
        self, 
        mock_get_redis, 
        mock_get_session, 
        MockOwnerService
    ):
        
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        mock_session = AsyncMock()
        mock_get_session.return_value = mock_session

        mock_service = AsyncMock()
        MockOwnerService.return_value = mock_service

        mock_service.exchange_code.return_value = MagicMock(
            access_token="mocked_access_token",
            refresh_token="mocked_refresh_token"
        )

        mock_service.get_owner_info.return_value = 123456789

        mock_service.add_owner.return_value = AccessToken(
            access_token="jwt_mocked",
            refresh_token="jwt_refresh_mocked",
            token_type="bearer",
        )

        response = self.client.post(
            "api/v1/auth/get_owner",
            json={"code": "any_fake_code_will_work"}
        )
        
        self.assertEqual(response.status_code, 200)
        mock_service.exchange_code.assert_called_once()


        