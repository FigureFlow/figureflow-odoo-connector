/** @odoo-module **/

/*
 * FigureFlow Copilot panel — mounts the FigureFlow chat INSIDE Odoo as a
 * right-side drawer, record-aware. This is pure web-asset JS (OWL) with no
 * server-side Python, so the module stays installable on Odoo Online.
 *
 * - A systray button toggles a drawer that hosts the FigureFlow panel as an
 *   iframe (web.figureflow.app/embed/panel).
 * - The drawer reports the ACTIVE Odoo record (model + id) to the panel over
 *   postMessage using the documented embed contract, so "explain this entry" /
 *   "reclassify this" act on whatever the user is looking at.
 * - Auth is handled entirely by the panel itself (its "Sign in" opens the
 *   figureflow.app /embed/auth popup and injects the token). The widget never
 *   touches credentials.
 *
 * Dev: set localStorage 'ff_panel_url' to e.g. http://localhost:3000/embed/panel
 * to point the drawer at a local FigureFlow stack, then reload Odoo.
 */
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { session } from "@web/session";

const PANEL_URL =
    browser.localStorage.getItem("ff_panel_url") ||
    "https://web.figureflow.app/embed/panel";
const PANEL_ORIGIN = new URL(PANEL_URL).origin;

export class FigureFlowPanel extends Component {
    static template = "figureflow_connector.Panel";
    static props = {};

    setup() {
        this.action = useService("action");
        this.iframeRef = useRef("iframe");
        // loaded: the iframe is mounted once on first open and then kept warm
        // (the chat persists across toggles). open: drawer visibility.
        this.state = useState({ open: false, loaded: false });
        this.panelUrl = PANEL_URL;

        this._ready = false; // panel posted FF_EMBED_READY
        this._lastKey = null; // last record we posted (dedupe)
        this._onMessage = this._onMessage.bind(this);

        onMounted(() => {
            browser.addEventListener("message", this._onMessage);
            // The active Odoo record isn't reactive to us; poll while open and
            // post only when it actually changes. Cheap in-memory read.
            this._poll = browser.setInterval(() => this._syncRecord(), 1200);
        });
        onWillUnmount(() => {
            browser.removeEventListener("message", this._onMessage);
            browser.clearInterval(this._poll);
        });
    }

    toggle() {
        this.state.open = !this.state.open;
        if (this.state.open) {
            this.state.loaded = true; // mount the iframe on first open
            this._lastKey = null; // force a re-post of the current record
        }
    }

    /** The record currently open in Odoo, or null (list/dashboard/no record). */
    _currentRecord() {
        const controller = this.action.currentController;
        const props = controller && controller.props;
        const model = props && props.resModel;
        const resId = props && props.resId;
        if (!model || !resId) {
            return null;
        }
        return {
            source: "odoo",
            model,
            id: String(resId),
            instanceHint: {
                host: browser.location.host,
                db: session.db || "",
            },
        };
    }

    _syncRecord() {
        if (!this.state.open || !this._ready) {
            return;
        }
        const record = this._currentRecord();
        const key = record ? `${record.model}:${record.id}` : "none";
        if (key === this._lastKey) {
            return;
        }
        this._lastKey = key;
        this._post({ type: "FF_RECORD", record });
    }

    _post(message) {
        const iframe = this.iframeRef.el;
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage(message, PANEL_ORIGIN);
        }
    }

    _onMessage(ev) {
        if (ev.origin !== PANEL_ORIGIN) {
            return;
        }
        const data = ev.data || {};
        if (data.type === "FF_EMBED_READY") {
            this._ready = true;
            this._lastKey = null;
            this._syncRecord();
        }
    }
}

registry.category("systray").add(
    "figureflow_connector.panel",
    { Component: FigureFlowPanel },
    { sequence: 1 }
);
