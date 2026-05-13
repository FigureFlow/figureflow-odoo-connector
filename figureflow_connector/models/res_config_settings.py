"""FigureFlow connector — settings page extension.

The Connect action generates a personal Odoo API key for the current user,
performs a server-to-server handshake with FigureFlow's marketplace
``initiate`` endpoint on the API host, receives a single-use claim_code,
and opens the user's browser to FigureFlow's web app to complete
signup/login. Credentials never travel through the browser; the
claim_code is the only thing the browser sees and it is single-use with
a short TTL on the FigureFlow side.
"""

import logging
from urllib.parse import urlencode, urlparse

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

FIGUREFLOW_API_URL_PARAM = "figureflow_connector.api_url"
FIGUREFLOW_WEB_URL_PARAM = "figureflow_connector.web_url"
FIGUREFLOW_CONNECTION_STATUS_PARAM = "figureflow_connector.connection_status"
FIGUREFLOW_CLAIM_CODE_PARAM = "figureflow_connector.last_claim_code"
FIGUREFLOW_API_KEY_ID_PARAM = "figureflow_connector.api_key_id"

DEFAULT_API_URL = "https://api.figureflow.app"
DEFAULT_WEB_URL = "https://web.figureflow.app"
INITIATE_TIMEOUT_SECONDS = 30


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    figureflow_api_url = fields.Char(
        string="FigureFlow API URL",
        config_parameter=FIGUREFLOW_API_URL_PARAM,
        default=DEFAULT_API_URL,
        help="Backend API endpoint this connector calls server-to-server. "
             "Change only if you're connecting to a non-production environment.",
    )
    figureflow_web_url = fields.Char(
        string="FigureFlow Web URL",
        config_parameter=FIGUREFLOW_WEB_URL_PARAM,
        default=DEFAULT_WEB_URL,
        help="FigureFlow web app the user's browser is redirected to after "
             "the handshake. Change only for non-production environments.",
    )
    figureflow_connection_status = fields.Char(
        string="Connection Status",
        config_parameter=FIGUREFLOW_CONNECTION_STATUS_PARAM,
        readonly=True,
    )

    def _figureflow_get_param(self, key, default=None):
        return self.env["ir.config_parameter"].sudo().get_param(key, default=default)

    def _figureflow_set_param(self, key, value):
        self.env["ir.config_parameter"].sudo().set_param(key, value or "")

    def _figureflow_resolve_odoo_domain(self):
        """Return the host portion of ``web.base.url`` — what FigureFlow stores
        as the Odoo instance's ``domain`` for the marketplace handshake."""
        base = self._figureflow_get_param("web.base.url") or ""
        parsed = urlparse(base)
        host = parsed.netloc or parsed.path
        return host.strip("/")

    def _figureflow_generate_api_key(self):
        """Create a personal API key on the current user, scoped to this
        connector. Returns ``(key_id, raw_key)``."""
        user = self.env.user
        api_keys_model = self.env["res.users.apikeys"]
        raw_key = api_keys_model.with_user(user)._generate(
            scope="figureflow_connector",
            name="FigureFlow Connector",
        )
        # ``_generate`` creates the row and returns the raw key string; the row
        # id is the most recent one for this user/scope.
        key_row = api_keys_model.sudo().search(
            [("user_id", "=", user.id), ("scope", "=", "figureflow_connector")],
            order="create_date desc",
            limit=1,
        )
        return key_row.id if key_row else False, raw_key

    def action_figureflow_connect(self):
        """Generate an API key, hand it off to FigureFlow over HTTPS, and open
        the browser to the marketplace claim page."""
        self.ensure_one()

        api_url = (self.figureflow_api_url or DEFAULT_API_URL).rstrip("/")
        web_url = (self.figureflow_web_url or DEFAULT_WEB_URL).rstrip("/")
        domain = self._figureflow_resolve_odoo_domain()
        if not domain:
            raise UserError(_(
                "Could not determine this Odoo instance's URL. Please set "
                "the System Parameter ``web.base.url`` to a reachable HTTPS URL "
                "and try again."
            ))

        key_id, api_key = self._figureflow_generate_api_key()
        if not api_key:
            raise UserError(_(
                "Failed to create an Odoo API key for the FigureFlow connector."
            ))

        payload = {
            "domain": domain,
            "db": self.env.cr.dbname,
            "username": self.env.user.login,
            "api_key": api_key,
        }
        try:
            response = requests.post(
                f"{api_url}/api/integrations/odoo/marketplace/initiate/",
                json=payload,
                timeout=INITIATE_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            _logger.warning("FigureFlow initiate request failed: %s", exc)
            raise UserError(_(
                "Could not reach FigureFlow at %(url)s. Check the FigureFlow "
                "API URL in settings and your network connection.",
                url=api_url,
            )) from exc

        if response.status_code == 401:
            raise UserError(_(
                "FigureFlow rejected the Odoo credentials. The API key was "
                "generated but Odoo rejected the test login — check your user "
                "permissions and try again."
            ))
        if response.status_code >= 400:
            _logger.warning(
                "FigureFlow initiate returned %s: %s",
                response.status_code,
                response.text[:500],
            )
            raise UserError(_(
                "FigureFlow could not start the connection (status %s). Please "
                "try again in a moment.",
                response.status_code,
            ))

        data = response.json()
        claim_code = data.get("claim_code")
        if not claim_code:
            raise UserError(_(
                "FigureFlow did not return a claim code; please retry."
            ))

        self._figureflow_set_param(FIGUREFLOW_CLAIM_CODE_PARAM, claim_code)
        self._figureflow_set_param(FIGUREFLOW_API_KEY_ID_PARAM, str(key_id) if key_id else "")
        self._figureflow_set_param(FIGUREFLOW_CONNECTION_STATUS_PARAM, "awaiting_claim")

        query = urlencode({"claim": claim_code})
        return {
            "type": "ir.actions.act_url",
            "url": f"{web_url}/connect-odoo?{query}",
            "target": "new",
        }

    def action_figureflow_disconnect(self):
        """Revoke the API key on Odoo's side and clear local connector state.

        AIDEV-NOTE: This only revokes the *Odoo* side. The user must also
        disconnect from inside FigureFlow to fully remove the integration —
        the disconnect button on the settings page links to the FF page.
        """
        self.ensure_one()
        key_id_param = self._figureflow_get_param(FIGUREFLOW_API_KEY_ID_PARAM, default="")
        if key_id_param:
            try:
                key_row = self.env["res.users.apikeys"].sudo().browse(int(key_id_param))
                if key_row.exists():
                    key_row.unlink()
            except (ValueError, TypeError):
                _logger.warning("Stored FigureFlow API key id is not an integer: %s", key_id_param)

        self._figureflow_set_param(FIGUREFLOW_CLAIM_CODE_PARAM, "")
        self._figureflow_set_param(FIGUREFLOW_API_KEY_ID_PARAM, "")
        self._figureflow_set_param(FIGUREFLOW_CONNECTION_STATUS_PARAM, "disconnected")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("FigureFlow disconnected"),
                "message": _(
                    "The Odoo API key has been revoked. To fully remove the "
                    "integration, also disconnect from inside FigureFlow."
                ),
                "type": "success",
                "sticky": False,
            },
        }

    def action_figureflow_open_dashboard(self):
        """Open the FigureFlow dashboard in a new tab."""
        self.ensure_one()
        web_url = (self.figureflow_web_url or DEFAULT_WEB_URL).rstrip("/")
        return {
            "type": "ir.actions.act_url",
            "url": web_url,
            "target": "new",
        }

    @api.model
    def figureflow_is_connected(self):
        status = self._figureflow_get_param(FIGUREFLOW_CONNECTION_STATUS_PARAM, default="")
        return status in {"awaiting_claim", "connected"}
