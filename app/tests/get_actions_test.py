# app/tests/get_actions_test.py
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime
from main import app
from app.src.security.oauth import get_current_owner
from app.src.schemas.response.action_schema import ActionSchema, MemberActionSchema

class TestGetActions(unittest.IsolatedAsyncioTestCase):
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

    @patch("app.src.routers.action_router.ActionService")
    @patch("app.src.orm.database.database.get_session")
    async def test_get_actions_success(
        self,
        mock_get_session,
        MockActionService
    ):
        mock_session = AsyncMock()
        mock_get_session.return_value = mock_session

        user_info = MemberActionSchema(
            username="john_doe",
            avatar_url="https://cdn.discordapp.com/avatars/123/avatar.png"
        )

        target_info = MemberActionSchema(
            username="violator_user",
            avatar_url=None
        )

        mock_actions = [
            ActionSchema(
                id=1,
                user=user_info,
                guild_id=123456789012345678,
                action="ban",
                target=target_info,
                reason="Нарушение правил",
                details="Пользователь нарушил правило №1",
                created_at=datetime(2024, 1, 1, 0, 0, 0)
            ),
            ActionSchema(
                id=2,
                user=user_info,
                guild_id=123456789012345678,
                action="kick",
                target=target_info,
                reason="Спам",
                details="Отправка рекламных сообщений",
                created_at=datetime(2024, 1, 2, 0, 0, 0)
            )
        ]

        mock_action_service = AsyncMock()
        mock_action_service.get_actions.return_value = mock_actions
        MockActionService.return_value = mock_action_service

        response = self.client.get("/api/v1/actions/123456789012345678")

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]["action"], "ban")
        self.assertEqual(response_data[0]["user"]["username"], "john_doe")
        self.assertEqual(response_data[1]["action"], "kick")

        mock_action_service.get_actions.assert_called_once_with(123456789012345678)