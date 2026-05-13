FigureFlow Connector
====================

This module bridges a customer's Odoo instance to FigureFlow, an AI-powered
financial management platform. Installing it adds a *FigureFlow* section to
Odoo's Settings page with a one-click Connect button.

Installation
------------

1. Install the module from the Odoo Apps marketplace, or place this
   directory in your addons path and update the app list.
2. Open ``Settings`` and find the **FigureFlow** section.
3. Click **Connect to FigureFlow**.

What happens on Connect
-----------------------

The Connect action:

1. Generates a personal Odoo API key for the current user, scoped to the
   FigureFlow connector.
2. POSTs ``{domain, db, username, api_key}`` to FigureFlow's marketplace
   handshake endpoint (``/api/integrations/odoo/marketplace/initiate/``).
3. Receives a single-use ``claim_code`` (TTL: 15 minutes).
4. Opens the user's browser to ``figureflow.app/connect-odoo?claim=...``.
5. The user signs up or logs in on FigureFlow, which completes the
   handshake and triggers the initial data sync.

Credentials never travel through the browser; the ``claim_code`` is the
only thing the browser sees and it is single-use with a short TTL.

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

Click **Disconnect** in the FigureFlow settings page. This revokes the
Odoo API key on this Odoo. To fully remove the integration, also
disconnect from inside FigureFlow — the user's accounting data will then
be purged on the FigureFlow side.

Pricing
-------

This connector is free. FigureFlow's AI features are billed separately
through your FigureFlow subscription.

Supported Odoo versions
-----------------------

This branch targets Odoo 18.0. Parallel branches exist for 17.0 and 19.0.

Support
-------

support@figureflow.app
