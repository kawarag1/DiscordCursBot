import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from app.src.schemas.request.disable_command_schema import DisableCommandSchema

class TestEnableCommand(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    @patch("app.src.routers.command_router.CommandService")
    @patch("app.src.orm.database.database.get_session")
    async def test_enable_command_success(
        self,
        mock_get_session,
        MockCommandService
    ):
        mock_session = AsyncMock()
        mock_get_session.return_value = mock_session
        
        command_data = {
            "command_name": "ban",
            "guild_id": 123456789012345678,
        }
        
        mock_response = DisableCommandSchema(
            command_name="ban",
            guild_id=123456789012345678,
        )
        
        mock_command_service = AsyncMock()
        mock_command_service.enable_command.return_value = mock_response
        MockCommandService.return_value = mock_command_service
        
        response = self.client.request(
            method="DELETE",
            url="/api/v1/commands/enable",
            json=command_data
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertEqual(response_data["command_name"], "ban")
        self.assertEqual(int(response_data["guild_id"]), 123456789012345678)
        
        mock_command_service.enable_command.assert_called_once()
        
        call_args = mock_command_service.enable_command.call_args[0][0]
        self.assertEqual(call_args.command_name, "ban")
        self.assertEqual(call_args.guild_id, 123456789012345678)