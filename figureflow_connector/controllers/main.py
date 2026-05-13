"""Controllers for the FigureFlow connector.

Reserved for an optional callback from FigureFlow after a successful claim.
The v1 marketplace flow doesn't require an inbound webhook — FigureFlow
polls Odoo for data and the user sees connection state in their FigureFlow
dashboard — but having a callback route reserved keeps the URL stable for
future use (e.g. real-time webhooks).
"""

from odoo import http


class FigureFlowController(http.Controller):

    @http.route(
        "/figureflow/connector/health",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def health(self, **_kwargs):
        return "ok"
