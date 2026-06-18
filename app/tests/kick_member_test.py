import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from app.src.security.oauth import get_current_owner

class TestKickMember(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_owner = MagicMock()
        self.mock_owner.ds_id = 123456789012345678
        
        async def override_get_current_owner():
            return self.mock_owner
        
        app.dependency_overrides[get_current_owner] = override_get_current_owner
        
        self.client = TestClient(app)
        self.client.cookies.set("access_token", "fake_token_123")
    
    def tearDown(self):
        app.dependency_overrides.clear()
    
    @patch("app.src.routers.guilds_router.GuildService")
    @patch("app.src.orm.database.database.get_session")
    async def test_kick_member_success(
        self,
        mock_get_session,
        MockGuildService
    ):  
        mock_session = AsyncMock()
        mock_get_session.return_value = mock_session
        
        mock_guild_service = AsyncMock()
        MockGuildService.return_value = mock_guild_service
        
        response = self.client.request(
            method="DELETE",
            url="/api/v1/guilds/123456789012345678/members/876543210987654321",
            json={
                "reason": "Нарушение правил",
                "delete_user_messages": False
            }
        )
        
        self.assertEqual(response.status_code, 200)
        mock_guild_service.kick_member.assert_called_once_with(
            123456789012345678,
            123456789012345678,
            876543210987654321,
            "Нарушение правил"
        )