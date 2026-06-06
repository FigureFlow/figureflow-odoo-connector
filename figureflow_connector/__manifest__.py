{
    "name": "FigureFlow AI Accounting",
    "version": "17.0.2.0.0",
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

This module contains no server-side code: it adds the FigureFlow app entry
and links out to the FigureFlow web app. It is therefore compatible with
Odoo Online, Odoo.sh and On-Premise.

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
    "images": ["static/description/images/brand-cover.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
