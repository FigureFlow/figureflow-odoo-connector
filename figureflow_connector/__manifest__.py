{
    "name": "FigureFlow",
    "version": "18.0.1.0.0",
    "summary": "Eliminate Financial Blind Spots with FigureFlow — AI-driven "
               "reconciliation, month-end close, KPIs and cash forecasting.",
    "description": """
FigureFlow Connector
====================

Bridges your Odoo instance to FigureFlow, an AI-powered financial management
platform. After installing this module and clicking Connect, your chart of
accounts, journal entries, partners and invoices are securely synced to
FigureFlow where AI agents handle:

- Bank reconciliation and adjustment proposals
- Month-end close workflows
- 40+ financial KPIs and threshold alerts
- Cash-flow forecasting
- Management and annual reports

Data sent to FigureFlow
-----------------------

When you click Connect, this module generates a personal Odoo API key and
shares it with figureflow.app together with your Odoo URL, database name
and login. FigureFlow uses these credentials to read accounting data from
your Odoo. Nothing is sent until you explicitly click Connect, and you can
revoke access at any time by removing the API key from your Odoo user
preferences and disconnecting in FigureFlow.

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
        "security/ir.model.access.csv",
        "data/figureflow_data.xml",
        "views/res_config_settings_views.xml",
        "views/figureflow_menu.xml",
    ],
    "images": ["static/description/images/cover.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
