// Shared front-desk terminal: when a staff member deliberately clicks
// "Log out", always land back on a clean /login (no redirect-to). Frappe's
// core desk.js logout() reuses redirect_to_login(), which appends the
// current path as redirect-to -- useful when a *session expires* mid-work,
// but wrong here: it sends the next person who logs in back to whatever
// page the previous person was on. Session-expiry redirects are untouched;
// only the explicit logout button is overridden.
//
// v3: v1 crashed on load with "frappe.ready is not a function" (confirmed
// via browser console) because this script can execute before the core
// frappe bundle has finished defining frappe.ready/frappe.provide/etc. This
// version never calls ANY frappe.* API until frappe.app is confirmed to
// exist (which only happens after core has fully booted), so it cannot
// crash on load order regardless of script ordering/timing.
(function () {
    function apply_override() {
        if (!window.frappe || !frappe.app) {
            return false;
        }
        if (frappe.app.__gym_logout_patched) {
            return true;
        }
        frappe.app.logout = function () {
            frappe.app.logged_out = true;
            frappe.confirm(__('Are you sure you want to log out?'), function () {
                return frappe.call({
                    method: 'logout',
                    callback: function (r) {
                        if (r.exc) {
                            return;
                        }
                        window.location.href = '/login';
                    },
                });
            });
        };
        frappe.app.__gym_logout_patched = true;
        if (window.console && console.log) {
            console.log('[gym_logout_override] applied');
        }
        return true;
    }

    if (apply_override()) {
        return;
    }

    var attempts = 0;
    var interval = setInterval(function () {
        attempts++;
        if (apply_override() || attempts > 50) {
            clearInterval(interval);
            if (attempts > 50 && window.console && console.warn) {
                console.warn('[gym_logout_override] gave up waiting for frappe.app');
            }
        }
    }, 200);
})();
