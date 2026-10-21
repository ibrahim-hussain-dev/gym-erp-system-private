// Kiosk-mode navigation lock for the client-facing "Gym Front Desk" and
// "Gym Owner" logins -- v2, built from real browser-console evidence (v1
// compared against the wrong route shape entirely and blocked everything).
//
// CONFIRMED real Frappe route shapes for this site (via live console +
// direct DB lookup, not guessed):
//   Workspace home page:  ["Workspaces", "<Workspace Title>"]
//   DocType list view:    ["List", "<DocType Name>", "<ViewType>"]
//   DocType form view:    ["Form", "<DocType Name>", "<docname>"]
//   Print view:           ["print", "<DocType Name>", "<docname>"]
//   Query report:         ["query-report", "<Report Name>"]
//   Custom Page:          ["<page-name>"]  (single segment, e.g. "record-expense")
//
// SAFETY: this never applies to any account that has the "System Manager"
// role (that includes the developer/admin login even though it also
// happens to carry the "Gym Owner" role for historical reasons). If this
// script ever misbehaves, log in with a System Manager account -- it is
// always completely unaffected -- to fix or remove it.
(function () {
    function log() {
        if (window.console && console.log) {
            var args = ["[route-guard]"];
            for (var i = 0; i < arguments.length; i++) {
                args.push(arguments[i]);
            }
            console.log.apply(console, args);
        }
    }

    var ROLE_CONFIG = {
        "Gym Front Desk": {
            home_route: "front-desk", // slug used to *navigate back* -- confirmed working via the site's own links
            home_workspace: "front desk", // lowercased title Frappe reports back via get_route() once there
            doctypes: [
                "gym member",
                "gym attendance",
                "gym subscription",
                "gym trainer",
                "sales invoice",
                "gym fitness log",
                "gym plan",
            ],
            pages: ["record-expense", "mark-attendance", "sell-membership"],
            reports: [],
        },
        "Gym Owner": {
            home_route: "impact-health-studio",
            home_workspace: "impact health studio",
            doctypes: [
                "gym member",
                "gym attendance",
                "gym subscription",
                "gym plan",
                "gym trainer",
                "gym timing slot",
                "payment entry",
                "sales invoice",
                "gym expense",
            ],
            pages: ["record-expense", "mark-attendance", "sell-membership"],
            reports: [
                "gym trainer commission",
                "gym revenue by plan",
                "gym monthly revenue",
                "gym member retention",
            ],
        },
    };

    function is_allowed(route_arr, cfg) {
        if (!route_arr || route_arr.length === 0) {
            return false;
        }
        var seg0 = String(route_arr[0] || "").toLowerCase();

        if (seg0 === "workspaces") {
            var ws_title = String(route_arr[1] || "").toLowerCase();
            return ws_title === cfg.home_workspace;
        }

        if (seg0 === "list" || seg0 === "form" || seg0 === "print") {
            var doctype = String(route_arr[1] || "").toLowerCase();
            for (var i = 0; i < cfg.doctypes.length; i++) {
                if (cfg.doctypes[i] === doctype) {
                    return true;
                }
            }
            return false;
        }

        if (seg0 === "query-report") {
            var report = String(route_arr[1] || "").toLowerCase();
            for (var j = 0; j < cfg.reports.length; j++) {
                if (cfg.reports[j] === report) {
                    return true;
                }
            }
            return false;
        }

        // Single-segment custom Page route (record-expense, mark-attendance, ...)
        if (route_arr.length === 1) {
            for (var k = 0; k < cfg.pages.length; k++) {
                if (cfg.pages[k] === seg0) {
                    return true;
                }
            }
            return false;
        }

        // Unrecognised route shape: deny by default rather than guess.
        return false;
    }

    function get_route_safely() {
        // Confirmed via live console: frappe.get_route() can throw
        // "Cannot read properties of null (reading 'join')" for a brief
        // moment right after a hard page load / typed URL, before Frappe
        // has finished parsing the route internally. Treat that as "not
        // known yet" and skip enforcement for this call rather than
        // treating the error as "disallowed" and force-redirecting --
        // the very next router 'change' event will re-check once the
        // route has actually resolved.
        try {
            return { ok: true, route: frappe.get_route() };
        } catch (e) {
            return { ok: false, error: e };
        }
    }

    function init() {
        if (!window.frappe || !frappe.boot || !frappe.boot.user || !frappe.router) {
            return false;
        }

        var roles = frappe.boot.user.roles || [];

        if (roles.indexOf("System Manager") !== -1 || frappe.session.user === "Administrator") {
            log("System Manager/Administrator detected -- no restriction applied.");
            return true;
        }

        var matched_role = null;
        for (var role in ROLE_CONFIG) {
            if (roles.indexOf(role) !== -1) {
                matched_role = role;
                break;
            }
        }

        if (!matched_role) {
            log("No matching restricted role for this user -- no restriction applied.");
            return true;
        }

        var cfg = ROLE_CONFIG[matched_role];
        log("Restriction active for role:", matched_role, "home_route:", cfg.home_route);

        function enforce() {
            var result = get_route_safely();
            if (!result.ok) {
                log("get_route() threw (route not resolved yet), skipping this check:", result.error && result.error.message);
                return;
            }
            var route_arr = result.route;
            if (!is_allowed(route_arr, cfg)) {
                log("BLOCKED route:", JSON.stringify(route_arr), "-> redirecting to", cfg.home_route);
                frappe.show_alert({ message: __("Access restricted"), indicator: "red" }, 3);
                frappe.set_route(cfg.home_route);
            }
        }

        frappe.router.on("change", enforce);
        // Also run once immediately, in case the initial route (from a
        // typed URL or a hard refresh) was already resolved before this
        // script finished loading.
        enforce();

        return true;
    }

    if (init()) {
        return;
    }

    var attempts = 0;
    var interval = setInterval(function () {
        attempts++;
        if (init() || attempts > 50) {
            clearInterval(interval);
        }
    }, 200);
})();
