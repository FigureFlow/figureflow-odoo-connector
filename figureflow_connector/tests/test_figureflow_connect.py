"""Smoke tests for the FigureFlow connector.

These run against an in-memory Odoo test database. The Connect action talks
to a real HTTPS endpoint, so we patch ``requests.post`` to keep the test
hermetic.
"""

from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestFigureFlowConnect(TransactionCase):

    def setUp(self):
        super().setUp()
        self.settings = self.env["res.config.settings"].create({})
        # web.base.url is read via ir.config_parameter; default test DB sets
        # it but we pin a known value for assertion ergonomics.
        self.env["ir.config_parameter"].sudo().set_param(
            "web.base.url", "https://acme.odoo.com",
        )

    def _stub_response(self, status_code=201, json_body=None):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_body or {"claim_code": "abc-123"}
        response.text = "stubbed"
        return response

    def test_connect_returns_act_url_with_claim_code(self):
        with patch(
            "odoo.addons.figureflow_connector.models.res_config_settings.requests.post",
            return_value=self._stub_response(),
        ) as mock_post:
            action = self.settings.action_figureflow_connect()

        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertIn("claim=abc-123", action["url"])
        self.assertEqual(action["target"], "new")

        # The handshake POSTed to the correct endpoint with the expected fields.
        url_arg, kwargs = mock_post.call_args.args[0], mock_post.call_args.kwargs
        self.assertTrue(url_arg.endswith("/api/integrations/odoo/marketplace/initiate/"))
        payload = kwargs["json"]
        self.assertEqual(payload["domain"], "acme.odoo.com")
        self.assertEqual(payload["username"], self.env.user.login)
        self.assertTrue(payload["api_key"])

        # Connection status was persisted.
        status = self.env["ir.config_parameter"].sudo().get_param(
            "figureflow_connector.connection_status"
        )
        self.assertEqual(status, "awaiting_claim")

    def test_connect_raises_user_error_on_figureflow_4xx(self):
        with patch(
            "odoo.addons.figureflow_connector.models.res_config_settings.requests.post",
            return_value=self._stub_response(status_code=401, json_body={}),
        ):
            with self.assertRaises(UserError):
                self.settings.action_figureflow_connect()

    def test_disconnect_clears_state(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "figureflow_connector.connection_status", "awaiting_claim",
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "figureflow_connector.last_claim_code", "abc-123",
        )

        self.settings.action_figureflow_disconnect()

        status = self.env["ir.config_parameter"].sudo().get_param(
            "figureflow_connector.connection_status"
        )
        claim = self.env["ir.config_parameter"].sudo().get_param(
            "figureflow_connector.last_claim_code"
        )
        self.assertEqual(status, "disconnected")
        self.assertEqual(claim, "")
