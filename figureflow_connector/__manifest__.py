{
    "name": "FigureFlow AI Accounting",
    "version": "18.0.3.0.0",
    "summary": "Eliminate Financial Blind Spots with FigureFlow — AI-driven "
               "reconciliation, month-end close, KPIs and cash forecasting.",
    "description": """
FigureFlow Connector
====================

Bridges your Odoo instance to FigureFlow, an AI-powered financial management
platform. Once connected, your chart of accounts, journal entries, partners
and invoices are securely synced to FigureFlow where AI agents handle:

- Bank reconciliation and adjustment proposals
- Month-end close workflows
- 40+ financial KPIs and threshold alerts
- Cash-flow forecasting
- Management and annual reports

Connecting to FigureFlow
------------------------

Open the FigureFlow app in Odoo and click **Connect to FigureFlow**. This
opens the FigureFlow web app in a new tab, where you connect your Odoo by
providing an Odoo API key together with your Odoo URL and database name.
You create the API key yourself under **My Profile > Account Security > New
API Key** in Odoo, so the key is generated and held by you and never passes
through your browser to anyone else.

Data sent to FigureFlow
-----------------------

FigureFlow uses the API key you provide to read your chart of accounts,
journal entries, partners and invoices over Odoo's standard External API.
Nothing is read from Odoo until you connect inside FigureFlow, and you can
revoke access at any time by deleting the API key in your Odoo profile and
disconnecting in FigureFlow.

Working inside Odoo
-------------------

Once connected, a FigureFlow button in the systray opens a Copilot panel
docked on the right of Odoo. It is record-aware: open a journal entry,
invoice or partner and ask FigureFlow to explain it, reconcile it, reclassify
it or draft a report — without leaving Odoo. The panel is the FigureFlow chat
embedded as a secure iframe; you sign in to FigureFlow from inside it.

This module contains no server-side code: it adds the FigureFlow app entry,
links out to the FigureFlow web app, and embeds the Copilot panel using
client-side web assets only. It is therefore compatible with Odoo Online,
Odoo.sh and On-Premise.

Pricing
-------

This connector is free. FigureFlow's AI features are billed separately
through your FigureFlow subscription.
""",
    "author": "FigureFlow",
    "website": "https://www.figureflow.app",
    "support": "support@figureflow.app",
    "license": "LGPL-3",
    "category": "Accounting/Accounting",
    "depends": ["base", "account"],
    "data": [
        "views/figureflow_actions.xml",
        "views/figureflow_menu.xml",
    ],
    # AIDEV-NOTE: Web-asset JS only (OWL) — no server-side Python — so the
    # in-Odoo Copilot panel stays compatible with Odoo Online. It embeds the
    # FigureFlow panel (web.figureflow.app/embed/panel) as a record-aware
    # iframe; auth + chat run inside that iframe.
    "assets": {
        "web.assets_backend": [
            "figureflow_connector/static/src/panel/panel_systray.scss",
            "figureflow_connector/static/src/panel/panel_systray.xml",
            "figureflow_connector/static/src/panel/panel_systray.js",
        ],
    },
    "images": ["static/description/images/brand-cover.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
