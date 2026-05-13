# FigureFlow Odoo Connector

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

Bridges a customer's Odoo instance to [FigureFlow](https://www.figureflow.com),
an AI-powered financial management platform.

## Branch layout

| Branch | Odoo version | Status |
|---|---|---|
| `18.0` (default) | Odoo 18.0 | Reference implementation |
| `17.0` | Odoo 17.0 | TODO — port |
| `19.0` | Odoo 19.0 | TODO — port |

Each branch is a self-contained Odoo module compatible with its named Odoo
release. Differences between branches are intentionally small (manifest
version, view XML attrs syntax) so changes can be cherry-picked across.

## Install (development)

```bash
git clone https://github.com/figureflow/figureflow-odoo-connector.git
ln -s "$(pwd)/figureflow-odoo-connector/figureflow_connector" /path/to/odoo/addons/
# In Odoo: Apps → Update Apps List → search "FigureFlow" → Install.
```

## What this module does

Installs a *FigureFlow* section in Odoo's Settings page with three actions:

- **Connect to FigureFlow** — generates a personal Odoo API key, POSTs the
  Odoo URL + db + login + key to FigureFlow's marketplace handshake endpoint
  over HTTPS, opens the user's browser to FigureFlow with a single-use
  claim code.
- **Open FigureFlow Dashboard** — deep-links to the FigureFlow app.
- **Disconnect** — revokes the Odoo API key locally and clears connector
  state. Users are told to also disconnect from inside FigureFlow to fully
  remove the integration.

The connector does no other side effects — the marketplace handshake is
all it does. FigureFlow handles data ingestion server-to-server using the
Odoo API key the connector hands off.

## Architecture

```
┌────────────────────────────┐                 ┌─────────────────────────────┐
│  Customer's Odoo           │                 │  FigureFlow                 │
│                            │  POST /initiate │                             │
│  Settings → FigureFlow     │ ──────────────▶ │  /api/integrations/odoo/    │
│  [Connect]                 │  {domain, db,   │  marketplace/initiate/      │
│    │                       │   username,     │                             │
│    │  generates API key    │   api_key}      │  validates against Odoo,    │
│    │                       │ ◀────────────── │  stores in pending row,     │
│    │                       │   {claim_code}  │  returns claim_code         │
│    │                       │                 │                             │
│    └─▶ opens browser ───── │ ──────────────▶ │  /connect-odoo?claim=…      │
│                            │                 │  signup/login,              │
│                            │  pulls Odoo     │  POST /marketplace/claim/   │
│                            │  data hourly    │  creates OdooToken,         │
│                            │ ◀────────────── │  triggers initial sync      │
└────────────────────────────┘                 └─────────────────────────────┘
```

## Submission to Odoo Apps

1. Push to a Git repo and register it at https://apps.odoo.com/apps/upload
2. `static/description/icon.png` is the FigureFlow brand mark (180×180).
   Replace `static/description/images/main_screenshot.png` (currently the
   FigureFlow wordmark, 430×162) with a real 1200×675 product screenshot
   showing the Connect flow or FigureFlow dashboard before submission.
3. Submit each version branch separately.

## License

LGPL-3.0 — see [LICENSE](LICENSE).
