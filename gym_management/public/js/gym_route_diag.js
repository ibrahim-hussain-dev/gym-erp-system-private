// DIAGNOSTIC ONLY -- logs every route change to the browser console so we can
// see the *real* sequence of events Frappe's router fires for a single
// navigation (list click, form open, back button, etc.) before writing any
// enforcement logic again. This script makes zero decisions and never calls
// frappe.set_route() or anything else that could affect navigation -- it is
// purely a console.log tap, so it cannot break anything no matter what
// sequence of events actually happens.
(function () {
    function log() {
        if (window.console && console.log) {
            var args = ["[route-diag]", new Date().toISOString().slice(11, 23)];
            for (var i = 0; i < arguments.length; i++) {
                args.push(arguments[i]);
            }
            console.log.apply(console, args);
        }
    }

    function snapshot(label) {
        var route_str = "(get_route_str unavailable)";
        var route_arr = "(get_route unavailable)";
        try {
            if (frappe.get_route_str) {
                route_str = frappe.get_route_str();
            }
        } catch (e) {
            route_str = "ERROR: " + e.message;
        }
        try {
            if (frappe.get_route) {
                route_arr = JSON.stringify(frappe.get_route());
            }
        } catch (e) {
            route_arr = "ERROR: " + e.message;
        }
        log(label, "route_str=", route_str, "route_arr=", route_arr, "window.location.pathname=", window.location.pathname);
    }

    function init() {
        if (!window.frappe || !frappe.router) {
            return false;
        }

        snapshot("INIT (script loaded, before attaching listener)");

        frappe.router.on("change", function () {
            snapshot("CHANGE EVENT");
        });

        log("listener attached to frappe.router 'change' event. Click around now.");
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
