FigureFlow Connector
====================

This module bridges a customer's Odoo instance to FigureFlow, an AI-powered
financial management platform. Installing it adds a *FigureFlow* app to Odoo
with links into the FigureFlow web app, where the connection is set up.

This is a data-only module: it contains no server-side Python, so it is
installable on Odoo Online as well as Odoo.sh and On-Premise.

Installation
------------

1. Install the module from the Odoo Apps marketplace, or place this
   directory in your addons path and update the app list.
2. Open the **FigureFlow** app.
3. Click **Connect to FigureFlow**.

What happens on Connect
-----------------------

**Connect to FigureFlow** opens the FigureFlow web app
(``web.figureflow.app/connect-odoo``) in a new browser tab. In FigureFlow
the user:

1. Signs in (magic link — no separate password).
2. Connects their Odoo by providing their Odoo URL, database name and an
   Odoo API key.

The API key is created by the user inside Odoo under **My Profile →
Account Security → New API Key**. The key is generated and held by the
user; the module never generates or transmits it.

FigureFlow then reads accounting data from Odoo over Odoo's standard
External API (XML-RPC / JSON-RPC) using that key.

What FigureFlow reads
---------------------

After connection, FigureFlow polls Odoo on an hourly cadence and pulls:

- ``account.account`` — chart of accounts
- ``account.move`` and ``account.move.line`` — journal entries
- ``res.partner`` — partners
- ``account.move`` (invoice subset) — invoices and credit notes
- ``account.journal`` — journal definitions
- ``account.tax`` — tax definitions
- ``res.company`` — company info, currency, country

Disconnecting
-------------

Delete the FigureFlow API key under **My Profile → Account Security** in
Odoo to revoke FigureFlow's access. To fully remove the integration, also
disconnect from inside FigureFlow — the user's accounting data will then
be purged on the FigureFlow side.

Why no server-side code
-----------------------

Odoo Online (SaaS) only accepts third-party modules whose sole Python
files are ``__init__.py`` and ``__manifest__.py``. Keeping this module
data-only is what makes it compatible with Odoo Online. The connect
handshake and all data sync therefore live in the FigureFlow web app and
backend, not in the Odoo module.

Pricing
-------

This connector is free. FigureFlow's AI features are billed separately
through your FigureFlow subscription.

Supported Odoo versions
-----------------------

Parallel branches exist for Odoo 14.0, 15.0, 16.0, 17.0, 18.0 and 19.0.

Support
-------

support@figureflow.app
